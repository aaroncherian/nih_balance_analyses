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

        self.fig,self.ax = self.initialize_skeleton_plot()
        self._layout.addWidget(self.fig)

        self.session_folder_path = None
            
    def initialize_skeleton_plot(self):
        fig = Mpl3DPlotCanvas(self, width=5, height=4, dpi=100)
        ax = fig.figure.axes[0]
        return fig, ax

    def reset_skeleton_3d_plot(self,skeleton_3d_data:np.ndarray, mediapipe_skeleton):
        self.skeleton_3d_data = skeleton_3d_data
        self.mediapipe_skeleton = mediapipe_skeleton
        self.ax.cla()
        self.calculate_axes_means(self.skeleton_3d_data)
        self.skel_x,self.skel_y,self.skel_z = self.get_x_y_z_data(0)
        self.plot_skel(0,self.skel_x,self.skel_y,self.skel_z)

    def calculate_axes_means(self,skeleton_3d_data):
        self.mx_skel = np.nanmean(skeleton_3d_data[:,0:33,0])
        self.my_skel = np.nanmean(skeleton_3d_data[:,0:33,1])
        self.mz_skel = np.nanmean(skeleton_3d_data[:,0:33,2])
        self.skel_3d_range = 900

    def plot_skel(self,frame_number,skel_x,skel_y,skel_z):
        self.ax.scatter(skel_x,skel_y,skel_z)
        self.plot_skeleton_bones(frame_number)
        self.ax.set_xlim([self.mx_skel-self.skel_3d_range, self.mx_skel+self.skel_3d_range])
        self.ax.set_ylim([self.my_skel-self.skel_3d_range, self.my_skel+self.skel_3d_range])
        self.ax.set_zlim([self.mz_skel-self.skel_3d_range, self.mz_skel+self.skel_3d_range])

        self.fig.figure.canvas.draw_idle()

    def plot_skeleton_bones(self,frame_number):
        this_frame_skeleton_data = self.mediapipe_skeleton[frame_number]
        for connection in this_frame_skeleton_data.keys():
            line_start_point = this_frame_skeleton_data[connection][0] 
            line_end_point = this_frame_skeleton_data[connection][1]
            
            bone_x,bone_y,bone_z = [line_start_point[0],line_end_point[0]],[line_start_point[1],line_end_point[1]],[line_start_point[2],line_end_point[2]] 

            self.ax.plot(bone_x,bone_y,bone_z)

    def get_x_y_z_data(self, frame_number:int):
        skel_x = self.skeleton_3d_data[frame_number,:,0]
        skel_y = self.skeleton_3d_data[frame_number,:,1]
        skel_z = self.skeleton_3d_data[frame_number,:,2]

        return skel_x,skel_y,skel_z

    def replot(self, frame_number:int):
        skel_x,skel_y,skel_z = self.get_x_y_z_data(frame_number)
        self.ax.cla()
        self.plot_skel(frame_number,skel_x,skel_y,skel_z)

class Mpl3DPlotCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=4, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111,projection = '3d')
        super(Mpl3DPlotCanvas, self).__init__(fig)




