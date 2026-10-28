"""類題の答えを SymPy で計算し、想定した答えと一致するか確かめるスクリプト。

使い方:
    python verify.py problems.json

problems.json の書き方は SKILL.md を参照。
"""

import json
import sys

from sympy import Symbol, diff, integrate, limit, simplify, solve, sympify


def compute(p):
    """問題1つ分の答えを SymPy で計算して返す。"""
    x = Symbol(p["var"])
    expr = sympify(p["expr"], locals={p["var"]: x})
    kind = p["type"]
    if kind == "limit":
        return limit(expr, x, sympify(p["at"]))
    if kind == "integral":
        return integrate(expr, (x, sympify(p["lower"]), sympify(p["upper"])))
    if kind == "derivative":
        return diff(expr, x)
    if kind == "solve":
        return solve(expr, x)
    raise ValueError(f"未対応の type です: {kind}")


def matches(kind, got, answer, var):
    """計算結果と想定した答えが数学的に等しいか判定する。"""
    x = Symbol(var)
    if kind == "solve":
        expected = [sympify(a, locals={var: x}) for a in answer]
        return len(got) == len(expected) and all(
            any(simplify(g - e) == 0 for e in expected) for g in got
        )
    return simplify(got - sympify(answer, locals={var: x})) == 0


def main():
    if len(sys.argv) != 2:
        print("使い方: python verify.py problems.json")
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        problems = json.load(f)

    ng = 0
    for p in problems:
        try:
            got = compute(p)
            ok = matches(p["type"], got, p["answer"], p["var"])
        except Exception as e:  # 式の書き間違いなど
            print(f"[ERROR] {p.get('id')}: {e}")
            ng += 1
            continue
        if ok:
            print(f"[OK] {p['id']}: 答え {got}")
        else:
            print(f"[NG] {p['id']}: 計算結果 {got} / 想定 {p['answer']}")
            ng += 1

    print(f"--- {len(problems)} 問中 OK {len(problems) - ng} 問、NG {ng} 問")
    sys.exit(1 if ng else 0)


if __name__ == "__main__":
    main()
