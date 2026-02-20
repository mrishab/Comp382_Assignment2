"""
Intersection matchers
All functions return LONGEST matching substrings.

"""

from comp382_assignment_2.pda.pda_loader import load_pda
from comp382_assignment_2.matchers.substring_utils import find_longest_matching_substring
from comp382_assignment_2.matchers.child_languages import (
    _check_pda_accept,
    an_bn,
    a_bn_a,
    bn
)


# Only need to load PDAs not already covered by child language functions
L_aa_pda  = load_pda("aa")     # {aa}  — R1∩C2 and R3∩C2
L_emp_pda = load_pda("empty")  # ∅     — R2∩C1, R2∩C3, R3∩C1, R3∩C3


def _match_language(pda, input_str: str) -> str:
    """Find the LONGEST substring accepted by PDA"""
    return find_longest_matching_substring(input_str, lambda s: _check_pda_accept(pda, s))


def intersect_r1_c1(input_str: str) -> str:
    """R1 (a*b*) ∩ C1 (aⁿbⁿ) = aⁿbⁿ"""
    return an_bn(input_str)


def intersect_r2_c1(input_str: str) -> str:
    """R2 (ab*a) ∩ C1 (aⁿbⁿ) = ∅  — R2 ends in 'a', C1 ends in 'b'"""
    return _match_language(L_emp_pda, input_str)


def intersect_r3_c1(input_str: str) -> str:
    """R3 (a*) ∩ C1 (aⁿbⁿ) = ∅  — R3 has no b's, C1 requires b's"""
    return _match_language(L_emp_pda, input_str)


def intersect_r1_c2(input_str: str) -> str:
    """R1 (a*b*) ∩ C2 (ab^na) = {aa}  — R1 can only end in 'a' with no b's, so only 'aa'"""
    return _match_language(L_aa_pda, input_str)


def intersect_r2_c2(input_str: str) -> str:
    """R2 (ab*a) ∩ C2 (ab^na) = ab^na"""
    return a_bn_a(input_str)


def intersect_r3_c2(input_str: str) -> str:
    """R3 (a*) ∩ C2 (ab^na) = {aa}  — R3 has no b's, so only 'aa' satisfies C2"""
    return _match_language(L_aa_pda, input_str)


def intersect_r1_c3(input_str: str) -> str:
    """R1 (a*b*) ∩ C3 (bⁿ) = bⁿ"""
    return bn(input_str)


def intersect_r2_c3(input_str: str) -> str:
    """R2 (ab*a) ∩ C3 (bⁿ) = ∅  — R2 ends in 'a', C3 has only b's"""
    return _match_language(L_emp_pda, input_str)


def intersect_r3_c3(input_str: str) -> str:
    """R3 (a*) ∩ C3 (bⁿ) = ∅  — R3 has only a's, C3 has only b's"""
    return _match_language(L_emp_pda, input_str)