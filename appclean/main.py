import sys
import cv2
import socket
import mediapipe as mp
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QSlider, QTextEdit, QMainWindow, QSizePolicy
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Gesture Controller")
        self.setGeometry(100, 100, 1280, 720)
        self.showMaximized()

        self.capture = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.hands = mp_hands.Hands(max_num_hands=1)
        self.command_sent = ""

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # --- Video label (left) ---
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.video_label.setScaledContents(True)

        # --- Controls & log (right) ---
        self.ip_input = QLineEdit("192.168.137.205")
        self.port_input = QLineEdit("4210")

        self.top_slider = QSlider(Qt.Horizontal)
        self.top_slider.setRange(0, 720)     # match new capture height
        self.top_slider.setValue(100)

        self.bottom_slider = QSlider(Qt.Horizontal)
        self.bottom_slider.setRange(0, 720)
        self.bottom_slider.setValue(380)

        self.start_button = QPushButton("Start Camera")
        self.stop_button  = QPushButton("Stop Camera")
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        settings_layout = QVBoxLayout()
        settings_layout.addWidget(QLabel("ESP32 IP:"))
        settings_layout.addWidget(self.ip_input)
        settings_layout.addWidget(QLabel("ESP32 Port:"))
        settings_layout.addWidget(self.port_input)
        settings_layout.addWidget(QLabel("Top Box Height:"))
        settings_layout.addWidget(self.top_slider)
        settings_layout.addWidget(QLabel("Bottom Box Height:"))
        settings_layout.addWidget(self.bottom_slider)
        settings_layout.addWidget(self.start_button)
        settings_layout.addWidget(self.stop_button)
        settings_layout.addWidget(QLabel("Log Output:"))
        settings_layout.addWidget(self.log_output)

        right_widget = QWidget()
        right_widget.setLayout(settings_layout)
        right_widget.setFixedWidth(300)

        layout = QHBoxLayout()
        layout.addWidget(self.video_label, stretch=1)
        layout.addWidget(right_widget)
        main_widget.setLayout(layout)

    def append_log(self, msg):
        self.log_output.append(msg)

    def start_camera(self):
        # disable button, open capture, then warm up for 2s
        self.start_button.setEnabled(False)
        self.append_log("Initializing camera...")
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.append_log("Please wait, camera warming up…")
        QTimer.singleShot(2000, self._begin_stream)

    def _begin_stream(self):
        if self.capture and self.capture.isOpened():
            self.timer.start(30)
            self.append_log("Camera started.")
        else:
            self.append_log("Failed to open camera.")
        self.start_button.setEnabled(True)

    def stop_camera(self):
        self.timer.stop()
        if self.capture:
            self.capture.release()
            self.capture = None
        self.video_label.clear()
        self.append_log("Camera stopped.")

    def send_command_to_esp32(self, command):
        try:
            ip = self.ip_input.text()
            port = int(self.port_input.text())
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(command.encode(), (ip, port))
            self.append_log(f"Sent command: {command}")
        except Exception as e:
            self.append_log(f"Error sending command: {e}")

    def update_frame(self):
        if not self.capture:
            return

        ret, frame = self.capture.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # --- draw your two red boxes ---
        top_y    = self.top_slider.value()
        bot_y    = self.bottom_slider.value()
        box_h    = 40
        cv2.rectangle(frame, (0, top_y), (w, top_y + box_h),   (0,0,255), 2)
        cv2.rectangle(frame, (0, bot_y), (w, bot_y + box_h),   (0,0,255), 2)

        # --- hand tracking & commands ---
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.hands.process(rgb)
        if res.multi_hand_landmarks:
            lm = res.multi_hand_landmarks[0].landmark
            wrist_y    = lm[0].y * h
            index_y    = lm[8].y * h
            # forward / backward / stop logic
            if top_y < wrist_y < top_y + box_h:
                cmd = "FORWARD"
            elif bot_y < wrist_y < bot_y + box_h:
                cmd = "BACKWARD"
            elif abs(wrist_y - index_y) > 80:
                cmd = "STOP"
            else:
                cmd = None

            if cmd and cmd != self.command_sent:
                self.send_command_to_esp32(cmd)
                self.command_sent = cmd

            mp_drawing.draw_landmarks(frame, res.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

        # --- scale & show ---
        rgb2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb2.data, w, h, rgb2.strides[0], QImage.Format_RGB888)
        pix  = QPixmap.fromImage(qimg)
        pix  = pix.scaled(
            self.video_label.width(),
            self.video_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.video_label.setPixmap(pix)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
