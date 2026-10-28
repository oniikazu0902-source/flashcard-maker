"""類題の答えを SymPy で計算し、想定した答えと一致するか確かめるスクリプト。

使い方:
    python verify.py problems.json

problems.json の書き方は SKILL.md を参照。
OK の問題は、問題の式と答えを LaTeX でも表示する。出力にはこの LaTeX をそのまま使う。
"""

import json
import sys

from sympy import (S, Symbol, diff, integrate, latex, limit, simplify, solve,
                   solveset, sympify)


def parse(text, x, var):
    return sympify(text, locals={var: x})


def extrema(expr, x):
    """f'(x) = 0 となる点を、f''(x) の符号で極大・極小に分ける。"""
    d1 = diff(expr, x)
    d2 = diff(d1, x)
    result = {"max": [], "min": [], "unknown": []}
    for c in sorted(solveset(d1, x, domain=S.Reals)):
        sign = d2.subs(x, c)
        point = [c, simplify(expr.subs(x, c))]
        if sign < 0:
            result["max"].append(point)
        elif sign > 0:
            result["min"].append(point)
        else:  # f''(c) = 0 のときは、この方法では判定できない
            result["unknown"].append(point)
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
        if got["unknown"]:
            return False
        return all(
            same_points(got[k], [[parse(a, x, var), parse(b, x, var)] for a, b in answer.get(k, [])])
            for k in ("max", "min")
        )
    return same(got, parse(answer, x, var))


def problem_latex(p, x):
    """問題の式を LaTeX にする。"""
    e = latex(parse(p["expr"], x, p["var"]))
    v = latex(x)
    kind = p["type"]
    if kind == "limit":
        return rf"\displaystyle\lim_{{{v} \to {latex(sympify(p['at']))}}} {e}"
    if kind == "integral":
        return rf"\displaystyle\int_{{{latex(sympify(p['lower']))}}}^{{{latex(sympify(p['upper']))}}} {e} \, d{v}"
    if kind == "solve":
        return rf"{e} = 0"
    return rf"f({v}) = {e}"


def answer_latex(kind, got, x):
    """答えを LaTeX にする。"""
    v = latex(x)
    if kind == "solve":
        return ", ".join(rf"{v} = {latex(g)}" for g in got)
    if kind == "extrema":
        parts = [rf"{v} = {latex(c)} で極大値 {latex(val)}" for c, val in got["max"]]
        parts += [rf"{v} = {latex(c)} で極小値 {latex(val)}" for c, val in got["min"]]
        return "、".join(parts) if parts else "極値なし"
    return latex(got)


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
            print(f"  問題: {problem_latex(p, x)}")
            print(f"  答え: {answer_latex(p['type'], got, x)}")
        else:
            print(f"[NG] {p['id']}: 計算結果 {got} / 想定 {p['answer']}")
            ng += 1

    print(f"--- {len(problems)} 問中 OK {len(problems) - ng} 問、NG {ng} 問")
    sys.exit(1 if ng else 0)


if __name__ == "__main__":
    main()
