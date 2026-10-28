# 検算用ファイル（problems.json）の書き方

**使う型の節だけ読めばよい。** 全型に共通：`id`（問題の番号）、`type`（型）、`answer`（想定した答え）。
式は Python（SymPy）の書き方：かけ算は `*`、累乗は `**`、`exp(x)`、`log(x)`、`sqrt(x)`、`pi`、`sin(x)`。

## limit（極限）
```json
{"id": "1", "type": "limit", "expr": "sin(3*x)/x", "var": "x", "at": "0", "answer": "3"}
```
`at` は `oo`（+∞）、`-oo`（−∞）も使える。

## integral（定積分）
```json
{"id": "2", "type": "integral", "expr": "x*exp(2*x)", "var": "x", "lower": "0", "upper": "1", "answer": "(exp(2)+1)/4"}
```

## derivative（導関数）
```json
{"id": "3", "type": "derivative", "expr": "x**2*sin(x)", "var": "x", "answer": "2*x*sin(x) + x**2*cos(x)"}
```

## solve（方程式 expr = 0 の解）
```json
{"id": "4", "type": "solve", "expr": "x**2 - 5*x + 6", "var": "x", "answer": ["2", "3"]}
```

## extrema（極値）
```json
{"id": "5", "type": "extrema", "expr": "x**3 - 3*x", "var": "x", "answer": {"max": [["-1", "2"]], "min": [["1", "-2"]]}}
{"id": "6", "type": "extrema", "expr": "sin(x) + cos(x)", "var": "x", "interval": ["0", "2*pi"], "answer": {"max": [["pi/4", "sqrt(2)"]], "min": [["5*pi/4", "-sqrt(2)"]]}}
```
- `answer` は `{"max": [[x, 極大値], …], "min": [[x, 極小値], …]}`。極値がなければ両方 `[]`。
- 判定は増減表と同じ方法（$f'(x) = 0$ の点の前後で $f'(x)$ の符号が変わるか）。
  $f'(x) = 0$ でも極値でない点（例：$x^4 - 4x^3$ の $x = 0$）は `answer` に書かない。
- $\sin x$ のように $f'(x) = 0$ の解が無限にある関数は、`interval`（開区間）を必ず指定する。

## maxmin（閉区間の最大値・最小値）
```json
{"id": "7", "type": "maxmin", "expr": "x**3 - 3*x", "var": "x", "interval": ["0", "3"], "answer": {"max": [["3", "18"]], "min": [["1", "-2"]]}}
```
- 端点と $f'(x) = 0$ の点の値を比べる。同じ値で最大になる点が複数あれば、すべて書く。

## partial（偏微分）
```json
{"id": "8", "type": "partial", "expr": "x**2*y**3", "vars": ["x", "y"], "wrt": ["x", "y"], "answer": "6*x*y**2"}
```
- `wrt` は**微分する順**。`["x", "y"]` は「x で微分してから y で微分」＝ $\dfrac{\partial^2 f}{\partial y \partial x}$。
- 1回だけなら `["x"]`、2回同じ変数なら `["x", "x"]`。

## double_integral（重積分・累次積分）
```json
{"id": "9", "type": "double_integral", "expr": "x*y", "vars": ["x", "y"], "bounds": [["y", "0", "x"], ["x", "0", "1"]], "answer": "1/8"}
```
- `bounds` は**内側の積分から順に** `[変数, 下端, 上端]`。上の例は $\displaystyle\int_0^1 \int_0^x xy \, dy \, dx$。

## matrix（行列）
```json
{"id": "10", "type": "matrix", "op": "det", "matrix": [["1", "2"], ["3", "4"]], "answer": "-2"}
{"id": "11", "type": "matrix", "op": "inverse", "matrix": [["1", "2"], ["3", "4"]], "answer": [["-2", "1"], ["3/2", "-1/2"]]}
{"id": "12", "type": "matrix", "op": "eigenvals", "matrix": [["2", "1"], ["0", "2"]], "answer": ["2", "2"]}
{"id": "13", "type": "matrix", "op": "rank", "matrix": [["1", "2"], ["2", "4"]], "answer": "1"}
```
- `op`：`det`（行列式）、`inverse`（逆行列）、`eigenvals`（固有値）、`rank`（階数）
- 固有値の重解は、重複度の数だけ並べる（上の例は 2 が重解）。
- 文字を含む行列は `"vars": ["a"]` を付ける。

## ode（常微分方程式）
```json
{"id": "14", "type": "ode", "ode": "y(x).diff(x, 2) + y(x)", "var": "x", "func": "y", "answer": "C1*sin(x) + C2*cos(x)"}
{"id": "15", "type": "ode", "ode": "y(x).diff(x, 2) - 3*y(x).diff(x) + 2*y(x)", "var": "x", "func": "y", "ics": {"y(0)": "0", "y'(0)": "1"}, "answer": "exp(2*x) - exp(x)"}
```
- `ode` は「左辺 = 0」の左辺。$y'$ は `y(x).diff(x)`、$y''$ は `y(x).diff(x, 2)`。
- 一般解の任意定数は `C1`、`C2`… と書く。
  **初期条件なし**：答えが方程式を満たし、任意定数の数が階数と同じなら OK（定数の付け方が違う正しい一般解も OK になる）。
  **初期条件あり**（`ics`）：解いた結果と答えが一致すれば OK。
