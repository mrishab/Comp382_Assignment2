from enum import Enum

class RegexSamples(Enum):
    STAR_A = ("a*", "desc_star_a")
    CONCAT_AB = ("a◦b", "desc_concat_ab")
    UNION_AB = ("a ∪ b", "desc_union_ab")
    STAR_AB_GROUP = ("(a◦b)*", "desc_star_ab_group")
    STAR_A_STAR_B = ("a*◦b*", "desc_star_a_star_b")
    UNIVERSAL_AB = ("(a ∪ b)*", "desc_universal_ab")
    EXACT_BAB = ("b◦a◦b", "desc_exact_bab")
    UNION_A_EPSILON = ("a ∪ ε", "desc_union_a_epsilon")

    def __init__(self, pattern, description_key):
        self.pattern = pattern
        self.description_key = description_key
