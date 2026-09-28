from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import numpy as np


class SkeletonViewWidget(QWidget):
    session_folder_loaded_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self.fig, self.ax = self.initialize_skeleton_plot()
        self._layout.addWidget(self.fig)

        self.session_folder_path = None

        # state
        self.xyz_array = None             # [F, M, 3]
        self.keypoint_names = None        # [M] list of strings
        self._name_to_idx = None          # dict name->int
        self.connections = []             # list[(nameA, nameB)]
        self.skel_3d_range = 900          # keep your previous default

    def initialize_skeleton_plot(self):
        fig = Mpl3DPlotCanvas(self, width=5, height=4, dpi=100)
        ax = fig.figure.axes[0]
        return fig, ax

    # NEW signature
    def reset_skeleton_3d_plot(self, xyz_array: np.ndarray, keypoint_names, connections):
        self.xyz_array = xyz_array
        self.keypoint_names = list(keypoint_names)
        self._name_to_idx = {n: i for i, n in enumerate(self.keypoint_names)}
        self.connections = list(connections) if connections else []

        self.ax.cla()
        self.calculate_axes_means(self.xyz_array)

        skel_x, skel_y, skel_z = self.get_x_y_z_data(0)
        self.plot_skel(0, skel_x, skel_y, skel_z)

    def calculate_axes_means(self, xyz_array):
        # Use ALL markers (not hard-coded 0:33)
        self.mx_skel = np.nanmean(xyz_array[:, :, 0])
        self.my_skel = np.nanmean(xyz_array[:, :, 1])
        self.mz_skel = np.nanmean(xyz_array[:, :, 2])

        # keep your fixed range; or compute from data if you prefer:
        # xr = np.nanmax(xyz_array[:, :, 0]) - np.nanmin(xyz_array[:, :, 0])
        # yr = np.nanmax(xyz_array[:, :, 1]) - np.nanmin(xyz_array[:, :, 1])
        # zr = np.nanmax(xyz_array[:, :, 2]) - np.nanmin(xyz_array[:, :, 2])
        # self.skel_3d_range = 0.6 * max(xr, yr, zr)  # example

    def plot_skel(self, frame_number, skel_x, skel_y, skel_z):
        self.ax.scatter(skel_x, skel_y, skel_z)
        self.plot_skeleton_bones(frame_number)
        self.ax.set_xlim([self.mx_skel - self.skel_3d_range, self.mx_skel + self.skel_3d_range])
        self.ax.set_ylim([self.my_skel - self.skel_3d_range, self.my_skel + self.skel_3d_range])
        self.ax.set_zlim([self.mz_skel - self.skel_3d_range, self.mz_skel + self.skel_3d_range])
        self.fig.figure.canvas.draw_idle()

    def plot_skeleton_bones(self, frame_number):
        if self.xyz_array is None or not self.connections:
            return
        for nameA, nameB in self.connections:
            if nameA not in self._name_to_idx or nameB not in self._name_to_idx:
                continue
            i = self._name_to_idx[nameA]
            j = self._name_to_idx[nameB]

            p = self.xyz_array[frame_number, i, :]
            q = self.xyz_array[frame_number, j, :]

            # Skip if both points are fully NaN
            if np.all(np.isnan(p)) and np.all(np.isnan(q)):
                continue

            self.ax.plot([p[0], q[0]], [p[1], q[1]], [p[2], q[2]])

    def get_x_y_z_data(self, frame_number: int):
        skel_x = self.xyz_array[frame_number, :, 0]
        skel_y = self.xyz_array[frame_number, :, 1]
        skel_z = self.xyz_array[frame_number, :, 2]
        return skel_x, skel_y, skel_z

    def replot(self, frame_number: int):
        if self.xyz_array is None:
            return
        skel_x, skel_y, skel_z = self.get_x_y_z_data(frame_number)
        self.ax.cla()
        self.plot_skel(frame_number, skel_x, skel_y, skel_z)


class Mpl3DPlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=4, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111, projection='3d')
        super(Mpl3DPlotCanvas, self).__init__(fig)
