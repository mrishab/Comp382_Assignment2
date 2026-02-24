from dataclasses import dataclass

from comp382_assignment_2.super_pda.base import BaseSuperPDA


@dataclass
class ContentPanelModel:
    reg_key: str | None = None
    cfl_key: str | None = None
    pda_config_key: str | None = None
    super_definition: BaseSuperPDA | None = None
