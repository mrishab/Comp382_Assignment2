"""
Super PDA function - checks if the ENTIRE string matches an intersection language.
Returns "matched" or "unmatched".

"""

from comp382_assignment_2.matchers.intersection_matchers import (
    intersect_r1_c1, intersect_r2_c1, intersect_r3_c1,
    intersect_r1_c2, intersect_r2_c2, intersect_r3_c2,
    intersect_r1_c3, intersect_r2_c3, intersect_r3_c3
)

_INTERSECTION_MAP = {
    ("r1", "c1"): intersect_r1_c1,  # aⁿbⁿ
    ("r2", "c1"): intersect_r2_c1,  # ∅
    ("r3", "c1"): intersect_r3_c1,  # ∅
    ("r1", "c2"): intersect_r1_c2,  # {aa}
    ("r2", "c2"): intersect_r2_c2,  # ab^na
    ("r3", "c2"): intersect_r3_c2,  # {aa}
    ("r1", "c3"): intersect_r1_c3,  # bⁿ
    ("r2", "c3"): intersect_r2_c3,  # ∅
    ("r3", "c3"): intersect_r3_c3,  # ∅
}


def super_accept(input_str: str, regular: str = "r1", cfl: str = "c1") -> str:
    """
    Checks if ENTIRE string matches the intersection of selected languages.
    Returns "matched" or "unmatched".

    Args:
        input_str: The string to test
        regular: "r1" (a*b*), "r2" (ab*a), "r3" (a*)
        cfl:     "c1" (aⁿbⁿ),  "c2" (ab^na), "c3" (bⁿ)

    Default (r1, c1) = aⁿbⁿ
    """
    if input_str == "":
        return "unmatched"

    func = _INTERSECTION_MAP.get((regular.lower(), cfl.lower()))
    if func is None:
        return "unmatched"

    result = func(input_str)
    return "matched" if result == input_str else "unmatched"