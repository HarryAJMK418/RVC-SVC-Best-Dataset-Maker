"""
Audio Splitter - a tool for splitting audio files
Author: Justin John
Date: 2023-05-19

This script uses PyQt5 and other libraries to create an application for splitting 
audio files based on silence detection.

This software is licensed under the MIT License. You are free to redistribute, modify, 
or sell this software under the conditions stated in the license.

For more information, contact the author at justinjohn0306@gmail.com.
"""

import os
import sys
import tempfile
import zipfile
import multiprocessing as mp
from pydub import AudioSegment, silence
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QIntValidator, QBrush, QColor
from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, 
                             QProgressBar, QListWidget, QListWidgetItem, QLineEdit, 
                             QFileDialog, QApplication, QSlider, QMessageBox, QComboBox, 
                             QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal



def remove_silence(audio, silence_thresh=-40):
    non_silent_audio = silence.split_on_silence(audio, min_silence_len=1000, silence_thresh=silence_thresh)
    return non_silent_audio


def join_audio_segments(segments, segment_duration):
    joined_segments = []
    current_segment = None
    for segment in segments:
        if current_segment is None:
            current_segment = segment
        elif len(current_segment) < segment_duration * 1000:
            current_segment += segment
        else:
            joined_segments.append(current_segment)
            current_segment = segment

    if current_segment is not None:
        joined_segments.append(current_segment)

    return joined_segments


def process_audio_file(audio_file_path, i, segment_duration, silence_thresh=-40, output_format="mp3"):
    audio = AudioSegment.from_file(audio_file_path)

    non_silent_audio = remove_silence(audio, silence_thresh=silence_thresh)

    segments = []
    for j, segment in enumerate(non_silent_audio):
        if len(segment) >= segment_duration * 1000:
            segments.extend(segment[0:segment_duration * 1000] for segment in segment[::segment_duration * 1000])
        else:
            segments.append(segment)

    joined_segments = join_audio_segments(segments, segment_duration)

    temp_files = []
    for k, segment in enumerate(joined_segments):
        temp_file = tempfile.NamedTemporaryFile(suffix=f".{output_format}", delete=False)
        segment.export(temp_file.name, format=output_format)  # Write segment to the temp file
        segment_file_name = f"segment_{i + 1}_{k + 1}.{output_format}"
        temp_files.append((segment_file_name, temp_file.name))

    return temp_files



def process_audio_files(audio_files, segment_duration, silence_thresh, output_format, progress_queue):
    for i, audio_file_path in enumerate(audio_files):
        temp_files = process_audio_file(audio_file_path, i, segment_duration, silence_thresh, output_format)
        progress_queue.put((i, temp_files))


class WorkerThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)

    def __init__(self, audio_files, segment_duration, silence_thresh, output_format, output_dir):
        super().__init__()
        self.audio_files = audio_files
        self.segment_duration = segment_duration
        self.silence_thresh = silence_thresh
        self.output_format = output_format
        self.output_dir = output_dir

    def run(self):
        progress_queue = mp.Queue()
        p = mp.get_context('spawn').Process(target=process_audio_files, args=(self.audio_files, self.segment_duration, self.silence_thresh, self.output_format, progress_queue))
        p.start()

        completed = 0
        temp_files = []
        while completed < len(self.audio_files):
            i, temp_file = progress_queue.get()
            completed += 1
            self.progress_signal.emit((completed / len(self.audio_files)) * 100)
            temp_files.extend(temp_file)

        p.join()

        zip_file_name = os.path.join(self.output_dir, "audio_segments.zip")  # Path now includes output directory
        with zipfile.ZipFile(zip_file_name, 'w') as zip_file:
            for segment_file_name, temp_file_name in temp_files:
                with open(temp_file_name, 'rb') as f:
                    zip_file.writestr(segment_file_name, f.read())
                os.remove(temp_file_name)

        self.finished_signal.emit(zip_file_name)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Window settings
        self.setWindowTitle("Audio Splitter")
        self.setFixedSize(800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #f0f0f0, stop: 1 #a3a3a3);
            }
            QLabel, QPushButton, QSlider, QProgressBar, QComboBox {
                font-family: "Segoe UI";
                font-size: 16px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
            QPushButton:pressed {
                background-color: #004070;
            }
            QLabel {
                color: #404040;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #bfbfbf;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4d455, stop:1 #8cbf26);
                border: 1px solid #5c912b;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #05B8CC;
                width: 20px;
            }
            QComboBox {
                border: 1px solid gray;
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }
            QComboBox:editable {
                background: white;
            }
            QComboBox:!editable, QComboBox::drop-down:editable {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                            stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
            }
            QComboBox:!editable:on, QComboBox::drop-down:editable:on {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #D3D3D3, stop: 0.4 #D8D8D8,
                                            stop: 0.5 #DDDDDD, stop: 1.0 #E1E1E1);
            }
            QComboBox:on {
                padding-top: 3px;
                padding-left: 4px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QListWidget {
                border: 1px solid gray;
                color: #404040;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6ea1f1, stop:1 #567dbc);
            }
        """)

        self.main_layout = QVBoxLayout()

        self.files_list_label = QLabel("Files:")
        self.files_list = FileListWidget()

        self.add_files_button = QPushButton("Add Files")
        self.add_files_button.clicked.connect(self.add_files)

        self.remove_files_button = QPushButton("Remove Selected Files")
        self.remove_files_button.clicked.connect(self.remove_files)

        self.clear_files_button = QPushButton("Clear All Files")
        self.clear_files_button.clicked.connect(self.clear_files)

        self.segment_duration_label = QLabel("Segment Duration (seconds):")
        self.segment_duration_input = QLineEdit()
        self.segment_duration_input.setValidator(QIntValidator(1, 3600))
        self.segment_duration_input.setStyleSheet("font-family: 'Roboto'; font-size: 14pt")


        self.silence_thresh_label = QLabel("Silence Threshold (dB):")
        self.silence_thresh_slider = QSlider(Qt.Horizontal)
        self.silence_thresh_slider.setMinimum(-50)
        self.silence_thresh_slider.setMaximum(0)
        self.silence_thresh_slider.setValue(-40)
        self.silence_thresh_slider.valueChanged.connect(self.update_silence_thresh_label)

        self.silence_thresh_value_label = QLabel()
        self.update_silence_thresh_label()

        self.output_format_label = QLabel("Output Format:")
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(["wav", "mp3", "flac", "ogg", "m4a"])

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #05B8CC;
                width: 20px;
            }
        """)

        self.main_layout.addWidget(self.files_list_label)
        self.main_layout.addWidget(self.files_list)
        self.main_layout.addWidget(self.add_files_button)
        self.main_layout.addWidget(self.remove_files_button)
        self.main_layout.addWidget(self.clear_files_button)
        self.main_layout.addWidget(self.segment_duration_label)
        self.main_layout.addWidget(self.segment_duration_input)
        self.main_layout.addWidget(self.silence_thresh_label)
        self.main_layout.addWidget(self.silence_thresh_slider)
        self.main_layout.addWidget(self.silence_thresh_value_label)
        self.main_layout.addWidget(self.output_format_label)
        self.main_layout.addWidget(self.output_format_combo)
        self.main_layout.addWidget(self.start_button)
        # Create a horizontal box layout
        progress_layout = QHBoxLayout()

        # Add stretch on both sides of the progress bar
        progress_layout.addStretch(1)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addStretch(1)

        # Add the progress layout to the main layout
        self.main_layout.addLayout(progress_layout)


        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.main_widget)

    def add_files(self, file_paths=None):
        if not file_paths:
            file_paths, _ = QFileDialog.getOpenFileNames(self, "Select audio files", "", "Audio Files (*.mp3 *.wav *.flac *.ogg *.m4a)")

        if file_paths:
            for file_path in file_paths:
                try:
                    item = QListWidgetItem(file_path)
                    self.files_list.addItem(item)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to load audio file: {str(e)}")

    def remove_files(self):
        selected_items = self.files_list.selectedItems()
        for item in selected_items:
            self.files_list.takeItem(self.files_list.row(item))

    def clear_files(self):
        self.files_list.clear()

    def update_silence_thresh_label(self):
        self.silence_thresh_value_label.setText(f"Current threshold: {self.silence_thresh_slider.value()} dB")

    def start(self):
        if not self.files_list.count():
            QMessageBox.warning(self, "No files", "No files have been added.")
            return

        segment_duration_text = self.segment_duration_input.text().strip()
        if not segment_duration_text.isdigit():
            QMessageBox.warning(self, "Invalid input", "Please enter a valid segment duration.")
            return
        segment_duration = int(segment_duration_text)

        silence_thresh = self.silence_thresh_slider.value()

        output_format = self.output_format_combo.currentText()

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return

        audio_files = [self.files_list.item(i).text() for i in range(self.files_list.count())]

        self.worker_thread = WorkerThread(audio_files, segment_duration, silence_thresh, output_format, output_dir)
        self.worker_thread.progress_signal.connect(self.progress_bar.setValue)
        self.worker_thread.finished_signal.connect(self.finished)
        self.worker_thread.start()

    def finished(self, zip_file_name):
        QMessageBox.information(self, "Finished", f"Audio segments saved to {zip_file_name}.")


class FileListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            self.add_files(file_paths)

    def add_files(self, file_paths):
        if file_paths:
            for file_path in file_paths:
                try:
                    item = QListWidgetItem(file_path)
                    self.addItem(item)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to load audio file: {str(e)}")


def main():
    QtCore.QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    mp.freeze_support()
    main()

