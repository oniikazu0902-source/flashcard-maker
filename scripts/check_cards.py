"""フラッシュカードの出力（Anki用CSV・Markdown表・Quizlet用TSV）を検査するスクリプト。

使い方:
    python check_cards.py cards.csv     # Anki用CSV
    python check_cards.py cards.md      # Markdown表
    python check_cards.py cards.tsv     # Quizlet用TSV

調べること:
    - 表面や補足に、ほかのカードの答えが書かれていないか（答えの漏れ）
    - 「補足：」だけの空の補足、「教材に明記されている」のような中身のない補足がないか
    - 形式ごとの決まり（見出し行、列の数、出典、タグ、エスケープ）を守っているか
問題がなければ終了コード 0、あれば 1。
"""

import csv
import html
import io
import re
import sys

ANKI_HEADER = ["#separator:comma", "#html:true", "#columns:表面,裏面,タグ", "#tags column:3"]
LEVELS = ("基本", "応用")
# 答えの漏れを調べる最短の長さ。「1」「-1」のような短い答えは、無関係な場所でも一致してしまうので比べない
MIN_ANSWER_LEN = 4
# 中身のない補足によく出る言い回し
FILLER = ("明記", "教材に書かれ", "講義ノートに", "教材のとおり", "教材に記載")


class Card:
    def __init__(self, line, front, answer, note, source, level):
        self.line, self.front, self.answer = line, front, answer
        self.note, self.source, self.level = note, source, level
        self.problems = []


def normalize(text):
    """比べやすいように、HTML・数式の記号・空白・句読点を取り除く。"""
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    for old, new in ((r"\lvert", "|"), (r"\rvert", "|"), (r"\lt", "<"), (r"\gt", ">"),
                     (r"\le", "≤"), (r"\ge", "≥"), (r"\dfrac", r"\frac")):
        text = text.replace(old, new)
    text = re.sub(r"\\\(|\\\)|\$", "", text)
    return re.sub(r"[\s。、．，.,]", "", text)


# ---------- 形式ごとの読み込み ----------

def split_back(back, sep):
    """裏面を「答え」「補足」「出典」に分ける。補足がなければ None。"""
    parts = [p.strip() for p in back.split(sep)]
    answer = parts[0]
    note = source = None
    for p in parts[1:]:
        p = re.sub(r"</?small>", "", p).strip()
        if p.startswith("補足："):
            note = p[len("補足："):].strip()
        elif p.startswith("出典："):
            source = p[len("出典："):].strip()
    return answer, note, source


def read_anki(text, errors):
    lines = text.splitlines()
    if lines[:4] != ANKI_HEADER:
        errors.append("1〜4行目が Anki 用の見出し（#separator:comma など）になっていない")
    cards = []
    quoted = re.compile(r'^"(?:[^"]|"")*","(?:[^"]|"")*","(?:[^"]|"")*"$')
    for no, raw in enumerate(lines, 1):
        if not raw.strip() or raw.startswith("#"):
            continue
        row = next(csv.reader(io.StringIO(raw)))
        if len(row) != 3:
            errors.append(f"{no}行目：列が {len(row)} 個（表面・裏面・タグの3個のはず）")
            continue
        front, back, tags = row
        answer, note, source = split_back(back, "<br>")
        tag = tags.split()
        card = Card(no, front, answer, note, source, tag[1] if len(tag) == 2 else None)
        if not quoted.match(raw):
            card.problems.append("すべての欄を \" で囲んでいない")
        # <br> <small> </small> 以外の < は、HTML の命令として読まれて表示が消える
        rest = re.sub(r"<br>|</?small>", "", front + back)
        if "<" in rest or ">" in rest:
            card.problems.append("< や > がそのまま書かれている（\\lt や &lt; にする）")
        if len(tag) != 2 or tag[1] not in LEVELS:
            card.problems.append(f"タグが「科目 基本／応用」の形でない：{tags}")
        cards.append(card)
    return cards


def split_md_row(line):
    """Markdown 表の1行を欄に分ける（\\| は区切りとみなさない）。"""
    cells = re.split(r"(?<!\\)\|", line.strip())
    return [c.strip() for c in cells[1:-1]]


def read_markdown(text, errors):
    rows = [(no, l) for no, l in enumerate(text.splitlines(), 1) if l.strip().startswith("|")]
    cards = []
    for no, line in rows[2:]:  # 見出し行と区切り行を飛ばす
        cells = split_md_row(line)
        if len(cells) != 6:
            errors.append(f"{no}行目：欄が {len(cells)} 個（6個のはず。| は \\| と書く）")
            continue
        _, front, answer, note, level, source = cells
        card = Card(no, front, answer, note or None, source or None, level)
        if level not in LEVELS:
            card.problems.append(f"難易度が「基本／応用」でない：{level}")
        cards.append(card)
    return cards


def read_quizlet(text, errors):
    cards = []
    for no, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) != 2:
            errors.append(f"{no}行目：タブが {len(cols) - 1} 個（1個のはず）")
            continue
        front, back = cols
        m = re.match(r"【(基本|応用)】", front)
        answer, note, source = split_back(back, "／")
        card = Card(no, front, answer, note, source, m.group(1) if m else None)
        if not m:
            card.problems.append("表面の先頭に【基本】【応用】がない")
        if re.search(r"[\\$^_]", line):
            card.problems.append("\\ $ ^ _ が残っている（Quizlet では特殊文字で書く）")
        cards.append(card)
    return cards


# ---------- 内容の検査 ----------

def check_contents(cards):
    for card in cards:
        if not card.source:
            card.problems.append("出典がない")
        if card.note is not None and not card.note:
            card.problems.append("「補足：」だけの空の補足がある（補足がなければ行ごと省く）")
        if card.note and any(w in card.note for w in FILLER):
            card.problems.append(f"中身のない補足：{card.note}")
    # 答えの漏れ：あるカードの表面・補足に、ほかのカードの答えが書かれていないか
    answers = [(c, normalize(c.answer)) for c in cards]
    for card in cards:
        seen = normalize(card.front + (card.note or ""))
        for other, ans in answers:
            if other is card or len(ans) < MIN_ANSWER_LEN or ans == normalize(card.answer):
                continue
            if ans in seen:
                card.problems.append(f"表面か補足に、{other.line}行目のカードの答え「{other.answer}」が書かれている")


READERS = {".csv": read_anki, ".md": read_markdown, ".tsv": read_quizlet}


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(tuple(READERS)):
        print("使い方: python check_cards.py cards.csv（または .md、.tsv）")
        sys.exit(2)
    path = sys.argv[1]
    with open(path, encoding="utf-8-sig") as f:  # BOM 付きでも読めるようにする
        text = f.read()
    errors = []
    cards = READERS[path[path.rfind("."):]](text, errors)
    check_contents(cards)

    for e in errors:
        print(f"[NG] {e}")
    ng = len(errors)
    for card in cards:
        if card.problems:
            ng += 1
            print(f"[NG] {card.line}行目：{card.front}")
            for p in card.problems:
                print(f"  - {p}")
    print(f"--- カード {len(cards)} 枚、問題 {ng} 件")
    sys.exit(1 if ng else 0)


if __name__ == "__main__":
    main()
