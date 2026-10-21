# flashcard-maker

講義資料・教科書の抜粋・過去問などの教材から、暗記用フラッシュカードを作る Claude 用スキルです。
大学編入試験（数学・英語・物理など）の対策用に作りました。

## できること

- 教材を渡すと、1枚1論点のフラッシュカードを作ります
- 裏面は「簡潔な答え＋1行の補足」
- 教材に書かれていない内容は作りません
- 難易度タグ（基本／応用）付き
- 出力形式：Anki用CSV、Markdown表（印刷・NotebookLM向け）、Quizlet用TSV

## ファイル構成

```
flashcard-maker/
├── SKILL.md            … スキル本体（Claude が読む指示書）
├── templates/          … 出力形式の見本
├── examples/           … 動作確認用の教材サンプルと生成結果
├── CHANGELOG.md        … バージョンごとの変更点と理由
└── README.md           … このファイル
```

## 使い方

1. このフォルダを Claude のスキルフォルダ（例：`~/.claude/skills/flashcard-maker/`）に置きます。
   claude.ai で使う場合は、フォルダを zip にして「設定 → 機能 → スキル」からアップロードします。
2. Claude に教材を渡して「この資料からフラッシュカードを作って。Anki用CSVで」のように頼みます。

## 改善の履歴

[CHANGELOG.md](CHANGELOG.md) を参照してください。
