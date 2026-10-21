# 動作確認用の教材サンプル

このファイルは flashcard-maker の動作確認用に作成した架空の講義ノートです（実在の教科書からの引用ではありません）。
数学・英語・物理の3科目を、大学編入試験レベルで短くまとめています。

---

## 数学：微分法の基礎（第3回 講義ノート）

### 3.1 平均値の定理
関数 f(x) が閉区間 [a, b] で連続、開区間 (a, b) で微分可能ならば、
f'(c) = (f(b) - f(a)) / (b - a) を満たす c が a < c < b の範囲に少なくとも1つ存在する。
これを平均値の定理という。特に f(a) = f(b) の場合をロルの定理という。

### 3.2 絶対値関数の微分可能性
f(x) = |x| は x = 0 で連続だが微分可能ではない。
右側微分係数は 1、左側微分係数は -1 であり、両者が一致しないためである。

### 3.3 マクローリン展開
e^x = 1 + x + x^2/2! + x^3/3! + … （すべての実数 x で成り立つ）
sin x = x - x^3/3! + x^5/5! - …
log(1 + x) のマクローリン展開については次回扱う。

### 例題（過去問より）
lim_{x→0} (sin x) / x の値を求めよ。
解答：1。sin x のマクローリン展開から (sin x)/x = 1 - x^2/3! + … となり、x → 0 で 1 に近づく。

---

## 英語：重要語法と構文（第5回）

### 5.1 語彙
- **deteriorate**（動）悪化する。例："The patient's condition deteriorated rapidly."
- **substantial**（形）かなりの、相当な。例：a substantial amount of money
- **comprehensive**（形）包括的な。※ comprehensible（理解できる）と混同しないこと。

### 5.2 構文
- **not A but B**：「AではなくB」。例：He is not a teacher but a student.
- **It is not until A that B**：「AになってはじめてBする」。
  例：It was not until he lost his health that he realized its value.

### 5.3 和文英訳のポイント
「〜するやいなや」は no sooner A than B、hardly A when B などで表せる。
no sooner を文頭に置く場合は倒置が起こる（No sooner had I arrived than it began to rain.）。

---

## 物理：力学（第2回 講義資料）

### 2.1 運動量保存則
物体系に外力が働かない（または外力の和が 0 の）とき、系の運動量の総和は保存される。
m1 v1 + m2 v2 = m1 v1' + m2 v2'

### 2.2 反発係数
2物体の衝突で、反発係数 e は e = -(v1' - v2') / (v1 - v2) で定義される。
0 ≤ e ≤ 1 であり、e = 1 を弾性衝突、e = 0 を完全非弾性衝突という。
弾性衝突では力学的エネルギーが保存される。

### 2.3 単振動
ばね定数 k のばねにつながれた質量 m の物体の単振動の周期は T = 2π√(m/k)。
周期は振幅によらない。
