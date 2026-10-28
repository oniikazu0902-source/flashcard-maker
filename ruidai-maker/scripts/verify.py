"""類題の答えを SymPy で計算し、想定した答えと一致するか確かめるスクリプト。

使い方:
    python verify.py problems.json

problems.json の書き方は references/types.md を参照。
OK の問題は、問題文と答えを Markdown（数式は $…$）で表示する。出力にはこれをそのまま使う。
"""

import json
import re
import sys
from itertools import combinations

from sympy import (Derivative, Function, Interval, Matrix, Rational, S, Symbol,
                   checkodesol, diff, dsolve, expand, factor, gcd, integrate,
                   latex, limit, simplify, solve, solveset, sympify, together, Eq)
from sympy.solvers.deutils import ode_order


# ---------- 共通の道具 ----------

def join_terms(terms):
    """項を「a - b + c」の形でつなぐ。"""
    text = tex(terms[0])
    for t in terms[1:]:
        text += f" - {tex(-t)}" if t.could_extract_minus_sign() else f" + {tex(t)}"
    return text


def tex(expr):
    """読みやすい LaTeX にする（\\sin{\\left(x \\right)} ではなく \\sin{x}）。
    足し算はプラスの項から始める（-e^{2x} + 2e^x ではなく 2e^x - e^{2x}）。"""
    expr = sympify(expr)
    if expr.is_Add:
        terms = expr.as_ordered_terms()
        positive = [t for t in terms if not t.could_extract_minus_sign()]
        if positive and terms[0].could_extract_minus_sign():
            terms.remove(positive[0])
            return join_terms([positive[0]] + terms)
    return latex(expr, fold_func_brackets=True)


def body_tex(expr):
    """積分・極限の中身が足し算なら、かっこで囲む（∫ 2x + y dy のあいまいさを防ぐ）。"""
    return rf"\left({tex(expr)}\right)" if expr.is_Add else tex(expr)


def sort_key(value):
    """解・固有値を小さい順に並べるための値（複素数は実部、虚部の順）。"""
    try:
        c = complex(value.evalf())
        return (c.real, c.imag)
    except TypeError:  # 文字を含む値は並べ替えない
        return (float("inf"), 0)


def short_tex(expr, forms=(simplify, together, factor)):
    """同じ値の書き方のうち、いちばん短い LaTeX を選ぶ（例：1/4 + e^2/4 → (e^2 + 1)/4）。"""
    return min((tex(f(expr)) for f in forms), key=len)


def deriv_tex(expr):
    """導関数は展開した形を優先する（x(x cos x + 2 sin x) ではなく x^2 cos x + 2x sin x）。"""
    return short_tex(expr, (expand, simplify))


def mat_tex(m):
    return latex(m, mat_str="pmatrix", mat_delim="")


def same(a, b):
    return simplify(a - b) == 0


def same_points(got, expected):
    """[[x, 値], ...] の組が、順番に関係なく一致するか。"""
    return len(got) == len(expected) and all(
        any(same(g[0], e[0]) and same(g[1], e[1]) for e in expected) for g in got
    )


def finite_points(eq, x, domain):
    pts = solveset(eq, x, domain=domain)
    if not pts.is_FiniteSet:
        raise ValueError("f'(x) = 0 の解が無限にあります。interval で範囲を指定してください")
    return sorted(pts, key=float)


def points_tex(v, points, label):
    return [rf"${v} = {tex(c)}$ で{label} ${short_tex(val)}$" for c, val in points]


# ---------- 型ごとの検算 ----------
# どの関数も (OK か, 計算結果, 問題文, 答え) を返す。

def check_limit(p, ns, P):
    x, e = ns[p["var"]], P(p["expr"])
    got = limit(e, x, P(p["at"]))
    q = rf"$\displaystyle\lim_{{{tex(x)} \to {tex(P(p['at']))}}} {body_tex(e)}$ を求めよ。"
    return same(got, P(p["answer"])), got, q, f"${short_tex(got)}$"


def check_integral(p, ns, P):
    x, e = ns[p["var"]], P(p["expr"])
    got = integrate(e, (x, P(p["lower"]), P(p["upper"])))
    q = rf"$\displaystyle\int_{{{tex(P(p['lower']))}}}^{{{tex(P(p['upper']))}}} {body_tex(e)} \, d{tex(x)}$ を求めよ。"
    return same(got, P(p["answer"])), got, q, f"${short_tex(got)}$"


def check_derivative(p, ns, P):
    x, e = ns[p["var"]], P(p["expr"])
    got = diff(e, x)
    v = tex(x)
    return (same(got, P(p["answer"])), got,
            rf"$f({v}) = {tex(e)}$ の導関数を求めよ。", rf"$f'({v}) = {deriv_tex(got)}$")


def check_solve(p, ns, P):
    x, e = ns[p["var"]], P(p["expr"])
    got = sorted(solve(e, x), key=sort_key)
    expected = [P(a) for a in p["answer"]]
    ok = len(got) == len(expected) and all(any(same(g, a) for a in expected) for g in got)
    a = rf"${tex(x)} = " + r",\ ".join(short_tex(g) for g in got) + "$"
    return ok, got, rf"方程式 ${tex(e)} = 0$ を解け。", a


def check_extrema(p, ns, P):
    """増減表と同じ方法で、f'(x) = 0 の点の前後で f'(x) の符号が変わるかを調べる。"""
    x, e = ns[p["var"]], P(p["expr"])
    d1 = diff(e, x)
    interval = [P(t) for t in p["interval"]] if "interval" in p else None
    pts = finite_points(d1, x, Interval.open(*interval) if interval else S.Reals)
    got = {"max": [], "min": [], "none": []}
    if pts:
        lo, hi = interval if interval else (pts[0] - 1, pts[-1] + 1)
        edges = [lo] + pts + [hi]
        # 隣り合う点の間で f'(x) の符号を調べる
        signs = [bool(d1.subs(x, (a + b) / 2) > 0) for a, b in zip(edges, edges[1:])]
        for i, c in enumerate(pts):
            point = [c, simplify(e.subs(x, c))]
            if signs[i] and not signs[i + 1]:
                got["max"].append(point)
            elif not signs[i] and signs[i + 1]:
                got["min"].append(point)
            else:  # 符号が変わらない点は極値ではない
                got["none"].append(point)
    ok = all(same_points(got[k], [[P(a), P(b)] for a, b in p["answer"].get(k, [])]) for k in ("max", "min"))

    v = tex(x)
    rng = rf"（${tex(interval[0])} \lt {v} \lt {tex(interval[1])}$）" if interval else ""
    parts = points_tex(v, got["max"], "極大値") + points_tex(v, got["min"], "極小値")
    a = "、".join(parts) if parts else "極値なし"
    if got["none"]:
        a += "（" + "、".join(rf"${v} = {tex(c)}$" for c, _ in got["none"]) + " は極値ではない）"
    return ok, got, rf"$f({v}) = {tex(e)}$" + (rng or " ") + "の極値を求めよ。", a


def check_maxmin(p, ns, P):
    """閉区間の最大・最小：端点と f'(x) = 0 の点の値を比べる。"""
    x, e = ns[p["var"]], P(p["expr"])
    lo, hi = [P(t) for t in p["interval"]]
    cands = [lo] + finite_points(diff(e, x), x, Interval.open(lo, hi)) + [hi]
    vals = [[c, simplify(e.subs(x, c))] for c in cands]
    top = max(float(v) for _, v in vals)
    bottom = min(float(v) for _, v in vals)
    got = {"max": [pt for pt in vals if abs(float(pt[1]) - top) < 1e-12],
           "min": [pt for pt in vals if abs(float(pt[1]) - bottom) < 1e-12]}
    ok = all(same_points(got[k], [[P(a), P(b)] for a, b in p["answer"][k]]) for k in ("max", "min"))

    v = tex(x)
    q = rf"$f({v}) = {tex(e)}$ の ${tex(lo)} \le {v} \le {tex(hi)}$ における最大値と最小値を求めよ。"
    return ok, got, q, "、".join(points_tex(v, got["max"], "最大値") + points_tex(v, got["min"], "最小値"))


def check_partial(p, ns, P):
    e = P(p["expr"])
    got = diff(e, *[ns[v] for v in p["wrt"]])
    # ∂²f/∂y∂x は「x で微分してから y で微分」。分母は微分の順と逆に書く
    groups = []
    for v in reversed(p["wrt"]):
        if groups and groups[-1][0] == v:
            groups[-1][1] += 1
        else:
            groups.append([v, 1])
    den = " ".join(rf"\partial {v}" + (f"^{{{n}}}" if n > 1 else "") for v, n in groups)
    n = len(p["wrt"])
    d = rf"\dfrac{{\partial{'^{' + str(n) + '}' if n > 1 else ''} f}}{{{den}}}"
    args = ", ".join(p["vars"])
    return (same(got, P(p["answer"])), got,
            rf"$f({args}) = {tex(e)}$ について ${d}$ を求めよ。", rf"${d} = {deriv_tex(got)}$")


def check_double_integral(p, ns, P):
    """bounds は内側の積分から順に [[変数, 下端, 上端], ...] と書く。"""
    e = P(p["expr"])
    bounds = [(ns[v], P(lo), P(hi)) for v, lo, hi in p["bounds"]]
    got = integrate(e, *bounds)
    signs = "".join(rf"\int_{{{tex(lo)}}}^{{{tex(hi)}}} " for _, lo, hi in reversed(bounds))
    ds = " ".join(rf"\, d{tex(v)}" for v, _, _ in bounds)
    q = rf"$\displaystyle{signs}{body_tex(e)} {ds}$ を求めよ。"
    return same(got, P(p["answer"])), got, q, f"${short_tex(got)}$"


MATRIX_OPS = {"det": "行列式", "inverse": "逆行列", "eigenvals": "固有値", "rank": "階数"}


def check_matrix(p, ns, P):
    m = Matrix([[P(c) for c in row] for row in p["matrix"]])
    op, ans = p["op"], p["answer"]
    if op == "det":
        got = m.det()
        ok, a = same(got, P(ans)), rf"$\det A = {short_tex(got)}$"
    elif op == "inverse":
        got = m.inv()
        expected = Matrix([[P(c) for c in r] for r in ans])
        ok = got.shape == expected.shape and all(simplify(c) == 0 for c in (got - expected))
        a =rf"$A^{{-1}} = {mat_tex(got.applyfunc(simplify))}$"
    elif op == "eigenvals":
        got = m.eigenvals()  # {固有値: 重複度}
        expected = [P(c) for c in ans]
        ok = sum(got.values()) == len(expected) and all(
            sum(1 for c in expected if same(c, val)) == mult for val, mult in got.items())
        a = r"$\lambda = " + r",\ ".join(short_tex(val) for val in sorted(got, key=sort_key)) + "$"
        multi = [val for val, mult in got.items() if mult > 1]
        if multi:
            a += "（" + "、".join(rf"$\lambda = {short_tex(val)}$ は重解" for val in multi) + "）"
    elif op == "rank":
        got = m.rank()
        ok, a = got == int(ans), rf"$\operatorname{{rank}} A = {got}$"
    else:
        raise ValueError(f"未対応の op です: {op}")
    return ok, got, rf"$A = {mat_tex(m)}$ の{MATRIX_OPS[op]}を求めよ。", a


LINSYS_ASK = {
    "none": "解をもたないように",
    "infinite": "無数の解をもつように",
    "solvable": "解をもつように",
    "unique": "ただ1つの解をもつように",
}


def generic_rank(m, k):
    """k が「ふつうの値」のときの階数（特別な値を避けるため、半端な有理数を代入して数える）。"""
    return m.subs(k, Rational(1234567, 1000003)).rank() if k is not None else m.rank()


def special_values(m, k):
    """階数が下がりうる k の値：最大の小行列式すべての共通因数（gcd）の実数解。"""
    r = generic_rank(m, k)
    if k is None or r == 0:
        return []
    g = 0
    for rows in combinations(range(m.rows), r):
        for cols in combinations(range(m.cols), r):
            g = gcd(g, m.extract(list(rows), list(cols)).det())
    return [v for v in solve(g, k) if v.is_real]


def classify(a, ab, n):
    """階数を比べて「解なし」「無数」「ただ1つ」に分ける。"""
    ra, rab = a.rank(), ab.rank()
    if ra < rab:
        return "none"
    return "unique" if ra == n else "infinite"


def linsys_sets(a, ab, n, k):
    """条件ごとに、成り立つ k の範囲を {"only": [...]} か {"except": [...]} で返す。"""
    cands = sorted(set(special_values(a, k)) | set(special_values(ab, k)), key=sort_key)
    gen = classify(a.subs(k, Rational(1234567, 1000003)), ab.subs(k, Rational(1234567, 1000003)), n) \
        if k is not None else classify(a, ab, n)
    at = {c: classify(a.subs(k, c), ab.subs(k, c), n) for c in cands}
    holds = {
        "none": lambda c: c == "none",
        "infinite": lambda c: c == "infinite",
        "solvable": lambda c: c != "none",
        "unique": lambda c: c == "unique",
    }
    result = {}
    for name, ok in holds.items():
        if ok(gen):
            result[name] = {"except": [c for c in cands if not ok(at[c])]}
        else:
            result[name] = {"only": [c for c in cands if ok(at[c])]}
    return gen, at, result


def same_values(got, expected):
    return len(got) == len(expected) and all(any(same(g, e) for e in expected) for g in got)


def check_general_solution(a, b, sol, xs, ns, P):
    """解が方程式を満たし、任意定数の数が「変数の数 − 階数」と同じで、それぞれが独立か。"""
    vec = Matrix([P(s) for s in sol])
    params = sorted(vec.free_symbols - set(ns.values()), key=lambda s: s.name)
    satisfies = all(simplify(e) == 0 for e in (a * vec - b))
    dim = len(xs) - a.rank()
    independent = len(params) == dim and (dim == 0 or vec.jacobian(params).rank() == dim)
    return satisfies and independent, vec, params, {"方程式を満たす": satisfies, "任意定数": len(params), "必要な数": dim}


def system_tex(a, b, xs):
    """連立方程式を cases 環境で書く（係数 0 の項は省く）。"""
    lines = []
    for i in range(a.rows):
        terms = [a[i, j] * x for j, x in enumerate(xs) if a[i, j] != 0]
        left = join_terms(terms) if terms else "0"
        lines.append(f"{left} = {tex(b[i])}")
    return r"\begin{cases} " + r" \\ ".join(lines) + r" \end{cases}"


def check_linsys(p, ns, P):
    """パラメータ付き連立1次方程式。answer は k の値のリスト、または {"except": [...]}（それ以外の全部）。"""
    xs = [ns[v] for v in p["vars"]]
    k = ns.get(p["param"]) if "param" in p else None
    a = Matrix([[P(c) for c in row] for row in p["matrix"]])
    b = Matrix([P(c) for c in p["rhs"]])
    ab = a.row_join(b)
    ask = p.get("ask", "solve")
    system = system_tex(a, b, xs)

    if k is None:  # パラメータなし：解を求める
        kind = classify(a, ab, len(xs))
        if kind == "none":
            ok, got, ans = p["answer"] == "none", "解なし", "解なし"
        else:
            ok, vec, params, got = check_general_solution(a, b, p["answer"], xs, ns, P)
            ans = rf"$({', '.join(tex(x) for x in xs)}) = \left({', '.join(short_tex(c) for c in vec)}\right)$"
            if params:
                ans += f"（${', '.join(tex(s) for s in params)}$ は任意）"
        return ok, got, rf"次の連立1次方程式を解け。 $$ {system} $$", ans

    gen, at, sets = linsys_sets(a, ab, len(xs), k)
    target = sets[ask]
    exp = p["answer"]
    if isinstance(exp, dict):
        ok = "except" in target and same_values(target["except"], [P(v) for v in exp["except"]])
    else:
        ok = "only" in target and same_values(target["only"], [P(v) for v in exp])
    got = {"ふつうの k": gen, "特別な k": {str(c): v for c, v in at.items()}}

    kv = tex(k)
    if "only" in target:
        ans = rf"${kv} = " + r",\ ".join(tex(v) for v in target["only"]) + "$"
    else:
        ans = rf"${kv} \neq " + r",\ ".join(tex(v) for v in target["except"]) + "$" if target["except"] else "すべての実数"

    q = rf"次の連立1次方程式が{LINSYS_ASK[ask]}定数 ${kv}$ の値を定めよ"
    if "solution" in p:  # そのときの解も問う
        if "at" in p:
            at_k = P(p["at"])
        elif len(target.get("only", [])) == 1:
            at_k = target["only"][0]
        else:
            raise ValueError("解を確かめる k の値を at で指定してください")
        a0, b0 = a.subs(k, at_k), b.subs(k, at_k)
        sol_ok, vec, params, detail = check_general_solution(a0, b0, p["solution"], xs, ns, P)
        ok = ok and sol_ok
        got["解の検算"] = detail
        q += "。また、そのときの解を求めよ"
        ans += rf"。このとき $({', '.join(tex(x) for x in xs)}) = \left({', '.join(short_tex(c) for c in vec)}\right)$"
        if params:
            ans += f"（${', '.join(tex(s) for s in params)}$ は任意）"
    return ok, got, q + rf"。 $$ {system} $$", ans


def ode_text(eq, f, x):
    """y(x).diff(x, 2) を y'' のように書き、階数の高い項から並べる（y'' - 3y' + 2y）。"""
    name = f.__name__
    order = ode_order(eq, f(x))
    syms = [Symbol(name + "'" * n) for n in range(order + 1)]  # y, y', y'', …
    for n in range(order, 0, -1):
        eq = eq.subs(Derivative(f(x), (x, n)), syms[n])
    eq = eq.subs(f(x), syms[0])

    def rank(term):
        return -max((n for n, s in enumerate(syms) if term.has(s)), default=-1)

    return join_terms(sorted(eq.as_ordered_terms(), key=rank))


def parse_ics(ics, f, x, P):
    """{"y(0)": "1", "y'(0)": "0"} を SymPy の初期条件にする。"""
    result = {}
    for key, value in ics.items():
        m = re.fullmatch(r"(\w+)('*)\((.+)\)", key.replace(" ", ""))
        if not m or m.group(1) != f.__name__:
            raise ValueError(f"初期条件の書き方が違います: {key}")
        n, at = len(m.group(2)), P(m.group(3))
        result[f(at) if n == 0 else f(x).diff(x, n).subs(x, at)] = P(value)
    return result


def check_ode(p, ns, P):
    """初期条件なし：答えが方程式を満たし、任意定数の数が階数と同じなら OK。
    初期条件あり：dsolve で解いた答えと一致すれば OK。"""
    x, f = ns[p["var"]], ns[p["func"]]
    eq = P(p["ode"])
    ans = P(p["answer"])
    lhs = ode_text(eq, f, x)
    y = f.__name__
    if "ics" in p:
        got = dsolve(eq, f(x), ics=parse_ics(p["ics"], f, x, P)).rhs
        conds = r",\ ".join(f"{k.replace(' ', '')} = {tex(P(v))}" for k, v in p["ics"].items())
        q = rf"微分方程式 ${lhs} = 0$ を、初期条件 ${conds}$ のもとで解け。"
        return same(got, ans), got, q, rf"${y} = {deriv_tex(got)}$"
    order = ode_order(eq, f(x))
    consts = {s for s in ans.free_symbols if re.fullmatch(r"C\d+", s.name)}
    satisfies = checkodesol(eq, Eq(f(x), ans))[0]
    got = {"方程式を満たす": satisfies, "任意定数の数": len(consts), "階数": order}
    ok = satisfies and len(consts) == order
    return ok, got, rf"微分方程式 ${lhs} = 0$ の一般解を求めよ。", rf"${y} = {tex(ans)}$（$C_1, C_2, \ldots$ は任意定数）"


CHECKS = {
    "limit": check_limit, "integral": check_integral, "derivative": check_derivative,
    "solve": check_solve, "extrema": check_extrema, "maxmin": check_maxmin,
    "partial": check_partial, "double_integral": check_double_integral,
    "matrix": check_matrix, "ode": check_ode, "linsys": check_linsys,
}


def namespace(p):
    """問題で使う変数・関数の名前を SymPy の記号にする。"""
    names = p.get("vars") or ([p["var"]] if "var" in p else [])
    ns = {n: Symbol(n) for n in names}
    if "param" in p:
        ns[p["param"]] = Symbol(p["param"])
    if "func" in p:
        ns[p["func"]] = Function(p["func"])
    return ns


def main():
    if len(sys.argv) != 2:
        print("使い方: python verify.py problems.json")
        sys.exit(2)
    # utf-8-sig：Windows のメモ帳や PowerShell が付ける BOM があっても読めるようにする
    with open(sys.argv[1], encoding="utf-8-sig") as fp:
        problems = json.load(fp)

    ng = 0
    for p in problems:
        ns = namespace(p)
        P = lambda text, ns=ns: sympify(text, locals=ns)
        try:
            if p["type"] not in CHECKS:
                raise ValueError(f"未対応の type です: {p['type']}")
            ok, got, q, a = CHECKS[p["type"]](p, ns, P)
        except Exception as e:  # 式の書き間違いなど
            print(f"[ERROR] {p.get('id')}: {e}")
            ng += 1
            continue
        if ok:
            print(f"[OK] {p['id']}")
            print(f"  問題: {q}")
            print(f"  答え: {a}")
        else:
            print(f"[NG] {p['id']}: 計算結果 {got} / 想定 {p['answer']}")
            ng += 1

    print(f"--- {len(problems)} 問中 OK {len(problems) - ng} 問、NG {ng} 問")
    sys.exit(1 if ng else 0)


if __name__ == "__main__":
    main()
