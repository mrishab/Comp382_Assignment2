"""
Utility functions for finding substrings that match language predicates.

"""

def find_longest_matching_substring(input_str: str, accept_func) -> str:
    """
    Find the LONGEST substring that satisfies accept_func.
    This is the primary function used by all matchers.
    
    Args:
        input_str: The string to search within
        accept_func: A function that takes a string and returns bool
        
    Returns:
        The longest matching substring found, or empty string if none found
    """
    n = len(input_str)
    
    # Try longest substrings first
    for length in range(n, 0, -1):
        for start in range(n - length + 1):
            candidate = input_str[start:start + length]
            if accept_func(candidate):
                return candidate
    
    return ""


def find_shortest_matching_substring(input_str: str, accept_func) -> str:
    """
    Find the SHORTEST substring that satisfies accept_func.
    Kept for compatibility if needed.
    """
    n = len(input_str)
    
    for length in range(1, n + 1):
        for start in range(n - length + 1):
            candidate = input_str[start:start + length]
            if accept_func(candidate):
                return candidate
    
    return ""


def find_all_matching_substrings(input_str: str, accept_func) -> list:
    """
    Find all substrings that satisfy accept_func.
    Returns list of (substring, start, end) tuples.
    """
    n = len(input_str)
    matches = []
    
    for length in range(1, n + 1):
        for start in range(n - length + 1):
            candidate = input_str[start:start + length]
            if accept_func(candidate):
                matches.append((candidate, start, start + length))
    
    return matches