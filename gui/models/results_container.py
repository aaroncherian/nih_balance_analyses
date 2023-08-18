from dataclasses import dataclass
from typing import Any, Dict, Optional

from matplotlib.figure import Figure
import numpy as np

@dataclass
class BalanceAssessmentResultsContainer:
    condition_frame_dictionary: Dict[str, Any]
    path_length_dictionary: Dict[str, Any]
    velocity_dictionary: Dict[str, Any]
    postion_dictionary: Dict[str,Any]
    center_of_mass_xyz: np.ndarray
    path_length_figure: Optional[Figure] = None
    position_and_velocity_figure: Optional[Figure] = None