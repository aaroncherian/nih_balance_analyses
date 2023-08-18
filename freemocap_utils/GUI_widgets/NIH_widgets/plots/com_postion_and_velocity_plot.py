from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import seaborn as sns
import numpy as np

class PathLengthsPlot(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create a Figure instance and attach it to FigureCanvas.
        self.figure = Figure(figsize=(10, 10))
        self.canvas = FigureCanvas(self.figure)
        
        # Create the navigation toolbar and attach it to the canvas.
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Layout to house the canvas and the toolbar
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)  # Add the toolbar at the top
        layout.addWidget(self.canvas)
        self.setLayout(layout)



class PositionAndVelocityPlot(QWidget):
    def __init__(self, parent=None):        
        super().__init__(parent)
        # Create a Figure instance and attach it to FigureCanvas.
        self.figure = Figure(figsize=(10, 10))
        self.canvas = FigureCanvas(self.figure)
        
        # Create the navigation toolbar and attach it to the canvas.
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Layout to house the canvas and the toolbar
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)  # Add the toolbar at the top
        layout.addWidget(self.canvas)
        self.setLayout(layout)


    def plot_data(self, results_container):
        # Clear the previous plot (if any)
        self.figure.clear()

        sns.set_style('whitegrid')

        com_position = results_container.center_of_mass_xyz
        com_velocity = np.diff(com_position, axis=0)

        # Create subplots for X Position, X Velocity, Y Position, Y Velocity
        ax1 = self.figure.add_subplot(2, 2, 1)
        ax2 = self.figure.add_subplot(2, 2, 2)
        ax3 = self.figure.add_subplot(2, 2, 3)
        ax4 = self.figure.add_subplot(2, 2, 4)

        # Plot X Position
        ax1.plot(com_position[:, 0], color='blue')
        ax1.set_title('X Position')
        ax1.set_ylabel('Position (units)')

        # Plot Y Position
        ax2.plot(com_position[:, 1], color='green')
        ax2.set_title('Y Position')

        # Plot X Velocity
        ax3.plot(com_velocity[:, 0], color='blue')
        ax3.set_title('X Velocity')
        ax3.set_ylabel('Velocity (units/s)')
        ax3.set_xlabel('Time (frames)')

        # Plot Y Velocity
        ax4.plot(com_velocity[:, 1], color='green')
        ax4.set_title('Y Velocity')
        ax4.set_xlabel('Time (frames)')

        # Redraw the canvas after plotting
        self.canvas.draw()

        results_container.position_and_velocity_figure = self.figure