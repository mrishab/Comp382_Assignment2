"""
demo.py - Comprehensive test suite for all matcher functions
Tests against the exact language definitions from pda_configs.json

"""

from comp382_assignment_2.matchers import *


def print_header(title):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_result(func_name, input_str, result, expected=None):
    if expected is not None:
        status = "+" if result == expected else "x"
        print(f"  {status} {func_name:25}('{input_str}') = '{result:12}' (expected '{expected}')")
    else:
        print(f"     {func_name:25}('{input_str}') = '{result}'")


def test_cfl_functions():
    """Test the 3 base CFL functions (C1, C2, C3)"""
    print_header("1. BASE CFL FUNCTIONS")

    # C1: a^n b^n
    print("\n  C1: an_bn (aⁿbⁿ)")
    for s, desc, expected in [
        ("ab",     "n=1",         "ab"),
        ("aabb",   "n=2",         "aabb"),
        ("aaabbb", "n=3",         "aaabbb"),
        ("aaa",    "only a's",    ""),
        ("bbb",    "only b's",    ""),
        ("ba",     "wrong order", ""),
        ("",       "empty",       ""),
    ]:
        print_result("  an_bn", s, an_bn(s), expected)

    # C2: a b^n a
    print("\n  C2: a_bn_a (ab^na)")
    for s, desc, expected in [
        ("aa",    "n=0",             "aa"),
        ("aba",   "n=1",             "aba"),
        ("abba",  "n=2",             "abba"),
        ("abbba", "n=3",             "abbba"),
        ("a",     "single a",        ""),
        ("ab",    "missing final a", ""),
        ("ba",    "starts with b",   ""),
        ("",      "empty",           ""),
    ]:
        print_result("  a_bn_a", s, a_bn_a(s), expected)

    # C3: b^n
    print("\n  C3: bn (bⁿ)")
    for s, desc, expected in [
        ("b",   "n=1",    "b"),
        ("bb",  "n=2",    "bb"),
        ("bbb", "n=3",    "bbb"),
        ("ab",  "has a",  "b"),
        ("a",   "only a", ""),
        ("",    "empty",  ""),
    ]:
        print_result("  bn", s, bn(s), expected)


def test_regular_functions():
    """Test the 3 regular language functions (R1, R2, R3)"""
    print_header("2. REGULAR LANGUAGE FUNCTIONS")

    print("\n  R1: a*b* (any a's followed by any b's)")
    for s, desc, expected in [
        ("",       "empty",        ""),
        ("a",      "single a",     "a"),
        ("b",      "single b",     "b"),
        ("ab",     "a then b",     "ab"),
        ("aaab",   "a's then b",   "aaab"),
        ("abbb",   "a then b's",   "abbb"),
        ("aaabbb", "a's then b's", "aaabbb"),
        ("ba",     "b then a",     "b"),
    ]:
        print_result("  a*b*", s, regex_a_star_b_star_matcher(s), expected)

    print("\n  R2: ab*a (a, then any b's, then a)")
    for s, desc, expected in [
        ("aa",    "n=0",             "aa"),
        ("aba",   "n=1",             "aba"),
        ("abba",  "n=2",             "abba"),
        ("abbba", "n=3",             "abbba"),
        ("a",     "single a",        ""),
        ("ab",    "missing final a", ""),
        ("ba",    "starts with b",   ""),
    ]:
        print_result("  ab*a", s, regex_a_b_star_a_matcher(s), expected)

    print("\n  R3: a* (any number of a's)")
    for s, desc, expected in [
        ("",    "empty",  ""),
        ("a",   "single", "a"),
        ("aa",  "double", "aa"),
        ("aaa", "triple", "aaa"),
        ("b",   "only b", ""),
        ("aba", "mixed",  "a"),
    ]:
        print_result("  a*", s, regex_a_star_matcher(s), expected)


def test_intersection_languages():
    """Test all 9 intersections"""
    print_header("3. INTERSECTION LANGUAGES")

    print("\n  R1∩C1 = aⁿbⁿ")
    for s, expected in [("ab","ab"), ("aabb","aabb"), ("aaabbb","aaabbb"), ("aaa",""), ("bbb","")]:
        print_result("  R1∩C1", s, intersect_r1_c1(s), expected)

    print("\n  R2∩C1 = ∅  (ab*a ends in 'a', aⁿbⁿ ends in 'b')")
    for s, expected in [("ab",""), ("aabb",""), ("aa",""), ("aba",""), ("abba","")]:
        print_result("  R2∩C1", s, intersect_r2_c1(s), expected)

    print("\n  R3∩C1 = ∅  (a* has no b's, aⁿbⁿ requires b's)")
    for s, expected in [("a",""), ("aa",""), ("aaa",""), ("ab",""), ("aabb","")]:
        print_result("  R3∩C1", s, intersect_r3_c1(s), expected)

    print("\n  R1∩C2 = {aa}")
    for s, expected in [("aa","aa"), ("aaa","aa"), ("a",""), ("ab",""), ("aba",""), ("abba","")]:
        print_result("  R1∩C2", s, intersect_r1_c2(s), expected)

    print("\n  R2∩C2 = ab^n a")
    for s, expected in [("aa","aa"), ("aba","aba"), ("abba","abba"), ("abbba","abbba"), ("a",""), ("ab","")]:
        print_result("  R2∩C2", s, intersect_r2_c2(s), expected)

    print("\n  R3∩C2 = {aa}")
    for s, expected in [("aa","aa"), ("aaa","aa"), ("a",""), ("aba",""), ("ab","")]:
        print_result("  R3∩C2", s, intersect_r3_c2(s), expected)

    print("\n  R1∩C3 = bⁿ")
    for s, expected in [("b","b"), ("bb","bb"), ("bbb","bbb"), ("ab","b"), ("a","")]:
        print_result("  R1∩C3", s, intersect_r1_c3(s), expected)

    print("\n  R2∩C3 = ∅  (ab*a ends in 'a', bⁿ has only b's)")
    for s, expected in [("b",""), ("bb",""), ("bbb",""), ("ab",""), ("aba","")]:
        print_result("  R2∩C3", s, intersect_r2_c3(s), expected)

    print("\n  R3∩C3 = ∅  (a* has only a's, bⁿ has only b's)")
    for s, expected in [("a",""), ("b",""), ("ab",""), ("aabb",""), ("","")]:
        print_result("  R3∩C3", s, intersect_r3_c3(s), expected)


def test_super_pda():
    """Test super_accept for all 9 combinations"""
    print_header("4. SUPER PDA (entire string match)")

    print("\n  R1∩C1 (aⁿbⁿ) — default:")
    for s, expected in [
        ("",         "unmatched"),
        ("ab",       "matched"),
        ("aabb",     "matched"),
        ("aaabbb",   "matched"),
        ("aaaabbbb", "matched"),
        ("aba",      "unmatched"),
        ("aab",      "unmatched"),
        ("abb",      "unmatched"),
        ("a",        "unmatched"),
        ("b",        "unmatched"),
    ]:
        print_result("super_accept", s, super_accept(s), expected)

    print("\n  R2∩C1 (∅ — always unmatched):")
    for s, expected in [("ab","unmatched"), ("aabb","unmatched"), ("aba","unmatched"), ("abba","unmatched")]:
        print_result("super_accept r2,c1", s, super_accept(s, "r2", "c1"), expected)

    print("\n  R3∩C1 (∅ — always unmatched):")
    for s, expected in [("a","unmatched"), ("aa","unmatched"), ("aaa","unmatched"), ("ab","unmatched")]:
        print_result("super_accept r3,c1", s, super_accept(s, "r3", "c1"), expected)

    print("\n  R1∩C2 ({aa}):")
    for s, expected in [
        ("aa",   "matched"),
        ("a",    "unmatched"),
        ("aaa",  "unmatched"),
        ("ab",   "unmatched"),
        ("aba",  "unmatched"),
        ("abba", "unmatched"),
    ]:
        print_result("super_accept r1,c2", s, super_accept(s, "r1", "c2"), expected)

    print("\n  R2∩C2 (ab^n a):")
    for s, expected in [
        ("aa",    "matched"),
        ("aba",   "matched"),
        ("abba",  "matched"),
        ("abbba", "matched"),
        ("a",     "unmatched"),
        ("ab",    "unmatched"),
        ("aabb",  "unmatched"),
    ]:
        print_result("super_accept r2,c2", s, super_accept(s, "r2", "c2"), expected)

    print("\n  R3∩C2 ({aa}):")
    for s, expected in [
        ("aa",  "matched"),
        ("a",   "unmatched"),
        ("aaa", "unmatched"),
        ("aba", "unmatched"),
    ]:
        print_result("super_accept r3,c2", s, super_accept(s, "r3", "c2"), expected)

    print("\n  R1∩C3 (bⁿ):")
    for s, expected in [
        ("b",   "matched"),
        ("bb",  "matched"),
        ("bbb", "matched"),
        ("ab",  "unmatched"),
        ("a",   "unmatched"),
    ]:
        print_result("super_accept r1,c3", s, super_accept(s, "r1", "c3"), expected)

    print("\n  R2∩C3 (∅ — always unmatched):")
    for s, expected in [("b","unmatched"), ("bb","unmatched"), ("aba","unmatched"), ("ab","unmatched")]:
        print_result("super_accept r2,c3", s, super_accept(s, "r2", "c3"), expected)

    print("\n  R3∩C3 (∅ — always unmatched):")
    for s, expected in [("a","unmatched"), ("b","unmatched"), ("ab","unmatched"), ("aabb","unmatched")]:
        print_result("super_accept r3,c3", s, super_accept(s, "r3", "c3"), expected)


def test_mixed_string():
    """Test all functions on a complex string"""
    print_header("5. ALL FUNCTIONS ON COMPLEX STRING")

    test_str = "aaababbabba"
    print(f"\n  Test string: '{test_str}'")
    print("  " + "-" * 50)

    functions = [
        ("an_bn (C1)",   an_bn,                       "aⁿbⁿ"),
        ("a_bn_a (C2)",  a_bn_a,                      "ab^na"),
        ("bn (C3)",      bn,                          "bⁿ"),
        ("a*b* (R1)",    regex_a_star_b_star_matcher, "R1"),
        ("ab*a (R2)",    regex_a_b_star_a_matcher,    "R2"),
        ("a* (R3)",      regex_a_star_matcher,        "R3"),
        ("R1∩C1",        intersect_r1_c1,             "aⁿbⁿ"),
        ("R2∩C1",        intersect_r2_c1,             "∅"),
        ("R3∩C1",        intersect_r3_c1,             "∅"),
        ("R1∩C2",        intersect_r1_c2,             "{aa}"),
        ("R2∩C2",        intersect_r2_c2,             "ab^na"),
        ("R3∩C2",        intersect_r3_c2,             "{aa}"),
        ("R1∩C3",        intersect_r1_c3,             "bⁿ"),
        ("R2∩C3",        intersect_r2_c3,             "∅"),
        ("R3∩C3",        intersect_r3_c3,             "∅"),
        ("super(r1,c1)", lambda s: super_accept(s),              "aⁿbⁿ"),
        ("super(r1,c2)", lambda s: super_accept(s, "r1", "c2"), "{aa}"),
        ("super(r2,c2)", lambda s: super_accept(s, "r2", "c2"), "ab^na"),
        ("super(r3,c2)", lambda s: super_accept(s, "r3", "c2"), "{aa}"),
        ("super(r1,c3)", lambda s: super_accept(s, "r1", "c3"), "bⁿ"),
    ]

    for name, func, desc in functions:
        result = func(test_str)
        print(f"  {name:20} ({desc:10}): '{result}'")

def main():
    print("\n" + "*" * 70)
    print("*  MATCHERS TEST")
    print("*" * 70)

    test_cfl_functions()
    test_regular_functions()
    test_intersection_languages()
    test_super_pda()
    test_mixed_string()

    print("\n" + "=" * 70)
    print(" TESTING COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()