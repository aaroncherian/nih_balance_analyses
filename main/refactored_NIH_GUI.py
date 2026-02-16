
from tkinter.font import names
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QApplication, QHBoxLayout, QVBoxLayout,
    QPushButton, QGroupBox, QTabWidget, QComboBox, QLabel, QMessageBox
)
from gui.widgets.skeleton_view_widget import SkeletonViewWidget
from gui.widgets.slider_widget import FrameCountSlider
from gui.widgets.video_capture_widget import VideoDisplay
from gui.widgets.frame_marking_widget import FrameMarker
from gui.widgets.saving_data_analysis_widget import SavingDataAnalysisWidget
from gui.widgets.balance_assessment_widget import BalanceAssessmentWidget
from gui.utils.mediapipe_skeleton_builder import build_skeleton, mediapipe_connections, mediapipe_indices, qualisys_indices
from gui.utils.file_manager import FileManager
from gui.models.results_container import BalanceAssessmentResultsContainer

from gui.plots.path_length_line_plot import PathLengthsPlot
from gui.plots.com_postion_and_velocity_plot import PositionAndVelocityPlot

from skellymodels.managers.human import Human
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.results_container = BalanceAssessmentResultsContainer(condition_frame_dictionary={}, path_length_dictionary={}, velocity_dictionary={}, postion_dictionary={}, center_of_mass_xyz = None)

        self.tab_widget = QTabWidget()

        self.main_tab = MainTab(self.results_container)
        self.tab_widget.addTab(self.main_tab, "Main Menu")

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        self.connect_signals_to_slots()

    def connect_signals_to_slots(self):
        self.main_tab.balance_assessment_widget.balance_assessment_finished_signal.connect(self.add_path_lengths_plot_tab)
        self.main_tab.balance_assessment_widget.balance_assessment_finished_signal.connect(self.add_position_and_velocity_plot_tab)

    def add_path_lengths_plot_tab(self):
        # Instantiate the plotting widget and plot the data
        path_lengths_plot_widget = PathLengthsPlot()
        path_lengths_plot_widget.plot_data(self.results_container)

        # Add the plotting widget as a new tab
        self.tab_widget.addTab(path_lengths_plot_widget, "Path Length vs. Condition")

    def add_position_and_velocity_plot_tab(self):
        # Instantiate the plotting widget and plot the data
        position_and_velocity_plot_widget = PositionAndVelocityPlot()
        position_and_velocity_plot_widget.plot_data(self.results_container)

        # Add the plotting widget as a new tab
        self.tab_widget.addTab(position_and_velocity_plot_widget, "Position and Velocity vs. Condition")






class MainTab(QWidget):

    def __init__(self, results_container):
        super().__init__()

        self.setWindowTitle("My App")

        layout = QVBoxLayout(self) 

        self.file_manager = FileManager()
        self.results_container = results_container
        

        slider_and_skeleton_layout = QVBoxLayout()

        self.load_session_groupbox = self.create_load_session_groupbox()
        slider_and_skeleton_layout.addWidget(self.load_session_groupbox)

        self.skeleton_viewer_groupbox = self.create_skeleton_viewer_groupbox()
        slider_and_skeleton_layout.addWidget(self.skeleton_viewer_groupbox)

        self.camera_view_groupbox = self.create_camera_view_groupbox()
        self.frame_marking_groupbox = self.create_frame_marking_groupbox()
        self.balance_assessment_groupbox = self.create_balance_assessment_groupbox()
        self.saving_data_groupbox = self.create_saving_data_groupbox()

        main_layout = QHBoxLayout()
        main_layout.addLayout(slider_and_skeleton_layout)
        main_layout.addWidget(self.camera_view_groupbox)

        layout.addLayout(main_layout)
        layout.addWidget(self.frame_marking_groupbox)
        layout.addWidget(self.balance_assessment_groupbox)
        layout.addWidget(self.saving_data_groupbox)

        self.setLayout(layout) 

        self.connect_signals_to_slots()

    def connect_signals_to_slots(self):
        self.frame_count_slider.slider.valueChanged.connect(self.handle_slider_value_changed)
        self.camera_view_widget.video_loader.video_loaded_signal.connect(self.set_video_to_slider_frame)

        self.frame_marking_widget.conditions_dict_updated_signal.connect(self.update_condition_frame_dictionary)
      

    def _handle_session_folder_loaded(self):
        self.frame_count_slider.set_slider_range(self.num_frames)
        self.enable_buttons()
        self.set_session_folder_path()

    def handle_slider_value_changed(self):
        self.skeleton_view_widget.replot(self.frame_count_slider.slider.value())
        if self.camera_view_widget.video_loader.video_is_loaded:
            current_frame = self.frame_count_slider.slider.value()
            self.camera_view_widget.set_frame(current_frame)

    def update_condition_frame_dictionary(self):
        self.results_container.condition_frame_dictionary = self.frame_marking_widget.condition_widget_dictionary

    def set_video_to_slider_frame(self):
        current_frame = self.frame_count_slider.slider.value()
        self.camera_view_widget.set_frame(current_frame)

    def open_folder_dialog(self):
        self.session_folder_path = self.file_manager.get_existing_directory("Choose a session")
        self.frame_marking_widget.set_data_path(self.session_folder_path)

        valid_datasets = self.file_manager.scan_session_for_data(self.session_folder_path)
        if not valid_datasets:
            QMessageBox.warning(self, "No datasets found",
                                "No tidy parquet files were found under this session's 'validation' folder.")
            # Hide/disable dataset UI
            self.dataset_selector.clear()
            self.dataset_selector.setEnabled(False)
            self.dataset_selector.setVisible(False)
            self.load_dataset_button.setEnabled(False)
            return

        self.dataset_paths = {p.stem: p for p in valid_datasets}
            # Populate and show the selector
        names = sorted(self.dataset_paths.keys())
        self.dataset_selector.blockSignals(True)
        self.dataset_selector.clear()
        self.dataset_selector.addItems(names)
        self.dataset_selector.blockSignals(False)

        # Select first by default
        if names:
            first = names[0]
            self.selected_dataset_name = first
            self.selected_dataset_root = self.dataset_paths[first]
        else:
            self.selected_dataset_name = None
            self.selected_dataset_root = None

        # Reveal controls now that we have something to pick
        self.dataset_selector.setVisible(True)
        self.dataset_selector.setEnabled(True)
        self.load_dataset_button.setEnabled(True)

    def on_dataset_changed(self, name: str):
        if not name:
            return
        # Update selected dataset pointers
        self.selected_dataset_name = name
        self.selected_dataset_root = self.dataset_paths[name]
        # (Optional) update a status label here if you have one

    def load_dataset_clicked(self):
        """
        Entry point after the user has chosen a dataset name from the combo box.
        This is where you'll plug in your parquet → arrays → viewer + COM wiring.
        """
        if not getattr(self, "selected_dataset_root", None):
            QMessageBox.warning(self, "No dataset selected", "Please choose a dataset to load.")
            return
        
        human:Human = Human.from_data(self.selected_dataset_root)

        if human.body.total_body_com is None:
            human.calculate()

        self.num_frames = human.body.xyz.as_array.shape[0]

        com_data = human.body.total_body_com.as_array
        self.balance_assessment_widget.set_center_of_mass_data(com_data)
        self.results_container.center_of_mass_xyz = com_data

        raw_conns = human.body.anatomical_structure.segment_connections
        connections = self._normalize_connections_to_pairs(raw_conns)
        self.skeleton_view_widget.reset_skeleton_3d_plot(
                xyz_array=human.body.xyz.as_array,
                keypoint_names=human.body.anatomical_structure.landmark_names,
                connections=connections,
        )
        
        self._handle_session_folder_loaded()
    
    def _normalize_connections_to_pairs(self, segment_connections) -> list[tuple[str, str]]:
        """
        Accepts either a dict of {seg: {proximal, distal}} or an iterable of pairs,
        and returns a clean list of (nameA, nameB) tuples.
        """
        if isinstance(segment_connections, dict):
            pairs = []
            for v in segment_connections.values():
                a = v.get("proximal")
                b = v.get("distal")
                if a and b:
                    pairs.append((a, b))
            return pairs
        # already pairs or list-like
        out = []
        for c in segment_connections:
            if isinstance(c, (list, tuple)) and len(c) == 2:
                out.append((c[0], c[1]))
        return out

    def set_session_folder_path(self):
        self.camera_view_widget.video_loader.set_session_folder_path(self.session_folder_path)
        self.saving_data_widget.set_selected_dataset_folder(self.selected_dataset_root)

    def enable_buttons(self):
        self.balance_assessment_widget.run_path_length_analysis_button.setEnabled(True)
        self.camera_view_widget.video_loader.videoLoadButton.setEnabled(True)
        self.frame_marking_widget.save_condition_button.setEnabled(True)
        self.frame_marking_widget.load_conditions_button.setEnabled(True)
        self.saving_data_widget.save_data_button.setEnabled(True)

    def set_condition_frames_dictionary(self, condition_frames_dictionary:dict):
        self.condition_frames_dictionary = condition_frames_dictionary

    def create_load_session_groupbox(self):
        groupbox = QGroupBox("Load a Session")
        layout = QVBoxLayout()

        # 1) Pick session folder
        self.folder_open_button = QPushButton("Choose session folder", self)
        self.folder_open_button.clicked.connect(self.open_folder_dialog)
        layout.addWidget(self.folder_open_button)

        # 2) Dataset picker (hidden until a session is chosen)
        row = QHBoxLayout()
        self.dataset_label = QLabel("Dataset:")
        self.dataset_selector = QComboBox()
        self.dataset_selector.setEnabled(False)
        self.dataset_selector.setVisible(False)
        self.dataset_selector.currentTextChanged.connect(self.on_dataset_changed)
        row.addWidget(self.dataset_label)
        row.addWidget(self.dataset_selector)
        layout.addLayout(row)

        # 3) Load selected dataset
        self.load_dataset_button = QPushButton("Load selected dataset")
        self.load_dataset_button.setEnabled(False)
        self.load_dataset_button.clicked.connect(self.load_dataset_clicked)
        layout.addWidget(self.load_dataset_button)

        groupbox.setLayout(layout)
        return groupbox
    
    def create_skeleton_viewer_groupbox(self):
        
        groupbox = QGroupBox("View Skeleton")
        view_skeleton_layout = QVBoxLayout()
        self.frame_count_slider = FrameCountSlider()
        view_skeleton_layout.addWidget(self.frame_count_slider)
        self.skeleton_view_widget = SkeletonViewWidget()
        self.skeleton_view_widget.setFixedSize(self.skeleton_view_widget.size())
        view_skeleton_layout.addWidget(self.skeleton_view_widget)
        
        groupbox.setLayout(view_skeleton_layout)

        return groupbox

    def create_camera_view_groupbox(self):
        groupbox = QGroupBox("Load a Video")
        layout = QVBoxLayout()
        self.camera_view_widget = VideoDisplay()
        self.camera_view_widget.setFixedSize(self.skeleton_view_widget.size())
        layout.addWidget(self.camera_view_widget)
        groupbox.setLayout(layout)
        return groupbox

    def create_frame_marking_groupbox(self):
        groupbox = QGroupBox("Annotate Frames for Conditions")
        layout = QVBoxLayout()
        self.frame_marking_widget = FrameMarker()
        self.frame_marking_widget.setFixedSize(640,200)
        layout.addWidget(self.frame_marking_widget)
        groupbox.setLayout(layout)
        return groupbox

    def create_balance_assessment_groupbox(self):
        groupbox = QGroupBox("Run Balance Assessment")
        layout = QVBoxLayout()
        self.balance_assessment_widget = BalanceAssessmentWidget(self.results_container)
        layout.addWidget(self.balance_assessment_widget)
        groupbox.setLayout(layout)
        return groupbox

    def create_saving_data_groupbox(self):
        groupbox = QGroupBox("Save Data")
        layout = QVBoxLayout()
        self.saving_data_widget = SavingDataAnalysisWidget(self.results_container)
        layout.addWidget(self.saving_data_widget)
        groupbox.setLayout(layout)
        return groupbox
    

if __name__ == "__main__":

    app = QApplication([])
    win = MainWindow()

    win.show()
    app.exec()
