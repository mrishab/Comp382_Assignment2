from comp382_assignment_2.super_pda.base import BaseSuperPDA
from comp382_assignment_2.super_pda.implementations import (
    AABNASuperPDA,
    AASuperPDA,
    AnBnSuperPDA,
    BnSuperPDA,
    EmptySuperPDA,
)

_SUPER_PDA_MAP: dict[str, type[BaseSuperPDA]] = {
    "an_bn": AnBnSuperPDA,
    "aa": AASuperPDA,
    "a_bn_a": AABNASuperPDA,
    "bn": BnSuperPDA,
    "empty": EmptySuperPDA,
}


def get_super_pda(key: str) -> BaseSuperPDA:
    cls = _SUPER_PDA_MAP.get(key)
    if cls is None:
        raise KeyError(f"Unknown SuperPDA '{key}'. Available: {list(_SUPER_PDA_MAP)}")
    return cls()


def list_super_pda_keys() -> list[str]:
    return list(_SUPER_PDA_MAP)
