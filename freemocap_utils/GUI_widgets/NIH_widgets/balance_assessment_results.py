from dataclasses import dataclass
from typing import Any, Dict, Optional

from matplotlib.figure import Figure

@dataclass
class BalanceAssessmentResults:
    path_length_dictionary: Dict[str, Any]
    velocity_dictionary: Dict[str, Any]
    path_length_figure: Optional[Figure] = None