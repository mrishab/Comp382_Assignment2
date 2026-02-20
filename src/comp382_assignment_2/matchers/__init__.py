"""
Matchers package for COMP 382 Assignment 2.
Provides functions for CFL, Regular, and Intersection language matching.

"""

from comp382_assignment_2.matchers.child_languages import (
    an_bn,
    a_bn_a,
    bn
)

from comp382_assignment_2.matchers.regular_languages import (
    regex_a_star_b_star_matcher,
    regex_a_b_star_a_matcher,
    regex_a_star_matcher
)

from comp382_assignment_2.matchers.intersection_matchers import (
    intersect_r1_c1,  # aⁿbⁿ
    intersect_r2_c1,  # ∅
    intersect_r3_c1,  # ∅
    intersect_r1_c2,  # {aa}
    intersect_r2_c2,  # ab^na
    intersect_r3_c2,  # {aa}
    intersect_r1_c3,  # bⁿ
    intersect_r2_c3,  # ∅
    intersect_r3_c3   # ∅
)

from comp382_assignment_2.matchers.super_pda import super_accept

__all__ = [
    # 3 CFL functions (C1, C2, C3)
    'an_bn',
    'a_bn_a',
    'bn',

    # 3 Regular functions (R1, R2, R3)
    'regex_a_star_b_star_matcher',
    'regex_a_b_star_a_matcher',
    'regex_a_star_matcher',

    # 9 Intersection functions
    'intersect_r1_c1',
    'intersect_r2_c1',
    'intersect_r3_c1',
    'intersect_r1_c2',
    'intersect_r2_c2',
    'intersect_r3_c2',
    'intersect_r1_c3',
    'intersect_r2_c3',
    'intersect_r3_c3',

    # Special function
    'super_accept'
]