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

class SimpleGestureWindow(QMainWindow):
    """
    A simplified GUI version of the gesture controller.
    
    This example demonstrates a cleaner, more user-friendly interface
    for gesture control without the complexity of the full application.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Robot Gesture Controller")
        self.setGeometry(100, 100, 1000, 600)

        self.capture = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.hands = mp_hands.Hands(max_num_hands=1)
        self.last_command = ""
        
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Video display (left side)
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.video_label.setScaledContents(True)
        self.video_label.setStyleSheet("border: 2px solid #333; background-color: #000;")
        self.video_label.setMinimumSize(480, 360)

        # Control panel (right side)
        control_widget = QWidget()
        control_layout = QVBoxLayout()
        
        # Connection settings
        connection_group = self.create_connection_group()
        control_layout.addWidget(connection_group)
        
        # Zone adjustment
        zone_group = self.create_zone_group()
        control_layout.addWidget(zone_group)
        
        # Control buttons
        button_group = self.create_button_group()
        control_layout.addWidget(button_group)
        
        # Status display
        status_group = self.create_status_group()
        control_layout.addWidget(status_group)
        
        control_widget.setLayout(control_layout)
        control_widget.setFixedWidth(300)

        # Main layout
        layout = QHBoxLayout()
        layout.addWidget(self.video_label, stretch=1)
        layout.addWidget(control_widget)
        main_widget.setLayout(layout)

    def create_connection_group(self):
        """Create connection settings group."""
        group = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>ESP32 Connection</b>"))
        
        layout.addWidget(QLabel("IP Address:"))
        self.ip_input = QLineEdit("192.168.137.205")
        layout.addWidget(self.ip_input)
        
        layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit("4210")
        layout.addWidget(self.port_input)
        
        group.setLayout(layout)
        return group

    def create_zone_group(self):
        """Create zone adjustment group."""
        group = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>Control Zones</b>"))
        
        layout.addWidget(QLabel("Top Zone Height:"))
        self.top_slider = QSlider(Qt.Horizontal)
        self.top_slider.setRange(50, 300)
        self.top_slider.setValue(150)
        layout.addWidget(self.top_slider)
        
        layout.addWidget(QLabel("Bottom Zone Height:"))
        self.bottom_slider = QSlider(Qt.Horizontal)
        self.bottom_slider.setRange(50, 300)
        self.bottom_slider.setValue(150)
        layout.addWidget(self.bottom_slider)
        
        group.setLayout(layout)
        return group

    def create_button_group(self):
        """Create control buttons group."""
        group = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>Camera Control</b>"))
        
        self.start_button = QPushButton("▶ Start Camera")
        self.start_button.clicked.connect(self.start_camera)
        self.start_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px; }")
        
        self.stop_button = QPushButton("⏹ Stop Camera")
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 8px; }")
        self.stop_button.setEnabled(False)
        
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        
        group.setLayout(layout)
        return group

    def create_status_group(self):
        """Create status display group."""
        group = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>Status & Commands</b>"))
        
        # Current command display
        self.command_label = QLabel("Command: STOP")
        self.command_label.setStyleSheet("QLabel { font-size: 16px; font-weight: bold; color: #2196F3; }")
        layout.addWidget(self.command_label)
        
        # Log output
        layout.addWidget(QLabel("Activity Log:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        self.log_output.setStyleSheet("QTextEdit { font-family: 'Courier New'; font-size: 9px; }")
        layout.addWidget(self.log_output)
        
        group.setLayout(layout)
        return group

    def append_log(self, msg):
        """Add message to log with timestamp."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {msg}")
        
        # Auto-scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def start_camera(self):
        """Initialize and start camera capture."""
        self.start_button.setEnabled(False)
        self.append_log("Initializing camera...")
        
        self.capture = cv2.VideoCapture(0)
        if self.capture.isOpened():
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.timer.start(50)  # 20 FPS
            self.stop_button.setEnabled(True)
            self.append_log("Camera started successfully")
            
            # Test ESP32 connection
            self.test_connection()
        else:
            self.append_log("ERROR: Failed to open camera")
            self.start_button.setEnabled(True)

    def test_connection(self):
        """Test connection to ESP32."""
        try:
            ip = self.ip_input.text()
            port = int(self.port_input.text())
            
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(2)
                sock.sendto(b"TEST", (ip, port))
                self.append_log(f"✓ Connected to ESP32 at {ip}:{port}")
        except Exception as e:
            self.append_log(f"⚠ ESP32 connection test failed: {str(e)[:50]}")

    def stop_camera(self):
        """Stop camera capture and cleanup."""
        self.timer.stop()
        
        if self.capture:
            self.capture.release()
            self.capture = None
        
        self.video_label.clear()
        self.video_label.setText("Camera Stopped")
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.append_log("Camera stopped")
        
        # Send stop command
        self.send_command_to_esp32("STOP")

    def send_command_to_esp32(self, command):
        """Send UDP command to ESP32."""
        try:
            ip = self.ip_input.text()
            port = int(self.port_input.text())
            
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(1)
                sock.sendto(command.encode(), (ip, port))
                
            if command != self.last_command:
                self.append_log(f"→ Sent: {command}")
                self.last_command = command
                
        except Exception as e:
            if command != "STOP":  # Don't log stop command failures
                self.append_log(f"✗ Send failed: {str(e)[:40]}")

    def update_frame(self):
        """Process camera frame and update display."""
        if not self.capture:
            return

        ret, frame = self.capture.read()
        if not ret:
            return

        # Mirror the frame
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Get zone settings
        top_height = self.top_slider.value()
        bottom_height = self.bottom_slider.value()
        
        # Define zones
        top_zone = (w//4, 0, w//2, top_height)
        bottom_zone = (w//4, h - bottom_height, w//2, bottom_height)

        # Process hand detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb_frame)
        
        command = "STOP"
        
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Draw hand landmarks
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Get hand position
                landmarks = hand_landmarks.landmark
                wrist = landmarks[0]
                
                wrist_x = int(wrist.x * w)
                wrist_y = int(wrist.y * h)
                
                # Zone detection
                if top_zone[0] < wrist_x < top_zone[0] + top_zone[2] and wrist_y < top_zone[3]:
                    command = "FORWARD"
                elif bottom_zone[0] < wrist_x < bottom_zone[0] + bottom_zone[2] and wrist_y > bottom_zone[1]:
                    command = "BACKWARD"
                
                # Draw wrist indicator
                cv2.circle(frame, (wrist_x, wrist_y), 8, (255, 255, 0), -1)

        # Draw control zones
        cv2.rectangle(frame, (top_zone[0], top_zone[1]), 
                     (top_zone[0] + top_zone[2], top_zone[3]), (0, 255, 0), 2)
        cv2.putText(frame, "FORWARD", (top_zone[0], top_zone[3] + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.rectangle(frame, (bottom_zone[0], bottom_zone[1]), 
                     (bottom_zone[0] + bottom_zone[2], h), (0, 0, 255), 2)
        cv2.putText(frame, "BACKWARD", (bottom_zone[0], bottom_zone[1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Display current command
        command_colors = {
            "FORWARD": (0, 255, 0),
            "BACKWARD": (0, 0, 255),
            "STOP": (128, 128, 128)
        }
        
        color = command_colors.get(command, (255, 255, 255))
        cv2.putText(frame, f"Command: {command}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Send command and update UI
        self.send_command_to_esp32(command)
        self.command_label.setText(f"Command: {command}")
        
        # Update command label color
        label_colors = {
            "FORWARD": "#4CAF50",
            "BACKWARD": "#f44336", 
            "STOP": "#9E9E9E"
        }
        label_color = label_colors.get(command, "#2196F3")
        self.command_label.setStyleSheet(f"QLabel {{ font-size: 16px; font-weight: bold; color: {label_color}; }}")

        # Convert to Qt format and display
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qt_image = QImage(rgb_image.data, w, h, rgb_image.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        # Scale to fit display
        scaled_pixmap = pixmap.scaled(
            self.video_label.width(),
            self.video_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.video_label.setPixmap(scaled_pixmap)

    def closeEvent(self, event):
        """Handle window close event."""
        if self.capture:
            self.stop_camera()
        event.accept()

def main():
    """Main function to run the simple gesture controller."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QWidget {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            margin: 2px;
        }
        QPushButton {
            border: 2px solid #ccc;
            border-radius: 6px;
            padding: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QLineEdit {
            border: 2px solid #ccc;
            padding: 4px;
            border-radius: 4px;
        }
        QSlider {
            border: none;
        }
    """)
    
    window = SimpleGestureWindow()
    window.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())