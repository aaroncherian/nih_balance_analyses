import cv2
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog

from pathlib import Path

class VideoLoader(QWidget):
    """Handles video loading functionality.

    This class provides the UI and functionality to load a video file using OpenCV.

    Attributes:
        video_loaded_signal: Signal emitted when a video is successfully loaded.
    """

    video_loaded_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self.videoLoadButton = QPushButton('Load a video', self)
        self.videoLoadButton.setEnabled(False)
        self._layout.addWidget(self.videoLoadButton)
        self.videoLoadButton.clicked.connect(self.load_video)
        self.video_is_loaded = False

    def set_session_folder_path(self, session_folder_path: Path):
        """Set the session folder path.

        Args:
            session_folder_path (Path): The path to the session folder.
        """
        self.session_folder_path = session_folder_path

    def load_video(self):
        """Load the video using OpenCV.

        Opens a file dialog to select the video file and then loads it using OpenCV.
        Emits the `video_loaded_signal` if the video is successfully loaded.
        """
        self.folder_diag = QFileDialog()
        self.video_path, _ = QFileDialog.getOpenFileName(self, 'Open file', directory=str(self.session_folder_path))
        if self.video_path:
            self.vid_capture_object = cv2.VideoCapture(str(self.video_path))
            self.video_is_loaded = True
            self.video_loaded_signal.emit()


class VideoDisplay(QWidget):
    """Displays a video frame.

    This class provides the UI and functionality to display a video frame using a QLabel.

    Attributes:
        video_loader (VideoLoader): A `VideoLoader` instance to manage video loading.
    """

    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self.video_loader = VideoLoader()
        self._layout.addWidget(self.video_loader)
        self.video_frame = QLabel()
        self._layout.addWidget(self.video_frame)

    def set_frame(self, frame_number: int):
        """Set the current frame of the video.

        Args:
            frame_number (int): The frame number to set.
        """
        self.video_loader.vid_capture_object.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.video_loader.vid_capture_object.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(img)
        resizeImage = pix.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
        self.video_frame.setPixmap(resizeImage)
