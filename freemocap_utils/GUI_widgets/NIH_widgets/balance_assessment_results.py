from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class BalanceAssessmentResults:
    path_length_dictionary: Dict[str, Any]
    velocity_dictionary: Dict[str, Any]