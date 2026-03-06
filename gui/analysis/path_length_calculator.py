import numpy as np

class PathLengthCalculator():

    def __init__(self,
                 freemocap_data:np.ndarray,
                 sampling_rate:float = 30):
        self.freemocap_data = freemocap_data
        self.sampling_rate = sampling_rate

    def slice_data(self, freemocap_data, num_frame_range):
        sliced_freemocap_data = freemocap_data[num_frame_range[0]:num_frame_range[-1],:]
        return sliced_freemocap_data

    def calculate_path_length(self, sliced_freemocap_data):
        diffs = np.diff(sliced_freemocap_data, axis=0)
        path_length = np.sum(np.linalg.norm(diffs, axis=-1))
        # duration_seconds = (len(sliced_freemocap_data) - 1) / self.sampling_rate
        return path_length 

    def calculate_distance(self, point1, point2):
        point1 = point1[0]
        point2 = point2[0]
        return np.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2 + (point1[2]-point2[2])**2)

    def get_path_length(self,num_frame_range):
        self.sliced_freemocap_data = self.slice_data(self.freemocap_data,num_frame_range)
        self.path_length = self.calculate_path_length(self.sliced_freemocap_data)
        return self.path_length

    def calculate_velocity(self, num_frame_range):
        sliced_freemocap_data = self.slice_data(self.freemocap_data,num_frame_range)
        velocity_data = []

        pos_difference = np.diff(sliced_freemocap_data, axis=0)

        velocity_data = pos_difference * self.sampling_rate
        return velocity_data 