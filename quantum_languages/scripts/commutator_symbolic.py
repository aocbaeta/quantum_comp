#!/usr/bin/env python3
from __future__ import annotations

GENERIC_SPIN = "s"
sg = GENERIC_SPIN


def delta(a, b):
    return [[a[1], b[1]], [a[2], b[2]]]


def _allowed_contraction(lhs, rhs):
    lhs_kind, _, lhs_spin = lhs
    rhs_kind, _, rhs_spin = rhs

    if lhs_kind == rhs_kind:
        return False

    if rhs_spin != GENERIC_SPIN and lhs_spin != rhs_spin:
        return False

    return True


def _sign_from_expansion_order(interaction_index):
    return 1 if interaction_index % 2 == 0 else -1


def comm(v1, v2):
    sig = []
    flt = []
    dta = []
    interaction_index = 0

    for i, lhs in enumerate(v1):
        _, lhs_site, _ = lhs
        left_prefix = v1[:i]
        left_suffix = v1[i + 1 :]

        for j, rhs in enumerate(v2):
            sign = _sign_from_expansion_order(interaction_index)
            interaction_index += 1

            if not _allowed_contraction(lhs, rhs):
                continue

            flatt = left_prefix + v2[:j] + v2[j + 1 :] + left_suffix
            sig.append([sign])
            flt.append(flatt)
            dta.append([] if lhs_site == rhs[1] else delta(lhs, rhs))

    return [sig, flt, dta]


def format_element(x):
    if isinstance(x, int):
        return f"{x:+2}"
    return str(x)


def render_result(result):
    lines = []
    for sig_row, flt_row, dta_row in zip(*result):
        sig = f"[{sig_row[0]:+2}]"
        flt = ", ".join(
            f"[{format_element(item[0])}, {format_element(item[1])}, {format_element(item[2])}]"
            for item in flt_row
        )
        dta = ", ".join(
            f"[{format_element(item[0])}, {format_element(item[1])}]"
            for item in dta_row
        )
        lines.append(f"{sig}, [{flt}], [{dta}]")
    return "\n".join(lines)


def print_formatted(result):
    print(render_result(result))


def _example_inputs():
    cdk = [[1, 1, 1]]
    vsg = [[1, 2, sg], [0, 2, sg]]
    vpk = [[1, 2, 1], [1, -2, -1], [0, -3, -1], [0, 3, 1]]
    bdk = [[1, 4, 1], [1, -4, -1], [0, -1, -1]]
    bkb = [[1, 5, 1], [1, -5, -1], [1, 1, 1], [0, -6, -1], [0, 6, 1]]
    return cdk, vsg, vpk, bdk, bkb


def _run_examples():
    cdk, vsg, vpk, bdk, bkb = _example_inputs()
    pop1 = comm(cdk, vsg)
    pop3 = comm(bdk, vsg)
    pop5 = comm(bkb, vpk)

    print("")
    print("####### RESULTADO #######")
    print("")
    print(render_result(pop1))
    print(render_result(pop3))
    print(render_result(pop5))
    print("")
    print("#########################")
    print("")


def _run_self_tests():
    assert delta([1, 2, 1], [0, -3, -1]) == [[2, -3], [1, -1]]

    result = comm([[1, 3, 1]], [[0, 3, 1]])
    assert result == [[[1]], [[]], [[]]]

    result = comm(
        [[1, 1, 1], [0, 4, 1]],
        [[0, 2, GENERIC_SPIN], [1, 9, GENERIC_SPIN], [1, 7, 1]],
    )
    assert result == [
        [[1], [1], [-1]],
        [
            [[1, 9, GENERIC_SPIN], [1, 7, 1], [0, 4, 1]],
            [[1, 1, 1], [0, 2, GENERIC_SPIN], [1, 7, 1]],
            [[1, 1, 1], [0, 2, GENERIC_SPIN], [1, 9, GENERIC_SPIN]],
        ],
        [
            [[1, 2], [1, GENERIC_SPIN]],
            [[4, 9], [1, GENERIC_SPIN]],
            [[4, 7], [1, 1]],
        ],
    ]

    cdk, vsg, vpk, bdk, bkb = _example_inputs()
    rendered = "\n".join(
        [
            render_result(comm(cdk, vsg)),
            render_result(comm(bdk, vsg)),
            render_result(comm(bkb, vpk)),
        ]
    )
    expected = "\n".join(
        [
            "[-1], [[+1, +2, s]], [[+1, +2], [+1, s]]",
            "[-1], [[+1, +2, s], [+1, -4, -1], [+0, -1, -1]], [[+4, +2], [+1, s]]",
            "[-1], [[+1, +4, +1], [+1, +2, s], [+0, -1, -1]], [[-4, +2], [-1, s]]",
            "[+1], [[+1, +4, +1], [+1, -4, -1], [+0, +2, s]], [[-1, +2], [-1, s]]",
            "[-1], [[+1, +2, +1], [+1, -2, -1], [+0, -3, -1], [+1, -5, -1], [+1, +1, +1], [+0, -6, -1], [+0, +6, +1]], [[+5, +3], [+1, +1]]",
            "[+1], [[+1, +5, +1], [+1, +2, +1], [+1, -2, -1], [+0, +3, +1], [+1, +1, +1], [+0, -6, -1], [+0, +6, +1]], [[-5, -3], [-1, -1]]",
            "[-1], [[+1, +5, +1], [+1, -5, -1], [+1, +2, +1], [+1, -2, -1], [+0, -3, -1], [+0, -6, -1], [+0, +6, +1]], [[+1, +3], [+1, +1]]",
            "[-1], [[+1, +5, +1], [+1, -5, -1], [+1, +1, +1], [+1, +2, +1], [+0, -3, -1], [+0, +3, +1], [+0, +6, +1]], [[-6, -2], [-1, -1]]",
            "[+1], [[+1, +5, +1], [+1, -5, -1], [+1, +1, +1], [+0, -6, -1], [+1, -2, -1], [+0, -3, -1], [+0, +3, +1]], [[+6, +2], [+1, +1]]",
        ]
    )
    assert rendered == expected


if __name__ == "__main__":
    _run_self_tests()
    _run_examples()
