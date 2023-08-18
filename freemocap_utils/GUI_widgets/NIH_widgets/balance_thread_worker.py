import threading
from freemocap_utils.GUI_widgets.NIH_widgets.path_length_tools import path_length_calculator
import numpy as np

class BalanceAssessmentWorkerThread(threading.Thread):
    """
    A thread to perform balance assessment tasks such as calculating path lengths and velocities.

    Attributes:
        com_data (np.ndarray): 3d total body center of mass data.
        condition_frames_dictionary (dict): Dictionary containing condition names and their corresponding frame ranges.
        path_length_calculator (PathLengthCalculator): An instance of the path length calculator tool.
        available_tasks (dict): Dictionary of task names mapped to their respective function handlers.
        tasks (dict): Dictionary of tasks to run with their results.
        task_running_callback (function): Callback function to indicate a task has started.
        task_completed_callback (function): Callback function to indicate a task has completed.
        all_tasks_finished_callback (function): Callback function to indicate all tasks have finished.
    """

    def __init__(self, 
                 com_data: np.ndarray, 
                 condition_frames_dictionary: dict, 
                 task_list: list,
                 task_running_callback=None, 
                 task_completed_callback=None, 
                 all_tasks_finished_callback=None):

        super().__init__()

        self.com_data = com_data
        self.condition_frames_dictionary = condition_frames_dictionary
        self.path_length_calculator = path_length_calculator.PathLengthCalculator(self.com_data)

        self.available_tasks = {
            'calculate_path_lengths': self.calculate_path_lengths,
            'calculate_velocities': self.calculate_velocities,
            'splice_positions_by_condition': self.splice_positions_by_condition
        }
        
        self.tasks = {}
        for task_name in task_list:
            try:
                self.tasks[task_name] = {'function': self.available_tasks[task_name], 'result': None}
            except KeyError:
                raise ValueError(f"The task '{task_name}' was not found in the available tasks {self.available_tasks.keys()}")
        self.task_running_callback = task_running_callback
        self.task_completed_callback = task_completed_callback
        self.all_tasks_finished_callback = all_tasks_finished_callback

    def run(self):
        """
        Overrides the threading.Thread run method. Executes the tasks and manages the callbacks.
        """
        for task_name, task_info in self.tasks.items():
            if self.task_running_callback:
                self.task_running_callback(task_name)
            
            is_completed, result = task_info['function']()
            task_info['result'] = result

            
            if self.task_completed_callback:
                self.task_completed_callback(task_name, result if is_completed else None)

        if self.all_tasks_finished_callback:
            self.all_tasks_finished_callback(self.tasks)

    def calculate_path_lengths(self):
        """
        Calculate the path lengths for each condition.

        Returns:
            tuple: A tuple containing a boolean indicating successful completion and a dictionary of the center of mass path length for each condition.
        """
        path_length_dictionary = {}
        for condition, frames in self.condition_frames_dictionary.items():
            frame_range = range(frames[0], frames[1])
            path_length_dictionary[condition] = self.path_length_calculator.get_path_length(frame_range)

        return True, path_length_dictionary

    def calculate_velocities(self):
        """
        Calculate the velocities for each condition.

        Returns:
            tuple: A tuple containing a boolean indicating successful completion and dictionary of the center of mass velocity values during each condition.
        """
        velocity_dictionary = {}
        for condition, frames in self.condition_frames_dictionary.items():
            frame_range = range(frames[0], frames[1])
            velocity_dictionary[condition] = self.path_length_calculator.calculate_velocity(frame_range)

        return True, velocity_dictionary
    
    def splice_positions_by_condition(self):
        """
        Splice the position data by condition to save out 

        Returns:
            tuple: A tuple containing a boolean indicating successful completion and dictionary of the center of mass position values during each condition.
        """
        position_dictionary = {}

        for condition, frames in self.condition_frames_dictionary.items():
            start_frame, end_frame = frames
            
            # Extract positions for each dimension separately and store in a list
            position_data = [self.com_data[start_frame:end_frame, i] for i in range(3)]
            position_dictionary[condition] = position_data
        return True, position_dictionary


