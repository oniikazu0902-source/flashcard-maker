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
- `op`：`det`（行列式）、`inverse`（逆行列）、`eigenvals`（固有値）、`rank`（階数）、`eigenvects`（固有ベクトル）、`expr`（行列の式）
- 固有値の重解は、重複度の数だけ並べる（上の例は 2 が重解）。
- 文字を含む行列は `"vars": ["a"]` を付ける。

### 固有ベクトル（`eigenvects`）
```json
{"id": "20", "type": "matrix", "op": "eigenvects", "matrix": [["0", "1"], ["-4", "4"]], "answer": [{"value": "2", "vectors": [["1", "2"]]}]}
```
- 固有値ごとに `{"value": 固有値, "vectors": [固有ベクトル, …]}` を書く。すべての固有値を書く。
- 固有ベクトルは定数倍してもよい。$Av = \lambda v$ を満たすか、本数が固有空間の次元と同じか、互いに独立かを確かめる。

### 行列の式（`expr`）
```json
{"id": "21", "type": "matrix", "op": "expr", "expr": "P**-1*A*P", "mats": {"A": [["0", "1"], ["-4", "4"]], "P": [["1", "0"], ["2", "1"]]}, "answer": [["2", "1"], ["0", "2"]]}
{"id": "22", "type": "matrix", "op": "expr", "expr": "A**n", "int_vars": ["n"], "mats": {"A": [["0", "1"], ["-4", "4"]]}, "answer": [["(1-n)*2**n", "n*2**(n-1)"], ["-n*2**(n+1)", "(n+1)*2**n"]]}
```
- `mats` に使う行列を名前つきで書く。`expr` は行列の名前を使った式（積は `*`、逆行列は `**-1`、累乗は `**`）。
- $A^n$ の $n$ のような自然数は `int_vars` に書く。
- 「$B = P^{-1}AP$ を示せ」「$B^n = \ldots$ を数学的帰納法で示せ」の結論の確認にも使える。

## linsys（連立1次方程式）
```json
{"id": "16", "type": "linsys", "vars": ["x", "y", "z"], "param": "k", "ask": "none", "matrix": [["1", "-1", "1"], ["1", "4", "k"], ["2", "k", "4"]], "rhs": ["1", "2", "3"], "answer": ["-4"]}
{"id": "17", "type": "linsys", "vars": ["x", "y", "z"], "param": "k", "ask": "infinite", "matrix": [["1", "-1", "1"], ["1", "5", "k"], ["2", "k", "5"]], "rhs": ["1", "2", "3"], "answer": ["4"], "solution": ["(7-9*a)/6", "(1-3*a)/6", "a"]}
{"id": "18", "type": "linsys", "vars": ["x", "y", "z"], "param": "k", "ask": "unique", "matrix": [["1", "-1", "1"], ["1", "5", "k"], ["2", "k", "5"]], "rhs": ["1", "2", "3"], "answer": {"except": ["-5", "4"]}}
{"id": "19", "type": "linsys", "vars": ["x", "y", "z"], "matrix": [["1", "1", "1"], ["1", "-1", "2"], ["2", "1", "-1"]], "rhs": ["6", "5", "1"], "answer": ["1", "2", "3"]}
```
- `matrix` は係数（行ごと）、`rhs` は右辺。`param` は定数（$k$ など）の名前。
- `ask`：`none`（解をもたない）、`infinite`（無数の解をもつ）、`solvable`（解をもつ）、`unique`（ただ1つの解をもつ）
- `answer`：条件を満たす $k$ の値のリスト。「この値以外すべて」のときは `{"except": [...]}`。
- `solution`（任意）：そのときの解。任意定数は `a`、`b` などの文字で書く。解が方程式を満たすことに加え、
  **任意定数の数が「変数の数 − 階数」と同じか**も確かめる（特殊解だけを書いた答えは NG になる）。
  $k$ の候補が2つ以上あるときは、`"at": "4"` のように解を確かめる $k$ を指定する。
- `param` がないときは「連立方程式を解け」の問題になり、`answer` に解を書く（解なしなら `"none"`）。
- $k$ の候補は、行列式だけでなく小行列式の共通因数から探すので、行列式が $k$ によらず 0 の問題にも使える。

## ode（常微分方程式）
```json
{"id": "14", "type": "ode", "ode": "y(x).diff(x, 2) + y(x)", "var": "x", "func": "y", "answer": "C1*sin(x) + C2*cos(x)"}
{"id": "15", "type": "ode", "ode": "y(x).diff(x, 2) - 3*y(x).diff(x) + 2*y(x)", "var": "x", "func": "y", "ics": {"y(0)": "0", "y'(0)": "1"}, "answer": "exp(2*x) - exp(x)"}
```
- `ode` は「左辺 = 0」の左辺。$y'$ は `y(x).diff(x)`、$y''$ は `y(x).diff(x, 2)`。
- 一般解の任意定数は `C1`、`C2`… と書く。
  **初期条件なし**：答えが方程式を満たし、任意定数の数が階数と同じなら OK（定数の付け方が違う正しい一般解も OK になる）。
  **初期条件あり**（`ics`）：解いた結果と答えが一致すれば OK。

## prob（確率：箱から球を取り出す）
```json
{"id": "23", "type": "prob", "vars": ["n"], "balls": {"赤": "2", "白": "n-2"}, "draws": 3, "event": {"at": {"2": "赤"}}, "answer": "2/n"}
{"id": "24", "type": "prob", "vars": ["n"], "balls": {"赤": "2", "白": "n-2"}, "draws": 3, "event": {"at": {"1": "赤"}}, "given": {"at": {"3": "赤"}}, "answer": "1/(n-1)"}
```
- `balls` は色ごとの個数（文字を使うなら `vars` に書く）。`draws` は取り出す回数。戻すときは `"replace": true`。
- `event`（求める事象）と `given`（条件）は、`{"at": {"何回目": "色"}}` と `{"count": {"色": 個数}}` で書く（両方書くと「かつ」）。
- `given` があれば条件付き確率 $P(\text{event} \mid \text{given})$ になる。
- 色の出方をすべて数え上げて計算する。個数に文字があっても、そのまま式で計算する。

## identity（「〜を示せ」の等式）
```json
{"id": "25", "type": "identity", "vars": ["x", "s"], "funcs": ["g"], "lhs": "g(log(x)).diff(x)", "rhs": "g(s).diff(s)*exp(-s)", "subs": {"s": "log(x)"}}
{"id": "26", "type": "identity", "vars": ["x"], "lhs": "Integral(sqrt(x)*exp(-x), (x, 0, oo))", "rhs": "Integral(exp(-x)/sqrt(x), (x, 0, oo))/2"}
```
- `lhs = rhs` が成り立てば OK。`answer` は書かない。
- 確かめるのは**結論の等式だけ**で、証明の過程（式変形の正しさ）は確かめない。出力には「検算：結論のみ」と書く。
- 関数 $y(s)$ のような「中身の決まっていない関数」は `funcs` に書く。$x = e^s$ のような置き換えは `subs` に書く。
- 積分は `Integral(...)` と書く（`integrate` と書くと先に計算されてしまう）。
- 微分を含む式の問題文の表示は読みにくいので、類題の問題文には使わない。
