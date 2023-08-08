import threading
from freemocap_utils.GUI_widgets.NIH_widgets.path_length_tools import PathLengthCalculator
import numpy as np


class BalanceAssessmentWorkerThread(threading.Thread):
    def __init__(self, 
                 com_data: np.ndarray, 
                 condition_frames_dictionary: dict, 
                 task_list: list,
                 task_running_callback=None, 
                 task_completed_callback=None, 
                 all_tasks_finished_callback=None):
        super().__init__()

        # Data and parameters
        self.com_data = com_data
        self.condition_frames_dictionary = condition_frames_dictionary
        self.path_length_calculator = PathLengthCalculator.PathLengthCalculator(self.com_data)

        # Define available tasks
        self.available_tasks = {
            'calculate_path_lengths': self.calculate_path_lengths,
            'calculate_velocities': self.calculate_velocities,
        }
        
        # Initialize tasks based on provided task list
        self.tasks = {task_name: {'function': self.available_tasks[task_name], 'result': None} for task_name in task_list}

        # Callbacks
        self.task_running_callback = task_running_callback
        self.task_completed_callback = task_completed_callback
        self.all_tasks_finished_callback = all_tasks_finished_callback

    def run(self):
        for task_name, task_info in self.tasks.items():
            if self.task_running_callback:
                self.task_running_callback(task_name)
            
            is_completed, result = task_info['function']()
            task_info['result'] = result

            if self.task_completed_callback:
                self.task_completed_callback(task_name, result)

        if self.all_tasks_finished_callback:
            self.all_tasks_finished_callback(self.tasks)

    def calculate_path_lengths(self):
        path_length_dictionary = {}
        for condition, frames in self.condition_frames_dictionary.items():
            frame_range = range(frames[0], frames[1])
            path_length_dictionary[condition] = self.path_length_calculator.get_path_length(frame_range)

        return True, path_length_dictionary

    def calculate_velocities(self):
        velocity_dictionary = {}
        for condition, frames in self.condition_frames_dictionary.items():
            frame_range = range(frames[0], frames[1])
            velocity_dictionary[condition] = self.path_length_calculator.calculate_velocity(frame_range)

        return True, velocity_dictionary