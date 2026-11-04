# ruidai-v7 解答例モードの出力（例題9〜11）

入力：`examples/sample-problems.md` の例題9〜11（自作）。
SKILL.md の「解答例モード」に従い、Claude が解答を書き、`problems.json` で検算した。

## 例題9

(1) 固有方程式は
$\det(A - \lambda E) = (1 - \lambda)(3 - \lambda) + 1 = \lambda^2 - 4\lambda + 4 = (\lambda - 2)^2 = 0$
より、固有値は $\lambda = 2$（重解）。
$(A - 2E)\boldsymbol{x} = \boldsymbol{0}$ は $\begin{pmatrix} -1 & 1 \\ -1 & 1 \end{pmatrix}\begin{pmatrix} x_1 \\ x_2 \end{pmatrix} = \begin{pmatrix} 0 \\ 0 \end{pmatrix}$、すなわち $x_1 = x_2$。
よって固有ベクトルは $c \begin{pmatrix} 1 \\ 1 \end{pmatrix}$（$c \neq 0$）。
　　検算：OK

(2) $P^{-1} = \begin{pmatrix} 1 & 0 \\ -1 & 1 \end{pmatrix}$ である。
$AP = \begin{pmatrix} 1 & 1 \\ -1 & 3 \end{pmatrix}\begin{pmatrix} 1 & 0 \\ 1 & 1 \end{pmatrix} = \begin{pmatrix} 2 & 1 \\ 2 & 3 \end{pmatrix}$ より、
$P^{-1}AP = \begin{pmatrix} 1 & 0 \\ -1 & 1 \end{pmatrix}\begin{pmatrix} 2 & 1 \\ 2 & 3 \end{pmatrix} = \begin{pmatrix} 2 & 1 \\ 0 & 2 \end{pmatrix}$。
　　検算：結論のみ

(3) $B = P^{-1}AP$ とおくと、(2) より $A = PBP^{-1}$。よって $A^n = PB^nP^{-1}$ であり、与えられた $B^n$ を用いて
$A^n = \begin{pmatrix} 1 & 0 \\ 1 & 1 \end{pmatrix}\begin{pmatrix} 2^n & n 2^{n-1} \\ 0 & 2^n \end{pmatrix}\begin{pmatrix} 1 & 0 \\ -1 & 1 \end{pmatrix} = \begin{pmatrix} (2 - n)2^{n-1} & n 2^{n-1} \\ -n 2^{n-1} & (n + 2)2^{n-1} \end{pmatrix}$。
　　検算：OK

## 例題10

(1) 1回目が赤球の場合と白球の場合に分けて、
$\dfrac{3}{n} \cdot \dfrac{2}{n - 1} + \dfrac{n - 3}{n} \cdot \dfrac{3}{n - 1} = \dfrac{3(n - 1)}{n(n - 1)} = \dfrac{3}{n}$。
　　検算：OK

(2) 1回目と2回目がともに赤球である確率は $\dfrac{3}{n} \cdot \dfrac{2}{n - 1} = \dfrac{6}{n(n - 1)}$。
(1) より、求める条件付き確率は $\dfrac{6}{n(n - 1)} \div \dfrac{3}{n} = \dfrac{2}{n - 1}$。
　　検算：OK

## 例題11

$x = e^s$ より $\dfrac{dx}{ds} = e^s$。合成関数と逆関数の微分より
$\dfrac{dy}{dx} = \dfrac{dy}{ds} \cdot \dfrac{ds}{dx} = \dfrac{dy}{ds} \cdot \dfrac{1}{e^s} = e^{-s} \dfrac{dy}{ds}$。
　　検算：結論のみ

---
検算の結果：`problems.json`（誤答4問を含む）。10問中 OK 6問、NG 4問（NG はすべて、わざと入れた誤答）。
