#!/usr/bin/env python3
"""
Solve Hacker101 Model E1337 v2: recover state from one wrong 64-bit code, predict next next(64).

Matrix construction follows 7Rocky's v2 write-up (triple state step per output bit).
"""
from __future__ import annotations

import re
import sys


def step_state(state: int) -> int:
    state = (state << 1) ^ (state >> 61)
    state &= 0xFFFFFFFFFFFFFFFF
    state ^= 0xFFFFFFFFFFFFFFFF
    for j in range(0, 64, 4):
        cur = (state >> j) & 0xF
        cur = (cur >> 3) | ((cur >> 2) & 2) | ((cur << 3) & 8) | ((cur << 2) & 4)
        state ^= cur << j
    return state


def build_transition_matrix() -> list[list[int]]:
    """
    64x64 M over GF(2) in **MSB-first state basis** x[0..63] where
    x[j] = (state >> (63 - j)) & 1  (same convention as 7Rocky's ret_mat rows).
    """
    m = [[0] * 64 for _ in range(64)]
    for k in range(64):
        old_state = 1 << (63 - k)
        out = step_state(old_state)
        for i in range(64):
            m[i][k] = (out >> (63 - i)) & 1
    return m


def mat_mul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    n = len(a)
    c = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            v = 0
            for k in range(n):
                v ^= a[i][k] & b[k][j]
            c[i][j] = v
    return c


def mat_pow(mat: list[list[int]], e: int) -> list[list[int]]:
    n = len(mat)
    acc = [[int(i == j) for j in range(n)] for i in range(n)]
    base = mat
    while e:
        if e & 1:
            acc = mat_mul(acc, base)
        base = mat_mul(base, base)
        e >>= 1
    return acc


def row_vec_mat_mul(row: list[int], mat: list[list[int]]) -> list[int]:
    """row (1xn) * mat (nxn) -> row (1xn) over GF(2)."""
    n = len(row)
    out = [0] * n
    for j in range(n):
        v = 0
        for k in range(n):
            v ^= row[k] & mat[k][j]
        out[j] = v
    return out


def gauss_elim(x_mat: list[list[int]], b_vec: list[int]) -> list[int] | None:
    """Solve A x = b over GF(2). x_mat is n x n, b_vec length n. Returns x or None."""
    n = len(x_mat)
    aug = [x_mat[i] + [b_vec[i]] for i in range(n)]

    for col in range(n):
        pivot = None
        for r in range(col, n):
            if aug[r][col]:
                pivot = r
                break
        if pivot is None:
            continue
        aug[col], aug[pivot] = aug[pivot], aug[col]
        for r in range(n):
            if r != col and aug[r][col]:
                aug[r] = [a ^ b for a, b in zip(aug[r], aug[col])]

    for r in range(n):
        if aug[r][r] == 0 and any(aug[r][c] for c in range(n)):
            if aug[r][n]:
                return None
        if aug[r][r] == 0:
            continue
        for r2 in range(n):
            if r2 != r and aug[r2][r]:
                aug[r2] = [a ^ b for a, b in zip(aug[r2], aug[r])]

    return [aug[i][n] for i in range(n)]


def next_rng(state: int, bits: int) -> tuple[int, int]:
    """Return (new_state, ret) matching rng.next(bits)."""
    ret = 0
    for _ in range(bits):
        ret <<= 1
        ret |= state & 1
        for _k in range(3):
            state = step_state(state)
    return state, ret


def solve_from_expected_code(expected: int) -> int:
    """
    Server calls next(64) and returns that value as 'Expected'.
    Recover internal state *before* that call, then caller can advance.
    """
    m = build_transition_matrix()
    t = mat_mul(mat_mul(m, m), m)

    # rows: 16 quartet constraints, then 48 output equations (48 MSBs of expected code)
    rows: list[list[int]] = []
    rhs: list[int] = []

    for i in range(16):
        rows.append(list(map(int, list(f"{9 << (4 * i):064b}"))))
        rhs.append(0)

    # LSB of Python int = x[63]; first output bit of next(64) is MSB of ret = that LSB
    row = [0] * 64
    row[63] = 1
    for k in range(48):
        obs = (expected >> (63 - k)) & 1
        rows.append(row[:])
        rhs.append(obs)
        row = row_vec_mat_mul(row, t)

    sol = gauss_elim(rows, rhs)
    if sol is None:
        raise RuntimeError("no solution (over/under constrained?)")
    state = 0
    for i in range(64):
        if sol[i]:
            state |= 1 << (63 - i)
    return state


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: solve_v2.py <base_url>   # e.g. https://abc123.ctf.hacker101.com", file=sys.stderr)
        sys.exit(1)
    import urllib.error
    import urllib.parse
    import urllib.request

    base = sys.argv[1].rstrip("/")

    def post_unlock(code: int) -> str:
        data = urllib.parse.urlencode({"code": str(code)}).encode()
        req = urllib.request.Request(f"{base}/unlock", data=data, method="POST")
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read().decode()

    try:
        body = post_unlock(0)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
    except Exception as e:
        print(f"request failed: {e}", file=sys.stderr)
        sys.exit(2)

    m = re.search(r"Expected\s+(\d+)", body)
    if not m:
        print(body[:500], file=sys.stderr)
        raise SystemExit("could not parse Expected code from /unlock response")

    code1 = int(m.group(1))
    state = solve_from_expected_code(code1)
    # Advance past the server's next(64) that produced code1
    state, _ = next_rng(state, 64)
    # Predict what server will expect next
    state, code2 = next_rng(state, 64)
    try:
        out = post_unlock(code2)
    except urllib.error.HTTPError as e:
        out = e.read().decode()
    print(out)


if __name__ == "__main__":
    main()
