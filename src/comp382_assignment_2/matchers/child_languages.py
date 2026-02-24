"""
CFL matchers — the 3 base context-free languages used in this assignment.
Each function returns the LONGEST matching substring.

C1: a^n b^n  (an_bn)
C2: a b^n a  (a_bn_a)
C3: b^n      (bn)
"""

from comp382_assignment_2.pda.pda_loader import load_pda
from comp382_assignment_2.matchers.substring_utils import find_longest_matching_substring


def check_pda_accept(pda, input_str: str) -> bool:
    """
    Helper function to check if a PDA accepts a string.
    Uses BFS to handle nondeterminism.
    """
    from collections import deque

    initial = (pda.initial_state, 0, (pda.initial_stack_symbol,))
    queue = deque([initial])
    visited = set()

    while queue:
        state, idx, stack_tuple = queue.popleft()
        stack = list(stack_tuple)

        if idx == len(input_str) and state in pda.final_states:
            return True

        symbol = input_str[idx] if idx < len(input_str) else None
        stack_top = stack[-1] if stack else None

        possible_transitions = []

        if (state, symbol, stack_top) in pda.transitions:
            possible_transitions.extend(pda.transitions[(state, symbol, stack_top)])
        if (state, None, stack_top) in pda.transitions:
            possible_transitions.extend(pda.transitions[(state, None, stack_top)])
        if (state, symbol, None) in pda.transitions:
            possible_transitions.extend(pda.transitions[(state, symbol, None)])
        if (state, None, None) in pda.transitions:
            possible_transitions.extend(pda.transitions[(state, None, None)])

        for next_state, push_list in possible_transitions:
            new_stack = stack.copy()

            if stack_top is not None:
                new_stack.pop()

            for sym in reversed(push_list):
                if sym:
                    new_stack.append(sym)

            new_idx = idx + 1 if symbol is not None and (state, symbol, stack_top) in pda.transitions else idx

            config = (next_state, new_idx, tuple(new_stack))
            if config not in visited and new_idx <= len(input_str):
                visited.add(config)
                queue.append(config)

    return False


def an_bn(input_str: str) -> str:
    """
    C1: a^n b^n (equal number of a's followed by b's), n>=1
    Returns LONGEST matching substring.
    Example: "ab", "aabb", "aaabbb"
    """
    pda = load_pda("an_bn")
    return find_longest_matching_substring(input_str, lambda s: check_pda_accept(pda, s))


def a_bn_a(input_str: str) -> str:
    """
    C2: a b^n a (one a, zero or more b's, one a), n>=0
    Returns LONGEST matching substring.
    Example: "aa", "aba", "abba", "abbba"
    """
    pda = load_pda("a_bn_a")
    return find_longest_matching_substring(input_str, lambda s: check_pda_accept(pda, s))


def bn(input_str: str) -> str:
    """
    C3: b^n (one or more b's), n>=1
    Returns LONGEST matching substring.
    Example: "b", "bb", "bbb"
    """
    pda = load_pda("bn")
    return find_longest_matching_substring(input_str, lambda s: check_pda_accept(pda, s))