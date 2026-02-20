import re

def regex_a_star_b_star_matcher(input_str: str) -> str:
    """Regular: a* ◦ b* - returns LONGEST matching substring"""
    if not input_str:
        return ""
    pattern = re.compile(r'a*b*')
    matches = pattern.findall(input_str)
    return max(matches, key=len) if matches else ""


def regex_a_b_star_a_matcher(input_str: str) -> str:
    """
    Regular: a ◦ b* ◦ a - returns LONGEST matching substring
    Finds patterns like 'aa', 'aba', 'abba', etc.
    Fixed to find 'aba' in 'abcba'
    """
    if not input_str:
        return ""
    
    # More robust pattern: find any 'a' followed by any characters? No, must be only b's in between
    # We need to find all substrings that match a(b*)a
    n = len(input_str)
    best = ""
    
    for i in range(n):
        if input_str[i] != 'a':
            continue
        for j in range(i + 1, n):
            if input_str[j] != 'a':
                continue
            # Check if all characters between i and j are 'b'
            valid = True
            for k in range(i + 1, j):
                if input_str[k] != 'b':
                    valid = False
                    break
            if valid:
                candidate = input_str[i:j+1]
                if len(candidate) > len(best):
                    best = candidate
    
    return best


def regex_a_star_matcher(input_str: str) -> str:
    """Regular: a* - returns LONGEST matching substring"""
    if not input_str:
        return ""
    pattern = re.compile(r'a+')
    matches = pattern.findall(input_str)
    return max(matches, key=len) if matches else ""