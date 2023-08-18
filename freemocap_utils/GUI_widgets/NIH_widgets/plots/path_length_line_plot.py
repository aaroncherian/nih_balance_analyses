from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import seaborn as sns
import pandas as pd

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

    def plot_data(self, results_container):
        # Clear the previous plot (if any)
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        path_length_dictionary = results_container.path_length_dictionary
        # Convert the dictionary to a DataFrame
        freemocap_path_lengths = pd.DataFrame(path_length_dictionary, index=[0])

        # Set seaborn style
        sns.set_style('whitegrid')

        # Conditions
        conditions = freemocap_path_lengths.columns
        conditions = [condition.replace('/', '\n') for condition in conditions]

        # Plotting Freemocap data for the single session
        ax.plot(conditions, freemocap_path_lengths.iloc[0], '-o', color= '#7994B0')

        # Labels and titles for Freemocap
        ax.set_title('Freemocap Path Lengths Per Condition', fontsize = 16)
        ax.set_ylabel('Path Length (mm)', fontsize = 14)
        ax.set_xlabel('Condition', fontsize = 14)

        # Redraw the canvas after plotting
        self.canvas.draw()

        results_container.path_length_figure = self.figure




        