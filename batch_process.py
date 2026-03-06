"""
Batch Path Length Analysis
==========================
Runs the balance/path-length analysis for every tracker subfolder under
a session's `validation/` directory, reusing the frame intervals that were
already established for Qualisys.

Usage
-----
    python batch_path_length_analysis.py /path/to/session_folder

Or import and call from another script:
    from batch_path_length_analysis import run_batch_analysis
    run_batch_analysis(session_folder_path)
"""

from pathlib import Path
import argparse
import datetime
import json
import logging

import numpy as np
import pandas as pd
from skellymodels.managers.human import Human

from gui.analysis.path_length_calculator import PathLengthCalculator

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_latest_qualisys_analysis(session_folder: Path) -> dict:
    """
    Look inside  session/validation/qualisys/path_length_analysis/
    for the most recent `analysis_*` folder and return the parsed
    condition_data.json (which contains 'Frame Intervals').
    """
    qualisys_analysis_root = session_folder / "validation" / "qualisys" / "path_length_analysis"

    if not qualisys_analysis_root.exists():
        raise FileNotFoundError(
            f"Could not find qualisys path_length_analysis folder at: {qualisys_analysis_root}"
        )

    analysis_folders = sorted(
        [f for f in qualisys_analysis_root.iterdir() if f.is_dir() and f.name.startswith("analysis_")],
        key=lambda p: p.name,
    )

    if not analysis_folders:
        raise FileNotFoundError(
            f"No analysis_* folders found in {qualisys_analysis_root}"
        )

    latest_folder = analysis_folders[-1]
    json_path = latest_folder / "condition_data.json"

    if not json_path.exists():
        raise FileNotFoundError(f"condition_data.json not found in {latest_folder}")

    with open(json_path, "r") as f:
        data = json.load(f)

    logger.info(f"Loaded frame intervals from: {json_path}")
    return data


def load_com_data(tracker_folder: Path) -> np.ndarray:
    """
    Use skellymodels Human to load the parquet data for a tracker,
    calculate derived quantities, and return the total-body COM array.
    """
    human:Human = Human.from_data(tracker_folder)
    if human.body.total_body_com is None:
        human.calculate()
    com_data = human.body.total_body_com.as_array
    logger.info(f"  Loaded COM data with shape {com_data.shape} from {tracker_folder.name}")
    return com_data


def run_analysis_for_tracker(
    com_data: np.ndarray,
    condition_frame_dict: dict,
    sampling_rate: float,
) -> dict:
    """
    Run path length, velocity, and position calculations for one tracker.

    Returns a dict with keys:
        'path_lengths', 'velocities', 'positions'
    """
    calculator = PathLengthCalculator(com_data, sampling_rate=sampling_rate)

    path_length_dict = {}
    velocity_dict = {}
    position_dict = {}

    for condition, frames in condition_frame_dict.items():
        frame_range = range(frames[0], frames[1])

        # Path length (normalized by duration)
        path_length_dict[condition] = calculator.get_path_length(frame_range)

        # Velocity
        vel = calculator.calculate_velocity(frame_range)
        vel = np.squeeze(vel, axis=1)  # (n_frames, 3)
        velocity_dict[condition] = [vel[:, 0], vel[:, 1], vel[:, 2]]

        # Position
        start_frame, end_frame = frames
        position_data = [com_data[start_frame:end_frame, 0, i] for i in range(3)]
        position_dict[condition] = position_data

    return {
        "path_lengths": path_length_dict,
        "velocities": velocity_dict,
        "positions": position_dict,
    }


def create_dataframe_from_dict(data_dict: dict) -> pd.DataFrame:
    """Convert a {condition: [x_arr, y_arr, z_arr]} dict to a DataFrame."""
    dataframes = []
    for condition, arrays in data_dict.items():
        arrays = np.squeeze(arrays)
        for dimension, arr in zip(["x", "y", "z"], arrays):
            temp_df = pd.DataFrame({f"{condition}_{dimension}": arr})
            dataframes.append(temp_df)

    result_df = pd.concat(dataframes, axis=1)
    result_df["Frame"] = np.arange(len(result_df))
    return result_df


def save_results(
    tracker_folder: Path,
    condition_frame_dict: dict,
    results: dict,
    folder_name: str,
):
    """
    Save path length results, velocity CSV, and position CSV
    into tracker_folder/path_length_analysis/<folder_name>/
    """
    save_path = tracker_folder / "path_length_analysis" / folder_name
    save_path.mkdir(parents=True, exist_ok=True)

    # condition_data.json  (matches GUI format)
    condition_data = {
        "Frame Intervals": condition_frame_dict,
        "Path Lengths:": results["path_lengths"],
    }
    with open(save_path / "condition_data.json", "w") as f:
        json.dump(condition_data, f, indent=1)

    # Velocity CSV
    vel_df = create_dataframe_from_dict(results["velocities"])
    vel_df.to_csv(save_path / "condition_velocities.csv", index=False)

    # Position CSV
    pos_df = create_dataframe_from_dict(results["positions"])
    pos_df.to_csv(save_path / "condition_positions.csv", index=False)

    logger.info(f"  Saved results to: {save_path}")


# ---------------------------------------------------------------------------
# Main batch runner
# ---------------------------------------------------------------------------

def run_batch_analysis(
    session_folder: str | Path,
    sampling_rate: float = 30.0,
    skip_qualisys: bool = False,
):
    """
    Run path-length analysis for every tracker under session/validation/,
    using the frame intervals from the latest qualisys analysis.

    Parameters
    ----------
    session_folder : path to the top-level session directory
    sampling_rate  : capture rate in Hz (default 30)
    skip_qualisys  : if True, skip re-running qualisys (since it already has results)
    """
    session_folder = Path(session_folder)
    validation_folder = session_folder / "validation"

    if not validation_folder.exists():
        raise FileNotFoundError(f"No validation folder found at {validation_folder}")

    # 1. Load the frame intervals from the latest qualisys analysis
    qualisys_data = find_latest_qualisys_analysis(session_folder)
    condition_frame_dict = qualisys_data["Frame Intervals"]

    logger.info(f"Frame intervals: {json.dumps(condition_frame_dict, indent=2)}")

    # 2. Discover all tracker folders
    tracker_folders = sorted([
        f for f in validation_folder.iterdir()
        if f.is_dir() and any(f.glob("*.parquet"))
    ])

    if not tracker_folders:
        raise FileNotFoundError(f"No tracker folders with parquet files found in {validation_folder}")

    logger.info(f"Found {len(tracker_folders)} tracker(s): {[f.name for f in tracker_folders]}")

    # 3. Timestamp for this batch run
    timestamp = datetime.datetime.now().strftime("analysis_%Y-%m-%d_%H_%M_%S")

    # 4. Process each tracker
    for tracker_folder in tracker_folders:
        if skip_qualisys and tracker_folder.name == "qualisys":
            logger.info(f"Skipping {tracker_folder.name} (already has results)")
            continue

        logger.info(f"Processing: {tracker_folder.name}")

        try:
            com_data = load_com_data(tracker_folder)
            results = run_analysis_for_tracker(com_data, condition_frame_dict, sampling_rate)
            save_results(tracker_folder, condition_frame_dict, results, timestamp)
        except Exception as e:
            logger.error(f"  Failed on {tracker_folder.name}: {e}")
            continue

    logger.info("Batch analysis complete.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    session_folder_list = [
        r"D:\validation\data\2025_07_31_JSM_pilot\freemocap\2025-07-31_16-00-42_GMT-4_jsm_nih_trial_1",
        r"D:\validation\data\2025_07_31_JSM_pilot\freemocap\2025-07-31_16-16-23_GMT-4_jsm_nih_trial_2",
        r"D:\validation\data\2025_09_03_OKK\freemocap\2025-09-03_14-24-21_GMT-4_okk_nih_1",
        r"D:\validation\data\2025_09_03_OKK\freemocap\2025-09-03_14-38-45_GMT-4_okk_nih_2",
        r"D:\validation\data\2025-11-04_ATC\2025-11-04_15-02-28_GMT-5_atc_nih_1",
        r"D:\validation\data\2025-11-04_ATC\2025-11-04_15-18-21_GMT-5_atc_nih_2",
        r"D:\validation\data\2026_01_26_KK\2026-01-16_13-41-17_GMT-5_kk_nih_1",
        r"D:\validation\data\2026_01_26_KK\2026-01-16_13-58-41_GMT-5_kk_nih_2",
        r"D:\validation\data\2026-01-30-JTM\2026-01-30_10-40-03_GMT-5_JTM_nih_1",
        r"D:\validation\data\2026-01-30-JTM\2026-01-30_10-57-13_GMT-5_JTM_nih_2"
    ]
    for session_folder in session_folder_list:
        run_batch_analysis(Path(session_folder), sampling_rate=30.0, skip_qualisys=False)
