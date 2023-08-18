from PyQt6.QtWidgets import QWidget,QVBoxLayout, QComboBox, QLineEdit, QFormLayout, QPushButton, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem, QFileDialog, QCheckBox
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import pyqtSignal

import json


class FrameMarker(QWidget):
    """Handles frame marking for conditions.

    Allows users to set the starting and ending frames for various conditions.
    Optionally offers the ability to set an ending frame based on a predefined interval.

    Attributes:
        conditions_dict_updated_signal (pyqtSignal): Signal emitted when the conditions dictionary is updated.
    """

    conditions_dict_updated_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self._layout = QHBoxLayout()
        self.setLayout(self._layout)
        self.condition_widget_dictionary = {}
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface elements."""
        conditions_layout = self.create_conditions_layout()
        self._layout.addLayout(conditions_layout)

        self.saved_conditions_table = self.create_conditions_table()
        self._layout.addWidget(self.saved_conditions_table)

    def create_conditions_layout(self):
        """Create and return the conditions layout."""
        conditions_layout = QVBoxLayout()

        # Load Previous Frame Intervals button
        self.load_conditions_button = QPushButton('Load Previous Frame Interval JSON')
        self.load_conditions_button.pressed.connect(self.load_conditions)
        self.load_conditions_button.setEnabled(False)
        conditions_layout.addWidget(self.load_conditions_button)

        # Conditions dropdown
        self.conditions_box = QComboBox()
        self.conditions_box.addItems(['Eyes Open/Solid Ground', 'Eyes Closed/Solid Ground', 'Eyes Open/Foam', 'Eyes Closed/Foam'])
        self.conditions_box.currentTextChanged.connect(self.reset_start_and_end_frames)
        conditions_layout.addWidget(self.conditions_box)

        # Auto-fill checkbox and its accompanying text box
        self.auto_set_end_frame_checkbox = QCheckBox("Auto-Fill End Frame with Interval")
        self.auto_set_end_frame_checkbox.stateChanged.connect(self.calculate_ending_frame)
        self.interval_input = QLineEdit("1600")  # default value
        self.interval_input.setValidator(QIntValidator())
        self.interval_input.setFixedWidth(100)

        interval_layout = QHBoxLayout()
        interval_layout.addWidget(self.auto_set_end_frame_checkbox)
        interval_layout.addWidget(self.interval_input)
        conditions_layout.addLayout(interval_layout)

        # Starting and ending frame input boxes
        text_width = 100
        self.starting_frame = QLineEdit()
        self.starting_frame.setValidator(QIntValidator())
        self.starting_frame.setFixedWidth(text_width)
        self.ending_frame = QLineEdit()
        self.ending_frame.setValidator(QIntValidator())
        self.ending_frame.setFixedWidth(text_width)
        frame_form = QFormLayout()
        frame_form.addRow(QLabel('Start Frame'), self.starting_frame)
        frame_form.addRow(QLabel('End Frame'), self.ending_frame)
        conditions_layout.addLayout(frame_form)

        self.starting_frame.textChanged.connect(self.calculate_ending_frame)

        # Save Frame Interval button
        self.save_condition_button = QPushButton('Save Frame Interval For This Condition')
        self.save_condition_button.pressed.connect(self.save_conditions_to_table)
        self.save_condition_button.setEnabled(False)
        conditions_layout.addWidget(self.save_condition_button)

        return conditions_layout
    
    def create_conditions_table(self):
        """Create and return the conditions table."""
        table = QTableWidget()
        table.setRowCount(4)
        table.setColumnCount(2)
        return table
    
    def update_conditions_table(self):
        """Update the conditions table with current data."""
        self.saved_conditions_table.setVerticalHeaderLabels(list(self.condition_widget_dictionary.keys()))

        for row, condition in enumerate(self.condition_widget_dictionary.keys()):
            start_frame, end_frame = self.condition_widget_dictionary[condition]
            self.saved_conditions_table.setItem(row, 0, QTableWidgetItem(str(start_frame)))
            self.saved_conditions_table.setItem(row, 1, QTableWidgetItem(str(end_frame)))

    def save_conditions_to_table(self):
        current_condition = self.conditions_box.currentText()
        start_frame = int(self.starting_frame.text())
        end_frame = int(self.ending_frame.text())

        self.condition_widget_dictionary[current_condition] = [start_frame, end_frame]
        self.update_conditions_table()

        self.conditions_dict_updated_signal.emit()

    def load_conditions(self):
        self.condition_json, _ = QFileDialog.getOpenFileName(self, "Select JSON file", "", "JSON Files (*.json)")

        if self.condition_json:
            with open(self.condition_json, 'r') as json_file:
                data = json.load(json_file)

            self.condition_widget_dictionary = data['Frame Intervals']
            self.update_conditions_table()

            self.conditions_dict_updated_signal.emit()

    def calculate_ending_frame(self):
        if self.auto_set_end_frame_checkbox.isChecked() and self.starting_frame.text() and self.interval_input.text():
            try:
                starting = int(self.starting_frame.text())
                interval = int(self.interval_input.text())
                self.ending_frame.setText(str(starting + interval))
            except ValueError:
                # Handle any potential conversion errors if the input isn't a valid integer yet
                pass

    def reset_start_and_end_frames(self):
        self.starting_frame.setText(None)
        self.ending_frame.setText(None)    

        


