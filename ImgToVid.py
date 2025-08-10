import sys
import os
import cv2
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QFileDialog, QVBoxLayout, QHBoxLayout, QProgressBar, QMessageBox, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QMouseEvent

class ImageToVideoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎞️ Image Sequence to Video Converter")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.dark_mode = False

        self.resize(600, 250)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        title_bar = QFrame()
        title_bar.setObjectName("TitleBar")
        title_bar.setFixedHeight(36)

        self.toggle_btn = QPushButton("🌞")
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.clicked.connect(self.toggle_theme)

        self.min_btn = QPushButton("–")
        self.min_btn.setFixedSize(32, 32)
        self.min_btn.clicked.connect(self.showMinimized)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.clicked.connect(self.close)

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(8, 0, 8, 0)

        self.title_label = QLabel("🎞️ Image Sequence to Video Converter")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_layout.insertWidget(0, self.title_label)

        title_layout.addWidget(self.toggle_btn)
        title_layout.addWidget(self.min_btn)
        title_layout.addWidget(self.close_btn)

        self.content = QWidget()
        self.content.setObjectName("Content")
        self.content_layout = QVBoxLayout(self.content)
        self.content.setStyleSheet(self.load_styles())

        self.setup_converter_ui()

        main_layout.addWidget(title_bar)
        main_layout.addWidget(self.content)

    def setup_converter_ui(self):
        layout = QVBoxLayout()

        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select folder containing image sequence...")
        folder_btn = QPushButton("📁 Browse Image Folder")
        folder_btn.clicked.connect(self.browse_folder)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(folder_btn)

        self.fps_input = QLineEdit("30")
        self.fps_input.setFixedWidth(120)
        fps_label = QLabel("Frame Rate (FPS):")

        self.format_combo = QComboBox()
        self.format_combo.setFixedWidth(120)
        self.format_combo.addItems(["mp4", "avi"])


        format_label = QLabel("Output Format:")

        fps_format_layout = QHBoxLayout()
        fps_format_layout.addWidget(fps_label)
        fps_format_layout.addWidget(self.fps_input)
        fps_format_layout.addStretch(50) # optional spacing between fps and format
        fps_format_layout.addWidget(format_label)
        fps_format_layout.addWidget(self.format_combo)

        fps_format_layout.addStretch()

        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("Choose output video file name...")
        output_btn = QPushButton("Browse")
        output_btn.clicked.connect(self.choose_output)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(output_btn)

        convert_btn = QPushButton("Convert Now")
        convert_btn.setStyleSheet("font-weight: bold; background-color: #6f00ff; color: white; padding: 10px 16px; font-size: 15px;")
        convert_btn.clicked.connect(self.convert_video)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(True)

        layout.addLayout(folder_layout)

        layout.addLayout(fps_format_layout)
        layout.addLayout(output_layout)
        layout.addWidget(convert_btn)
        layout.addWidget(self.progress)

        self.content_layout.addLayout(layout)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.toggle_btn.setText("🌙" if not self.dark_mode else "🌞")
        self.content.setStyleSheet(self.load_styles())




    def load_styles(self):
        if self.dark_mode:
            return """
            QWidget#Content {
                background-color: #1e1e1e;
                color: #f1f5f9;
                border-radius: 10px;
            }
            QLineEdit, QComboBox {
                background-color: #2c2c2c;
                color: #e2e8f0;
                border: 1px solid #4D4D4D;
                border-radius: 12px;
                padding: 8px;
            }


            
            QPushButton {
                background-color: #2c2c2c;
                color: white;
                border: none;
                padding: 8px 14px;
                border: 1px solid #4D4D4D;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #6f00ff;
            }
            QLabel {
                font-weight: 600;
            }
            QProgressBar {
                height: 24px;
                border: 1px solid #4D4D4D;
                border-radius: 10px;
                background-color: #2c2c2c;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 10px;
            }
            QFrame#TitleBar {
                background-color: #0f172a;
            }
            """
        else:
            return """
            QWidget#Content {
                background-color: #f9fafb;
                font-family: 'Segoe UI';
                font-size: 14px;
                color: #111827;
                border-radius:12px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 12px;
                background-color: #f9fafb;
                color: black;
            }
            QPushButton {
                background-color: #1e1e1e;
                color: white;
                border: none;
                padding: 8px 14px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QLabel {
                font-weight: 600;
                color: black;
            }
            QProgressBar {
                height: 24px;
                border: 1px solid #cbd5e1;
                border-radius: 10px;
                background-color: #e5e7eb;
                text-align: center;
                color:black;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 10px;
            }
            QFrame#TitleBar {
                background-color: #e5e7eb;
            }
            """

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if hasattr(self, 'old_pos'):
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.folder_input.setText(folder)

    def choose_output(self):
        file_type = self.format_combo.currentText()
        file_filter = "MP4 Video (*.mp4)" if file_type == "mp4" else "AVI Video (*.avi)"
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Video As", "output_video." + file_type, file_filter)
        if file_name:
            self.output_input.setText(file_name)

    def convert_video(self):
        folder = self.folder_input.text()
        output_file = self.output_input.text()
        file_type = self.format_combo.currentText()

        try:
            fps = float(self.fps_input.text())
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid frame rate value.")
            return

        if not os.path.isdir(folder):
            QMessageBox.critical(self, "Error", "Selected folder does not exist.")
            return

        images = [img for img in os.listdir(folder) if img.lower().endswith((".png", ".jpg", ".jpeg"))]
        images.sort()

        if not images:
            QMessageBox.critical(self, "Error", "No image files found in the selected folder.")
            return

        first_frame = cv2.imread(os.path.join(folder, images[0]))
        height, width, _ = first_frame.shape

        if file_type == "avi":
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
        else:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        video = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

        self.progress.setMaximum(len(images))
        for i, img_name in enumerate(images):
            frame = cv2.imread(os.path.join(folder, img_name))
            video.write(frame)
            self.progress.setValue(i + 1)

            QApplication.processEvents()

        video.release()

        msg_box = QMessageBox(self)
        msg_box.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        msg_box.setText(f"✅ Video successfully saved!")


        msg_box.setStyleSheet("""

        QMessageBox {
            background-color: white;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            font-size: 14px;
            padding: 20px;
        }
                      
        QLabel {
            color: #111827;
            font-weight: 500;
            text-align: center;
        }
        QPushButton {
            background-color: #3b82f6;
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2563eb;
        }
    """)


        open_btn = msg_box.addButton("📂 Open Folder", QMessageBox.ButtonRole.ActionRole)
        ok_btn = msg_box.addButton(QMessageBox.StandardButton.Ok)

        msg_box.exec()

        if msg_box.clickedButton() == open_btn:
            self.open_folder_with_platform_support(os.path.dirname(output_file))



    def open_folder_with_platform_support(self, path):
        import platform
        import subprocess
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageToVideoApp()
    window.show()
    sys.exit(app.exec())
