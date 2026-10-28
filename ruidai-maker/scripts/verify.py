"""類題の答えを SymPy で計算し、想定した答えと一致するか確かめるスクリプト。

使い方:
    python verify.py problems.json

problems.json の書き方は SKILL.md を参照。
OK の問題は、問題文と答えを Markdown（数式は $…$）で表示する。出力にはこれをそのまま使う。
"""

import json
import sys

from sympy import (S, Symbol, diff, factor, integrate, latex, limit, simplify,
                   solve, solveset, sympify, together)


def parse(text, x, var):
    return sympify(text, locals={var: x})


def tex(expr):
    """読みやすい LaTeX にする（\\sin{\\left(x \\right)} ではなく \\sin{x}）。"""
    return latex(expr, fold_func_brackets=True)


def short_tex(expr):
    """同じ値の書き方のうち、いちばん短い LaTeX を選ぶ（例：1/4 + e^2/4 → (e^2 + 1)/4）。"""
    forms = [simplify(expr), together(expr), factor(expr)]
    return min((tex(f) for f in forms), key=len)


def extrema(expr, x):
    """増減表と同じ方法で、f'(x) = 0 の点の前後で f'(x) の符号が変わるかを調べる。"""
    d1 = diff(expr, x)
    points = sorted(solveset(d1, x, domain=S.Reals))
    # 隣り合う点の間と、両端の外側で f'(x) の符号を調べる
    tests = [points[0] - 1] + [(a + b) / 2 for a, b in zip(points, points[1:])] + [points[-1] + 1] if points else []
    signs = [d1.subs(x, t) > 0 for t in tests]
    result = {"max": [], "min": [], "none": []}
    for i, c in enumerate(points):
        point = [c, simplify(expr.subs(x, c))]
        left, right = signs[i], signs[i + 1]
        if left and not right:
            result["max"].append(point)
        elif not left and right:
            result["min"].append(point)
        else:  # 符号が変わらない点は極値ではない
            result["none"].append(point)
    return result


def compute(p, x):
    """問題1つ分の答えを SymPy で計算して返す。"""
    expr = parse(p["expr"], x, p["var"])
    kind = p["type"]
    if kind == "limit":
        return limit(expr, x, sympify(p["at"]))
    if kind == "integral":
        return integrate(expr, (x, sympify(p["lower"]), sympify(p["upper"])))
    if kind == "derivative":
        return diff(expr, x)
    if kind == "solve":
        return solve(expr, x)
    if kind == "extrema":
        return extrema(expr, x)
    raise ValueError(f"未対応の type です: {kind}")


def same(a, b):
    return simplify(a - b) == 0


def same_points(got, expected):
    """[[x, 値], ...] の組が、順番に関係なく一致するか。"""
    return len(got) == len(expected) and all(
        any(same(g[0], e[0]) and same(g[1], e[1]) for e in expected) for g in got
    )


def matches(p, got, x):
    """計算結果と想定した答えが数学的に等しいか判定する。"""
    kind, answer, var = p["type"], p["answer"], p["var"]
    if kind == "solve":
        expected = [parse(a, x, var) for a in answer]
        return len(got) == len(expected) and all(
            any(same(g, e) for e in expected) for g in got
        )
    if kind == "extrema":
        return all(
            same_points(got[k], [[parse(a, x, var), parse(b, x, var)] for a, b in answer.get(k, [])])
            for k in ("max", "min")
        )
    return same(got, parse(answer, x, var))


def problem_text(p, x):
    """型に合わせた問題文を作る。"""
    e = tex(parse(p["expr"], x, p["var"]))
    v = tex(x)
    kind = p["type"]
    if kind == "limit":
        return rf"$\displaystyle\lim_{{{v} \to {tex(sympify(p['at']))}}} {e}$ を求めよ。"
    if kind == "integral":
        return rf"$\displaystyle\int_{{{tex(sympify(p['lower']))}}}^{{{tex(sympify(p['upper']))}}} {e} \, d{v}$ を求めよ。"
    if kind == "derivative":
        return rf"$f({v}) = {e}$ の導関数を求めよ。"
    if kind == "solve":
        return rf"方程式 ${e} = 0$ を解け。"
    return rf"$f({v}) = {e}$ の極値を求めよ。"


def answer_text(kind, got, x):
    """答えを作る。日本語は数式（$…$）の外に出す。"""
    v = tex(x)
    if kind == "derivative":
        return rf"$f'({v}) = {short_tex(got)}$"
    if kind == "solve":
        return rf"${v} = " + r",\ ".join(short_tex(g) for g in got) + "$"
    if kind == "extrema":
        parts = [rf"${v} = {tex(c)}$ で極大値 ${short_tex(val)}$" for c, val in got["max"]]
        parts += [rf"${v} = {tex(c)}$ で極小値 ${short_tex(val)}$" for c, val in got["min"]]
        text = "、".join(parts) if parts else "極値なし"
        if got["none"]:
            text += "（" + "、".join(rf"${v} = {tex(c)}$" for c, _ in got["none"]) + " は極値ではない）"
        return text
    return f"${short_tex(got)}$"


def main():
    if len(sys.argv) != 2:
        print("使い方: python verify.py problems.json")
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        problems = json.load(f)

    ng = 0
    for p in problems:
        x = Symbol(p["var"])
        try:
            got = compute(p, x)
            ok = matches(p, got, x)
        except Exception as e:  # 式の書き間違いなど
            print(f"[ERROR] {p.get('id')}: {e}")
            ng += 1
            continue
        if ok:
            print(f"[OK] {p['id']}")
            print(f"  問題: {problem_text(p, x)}")
            print(f"  答え: {answer_text(p['type'], got, x)}")
        else:
            print(f"[NG] {p['id']}: 計算結果 {got} / 想定 {p['answer']}")
            ng += 1

    print(f"--- {len(problems)} 問中 OK {len(problems) - ng} 問、NG {ng} 問")
    sys.exit(1 if ng else 0)


if __name__ == "__main__":
    main()
