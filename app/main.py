import cv2
import mediapipe as mp
import math
import socket
import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QSlider, QGroupBox, QTabWidget,
                             QSpinBox, QCheckBox, QMessageBox, QFileDialog, QGridLayout)
from PyQt5.QtGui import QImage, QPixmap, QIcon, QColor, QPainter, QPen, QFont
from PyQt5.QtCore import Qt, QTimer, QRect, QThread, pyqtSignal, QSettings

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

# Default settings
DEFAULT_SETTINGS = {
    'network': {
        'ip_address': '192.168.137.205',
        'port': 4210
    },
    'detection': {
        'min_detection_confidence': 0.7,
        'min_tracking_confidence': 0.7
    },
    'zones': {
        'forward_zone': {'x': 0.4, 'y': 0.0, 'width': 0.2, 'height': 0.3},
        'backward_zone': {'x': 0.4, 'y': 0.7, 'width': 0.2, 'height': 0.3},
        'turn_angle_threshold': 20
    }
}

# Load settings
def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        return DEFAULT_SETTINGS
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS

# Save settings
def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

# Camera thread for processing frames
class CameraThread(QThread):
    update_frame = pyqtSignal(QImage)
    update_command = pyqtSignal(str)
    initialization_complete = pyqtSignal(bool)
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.running = False
        self.command = "STOP"
        
        # Will initialize MediaPipe in the thread to avoid blocking UI
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = None
        
        # Initialize camera
        self.cap = None
        
    def update_settings(self, settings):
        self.settings = settings
        # Update MediaPipe settings if hands object exists
        if self.hands is not None:
            self.hands.close()
            self.hands = self.mp_hands.Hands(
                min_detection_confidence=self.settings['detection']['min_detection_confidence'],
                min_tracking_confidence=self.settings['detection']['min_tracking_confidence']
            )
    
    def run(self):
        try:
            # Initialize MediaPipe Hands in the thread to avoid blocking UI
            self.hands = self.mp_hands.Hands(
                min_detection_confidence=self.settings['detection']['min_detection_confidence'],
                min_tracking_confidence=self.settings['detection']['min_tracking_confidence']
            )
            
            # Initialize camera with timeout
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Could not open camera.")
                self.initialization_complete.emit(False)
                return
                
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            self.running = True
            self.initialization_complete.emit(True)
            
            while self.running and self.cap is not None and self.cap.isOpened():
                try:
                    # Check if thread should still be running before processing
                    if not self.running:
                        break
                        
                    ret, frame = self.cap.read()
                    if not ret:
                        print("Failed to read frame from camera")
                        self.msleep(100)  # Short delay before retry
                        continue
                    
                    # Check again if thread should still be running
                    if not self.running:
                        break
                        
                    # Flip frame for a mirrored effect
                    frame = cv2.flip(frame, 1)
                    height, width, channels = frame.shape
                    
                    # Process the frame with MediaPipe - with error handling
                    try:
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        if self.hands is None:  # Ensure hands object exists
                            self.hands = self.mp_hands.Hands(
                                min_detection_confidence=self.settings['detection']['min_detection_confidence'],
                                min_tracking_confidence=self.settings['detection']['min_tracking_confidence']
                            )
                        result = self.hands.process(rgb_frame)
                    except Exception as e:
                        print(f"MediaPipe processing error: {e}")
                        self.msleep(100)
                        continue
                    
                    # Default command
                    self.command = "STOP"
                    
                    # Get zone coordinates from settings - with validation
                    try:
                        forward_zone = self.settings['zones']['forward_zone']
                        backward_zone = self.settings['zones']['backward_zone']
                        turn_threshold = self.settings['zones']['turn_angle_threshold']
                        
                        # Calculate actual pixel coordinates for zones
                        forward_rect = (
                            int(forward_zone['x'] * width),
                            int(forward_zone['y'] * height),
                            int(forward_zone['width'] * width),
                            int(forward_zone['height'] * height)
                        )
                        
                        backward_rect = (
                            int(backward_zone['x'] * width),
                            int(backward_zone['y'] * height),
                            int(backward_zone['width'] * width),
                            int(backward_zone['height'] * height)
                        )
                    except (KeyError, TypeError) as e:
                        print(f"Zone settings error: {e}")
                        # Use default values if settings are corrupted
                        forward_rect = (int(0.4 * width), 0, int(0.2 * width), int(0.3 * height))
                        backward_rect = (int(0.4 * width), int(0.7 * height), int(0.2 * width), int(0.3 * height))
                        turn_threshold = 20
                    
                    # Draw the control zones - with bounds checking
                    try:
                        cv2.rectangle(frame, 
                                    (forward_rect[0], forward_rect[1]), 
                                    (forward_rect[0] + forward_rect[2], forward_rect[1] + forward_rect[3]), 
                                    (0, 0, 255), 2)
                        cv2.putText(frame, "FORWARD", (forward_rect[0], max(forward_rect[1] - 10, 10)), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                        cv2.rectangle(frame, 
                                    (backward_rect[0], backward_rect[1]), 
                                    (backward_rect[0] + backward_rect[2], backward_rect[1] + backward_rect[3]), 
                                    (0, 0, 255), 2)
                        cv2.putText(frame, "BACKWARD", (backward_rect[0], max(backward_rect[1] - 10, 10)), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    except Exception as e:
                        print(f"Drawing error: {e}")
                    
                    # Process hand landmarks with error handling
                    if result and result.multi_hand_landmarks:
                        for hand_landmarks in result.multi_hand_landmarks:
                            try:
                                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                                landmarks = hand_landmarks.landmark
                                
                                # Get the wrist and middle MCP for angle calculation
                                wrist = landmarks[0]
                                middle_mcp = landmarks[9]
                                
                                # Calculate rotation angle for turning
                                angle = math.atan2(wrist.y - middle_mcp.y, wrist.x - middle_mcp.x)
                                angle = math.degrees(angle) - 90
                                if angle <= -180:
                                    angle += 360
                                elif angle > 180:
                                    angle -= 360
                                
                                # Determine if landmarks[9] and landmarks[13] are in the zones
                                index_mcp = landmarks[9]
                                middle_pip = landmarks[13]
                                
                                # Convert normalized coordinates to pixel coordinates
                                index_mcp_x = int(index_mcp.x * width)
                                index_mcp_y = int(index_mcp.y * height)
                                middle_pip_x = int(middle_pip.x * width)
                                middle_pip_y = int(middle_pip.y * height)
                                
                                # Check if the hand is inside the forward zone
                                if (forward_rect[0] < index_mcp_x < forward_rect[0] + forward_rect[2] and
                                    forward_rect[1] < index_mcp_y < forward_rect[1] + forward_rect[3] and
                                    forward_rect[0] < middle_pip_x < forward_rect[0] + forward_rect[2] and
                                    forward_rect[1] < middle_pip_y < forward_rect[1] + forward_rect[3]):
                                    self.command = "FORWARD"
                                
                                # Check if the hand is inside the backward zone
                                elif (backward_rect[0] < index_mcp_x < backward_rect[0] + backward_rect[2] and
                                    backward_rect[1] < index_mcp_y < backward_rect[1] + backward_rect[3] and
                                    backward_rect[0] < middle_pip_x < backward_rect[0] + backward_rect[2] and
                                    backward_rect[1] < middle_pip_y < backward_rect[1] + backward_rect[3]):
                                    self.command = "BACKWARD"
                                
                                # Check for left or right turns based on angle
                                elif angle > turn_threshold:
                                    self.command = "RIGHT"
                                elif angle < -turn_threshold:
                                    self.command = "LEFT"
                                
                                # Display angle on frame
                                cv2.putText(frame, f"Angle: {angle:.1f}", (50, 100), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            except Exception as e:
                                print(f"Hand landmark processing error: {e}")
                    
                    # Display the command on the frame
                    try:
                        cv2.putText(frame, f"Command: {self.command}", (50, 50), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    except Exception as e:
                        print(f"Command display error: {e}")
                    
                    # Send the command to ESP32 - only if still running
                    if self.running:
                        try:
                            self.send_command_to_esp32(self.command)
                        except Exception as e:
                            print(f"Command sending error: {e}")
                    
                    # Emit signals only if still running
                    if self.running:
                        try:
                            self.update_command.emit(self.command)
                            
                            # Convert the frame to QImage and emit signal
                            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            h, w, ch = rgb_image.shape
                            bytes_per_line = ch * w
                            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                            
                            # Only emit if image is valid
                            if not qt_image.isNull():
                                self.update_frame.emit(qt_image)
                        except Exception as e:
                            print(f"Signal emission error: {e}")
                except Exception as e:
                    print(f"Error processing frame: {e}")
                    if self.running:
                        # Small delay to prevent CPU overload in case of errors
                        self.msleep(100)
        except Exception as e:
            print(f"Camera thread error: {e}")
            self.initialization_complete.emit(False)
        finally:
            # Ensure resources are properly released
            self.stop()
    
    def send_command_to_esp32(self, command):
        try:
            # Create a UDP socket
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(0.5)  # Set a timeout to prevent blocking
                # Send the command over UDP
                sock.sendto(command.encode(), 
                           (self.settings['network']['ip_address'], 
                            self.settings['network']['port']))
        except socket.timeout:
            print("UDP socket timeout")
        except Exception as e:
            print(f"Failed to send command: {e}")
    
    def stop(self):
        self.running = False
        # Release resources in a safe way
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if self.hands is not None:
            self.hands.close()
            self.hands = None

# Zone Editor Widget
class ZoneEditorWidget(QWidget):
    zone_updated = pyqtSignal(dict)
    
    def __init__(self, zone_name, zone_data, parent=None):
        super().__init__(parent)
        self.zone_name = zone_name
        self.zone_data = zone_data
        self.initUI()
    
    def initUI(self):
        layout = QGridLayout()
        
        # X position
        layout.addWidget(QLabel("X Position:"), 0, 0)
        self.x_slider = QSlider(Qt.Horizontal)
        self.x_slider.setRange(0, 100)
        self.x_slider.setValue(int(self.zone_data['x'] * 100))
        self.x_slider.valueChanged.connect(self.update_zone)
        layout.addWidget(self.x_slider, 0, 1)
        self.x_value = QLabel(f"{self.zone_data['x']:.2f}")
        layout.addWidget(self.x_value, 0, 2)
        
        # Y position
        layout.addWidget(QLabel("Y Position:"), 1, 0)
        self.y_slider = QSlider(Qt.Horizontal)
        self.y_slider.setRange(0, 100)
        self.y_slider.setValue(int(self.zone_data['y'] * 100))
        self.y_slider.valueChanged.connect(self.update_zone)
        layout.addWidget(self.y_slider, 1, 1)
        self.y_value = QLabel(f"{self.zone_data['y']:.2f}")
        layout.addWidget(self.y_value, 1, 2)
        
        # Width
        layout.addWidget(QLabel("Width:"), 2, 0)
        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setRange(5, 50)  # 5% to 50% of screen width
        self.width_slider.setValue(int(self.zone_data['width'] * 100))
        self.width_slider.valueChanged.connect(self.update_zone)
        layout.addWidget(self.width_slider, 2, 1)
        self.width_value = QLabel(f"{self.zone_data['width']:.2f}")
        layout.addWidget(self.width_value, 2, 2)
        
        # Height
        layout.addWidget(QLabel("Height:"), 3, 0)
        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setRange(5, 50)  # 5% to 50% of screen height
        self.height_slider.setValue(int(self.zone_data['height'] * 100))
        self.height_slider.valueChanged.connect(self.update_zone)
        layout.addWidget(self.height_slider, 3, 1)
        self.height_value = QLabel(f"{self.zone_data['height']:.2f}")
        layout.addWidget(self.height_value, 3, 2)
        
        self.setLayout(layout)
    
    def update_zone(self):
        self.zone_data = {
            'x': self.x_slider.value() / 100,
            'y': self.y_slider.value() / 100,
            'width': self.width_slider.value() / 100,
            'height': self.height_slider.value() / 100
        }
        
        # Update labels
        self.x_value.setText(f"{self.zone_data['x']:.2f}")
        self.y_value.setText(f"{self.zone_data['y']:.2f}")
        self.width_value.setText(f"{self.zone_data['width']:.2f}")
        self.height_value.setText(f"{self.zone_data['height']:.2f}")
        
        # Emit signal with updated zone data
        self.zone_updated.emit({self.zone_name: self.zone_data})

# Main Window
class GestureControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.camera_thread = None
        self.resize_timer = None
        self.initUI()
        
    def resizeEvent(self, event):
        # Handle window resize events safely
        super().resizeEvent(event)
        
        # Use a timer to prevent multiple resize operations
        if self.resize_timer is None:
            self.resize_timer = QTimer()
            self.resize_timer.setSingleShot(True)
            self.resize_timer.timeout.connect(self.on_resize_timeout)
        
        self.resize_timer.start(200)  # 200ms delay
    
    def on_resize_timeout(self):
        # Update camera feed display after resize
        if self.camera_thread is not None and self.camera_thread.isRunning():
            # Just update the UI, no need to restart the camera
            pass
    
    def initUI(self):
        self.setWindowTitle("Gesture Control Application")
        self.setGeometry(100, 100, 1280, 800)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left panel - Camera feed
        self.camera_feed = QLabel()
        self.camera_feed.setMinimumSize(640, 480)
        self.camera_feed.setAlignment(Qt.AlignCenter)
        self.camera_feed.setStyleSheet("border: 2px solid #cccccc; background-color: #f0f0f0;")
        
        # Command display
        self.command_label = QLabel("Command: STOP")
        self.command_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #009900;")
        
        # Camera controls
        camera_control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.start_camera)
        
        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setEnabled(False)
        
        camera_control_layout.addWidget(self.start_button)
        camera_control_layout.addWidget(self.stop_button)
        
        # Left panel layout
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(self.camera_feed)
        left_layout.addWidget(self.command_label)
        left_layout.addLayout(camera_control_layout)
        
        # Right panel - Settings
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Settings tabs
        settings_tabs = QTabWidget()
        
        # Network settings tab
        network_tab = QWidget()
        network_layout = QVBoxLayout(network_tab)
        
        # IP Address
        ip_group = QGroupBox("ESP32 IP Address")
        ip_layout = QHBoxLayout()
        self.ip_input = QLineEdit(self.settings['network']['ip_address'])
        ip_layout.addWidget(self.ip_input)
        ip_group.setLayout(ip_layout)
        
        # Port
        port_group = QGroupBox("ESP32 Port")
        port_layout = QHBoxLayout()
        self.port_input = QSpinBox()
        self.port_input.setRange(1000, 65535)
        self.port_input.setValue(self.settings['network']['port'])
        port_layout.addWidget(self.port_input)
        port_group.setLayout(port_layout)
        
        # Add to network layout
        network_layout.addWidget(ip_group)
        network_layout.addWidget(port_group)
        network_layout.addStretch()
        
        # Detection settings tab
        detection_tab = QWidget()
        detection_layout = QVBoxLayout(detection_tab)
        
        # Detection confidence
        detection_group = QGroupBox("Hand Detection Confidence")
        detection_conf_layout = QVBoxLayout()
        
        detection_conf_layout.addWidget(QLabel("Min Detection Confidence:"))
        self.detection_conf_slider = QSlider(Qt.Horizontal)
        self.detection_conf_slider.setRange(1, 10)
        self.detection_conf_slider.setValue(int(self.settings['detection']['min_detection_confidence'] * 10))
        detection_conf_layout.addWidget(self.detection_conf_slider)
        self.detection_conf_value = QLabel(f"{self.settings['detection']['min_detection_confidence']:.1f}")
        detection_conf_layout.addWidget(self.detection_conf_value)
        
        detection_conf_layout.addWidget(QLabel("Min Tracking Confidence:"))
        self.tracking_conf_slider = QSlider(Qt.Horizontal)
        self.tracking_conf_slider.setRange(1, 10)
        self.tracking_conf_slider.setValue(int(self.settings['detection']['min_tracking_confidence'] * 10))
        detection_conf_layout.addWidget(self.tracking_conf_slider)
        self.tracking_conf_value = QLabel(f"{self.settings['detection']['min_tracking_confidence']:.1f}")
        detection_conf_layout.addWidget(self.tracking_conf_value)
        
        detection_group.setLayout(detection_conf_layout)
        detection_layout.addWidget(detection_group)
        
        # Turn angle threshold
        turn_group = QGroupBox("Turn Angle Threshold")
        turn_layout = QVBoxLayout()
        self.turn_threshold_slider = QSlider(Qt.Horizontal)
        self.turn_threshold_slider.setRange(5, 45)
        self.turn_threshold_slider.setValue(self.settings['zones']['turn_angle_threshold'])
        turn_layout.addWidget(self.turn_threshold_slider)
        self.turn_threshold_value = QLabel(f"{self.settings['zones']['turn_angle_threshold']}°")
        turn_layout.addWidget(self.turn_threshold_value)
        turn_group.setLayout(turn_layout)
        
        detection_layout.addWidget(turn_group)
        detection_layout.addStretch()
        
        # Connect sliders to update functions
        self.detection_conf_slider.valueChanged.connect(self.update_detection_conf)
        self.tracking_conf_slider.valueChanged.connect(self.update_tracking_conf)
        self.turn_threshold_slider.valueChanged.connect(self.update_turn_threshold)
        
        # Zones settings tab
        zones_tab = QWidget()
        zones_layout = QVBoxLayout(zones_tab)
        
        # Forward zone editor
        forward_group = QGroupBox("Forward Zone")
        self.forward_zone_editor = ZoneEditorWidget(
            'forward_zone', self.settings['zones']['forward_zone'])
        forward_layout = QVBoxLayout()
        forward_layout.addWidget(self.forward_zone_editor)
        forward_group.setLayout(forward_layout)
        
        # Backward zone editor
        backward_group = QGroupBox("Backward Zone")
        self.backward_zone_editor = ZoneEditorWidget(
            'backward_zone', self.settings['zones']['backward_zone'])
        backward_layout = QVBoxLayout()
        backward_layout.addWidget(self.backward_zone_editor)
        backward_group.setLayout(backward_layout)
        
        # Connect zone editors to update function
        self.forward_zone_editor.zone_updated.connect(self.update_zone)
        self.backward_zone_editor.zone_updated.connect(self.update_zone)
        
        zones_layout.addWidget(forward_group)
        zones_layout.addWidget(backward_group)
        zones_layout.addStretch()
        
        # Add tabs to settings
        settings_tabs.addTab(network_tab, "Network")
        settings_tabs.addTab(detection_tab, "Detection")
        settings_tabs.addTab(zones_tab, "Control Zones")
        
        # Save settings button
        self.save_settings_button = QPushButton("Save Settings")
        self.save_settings_button.clicked.connect(self.save_current_settings)
        
        # Reset settings button
        self.reset_settings_button = QPushButton("Reset to Defaults")
        self.reset_settings_button.clicked.connect(self.reset_to_defaults)
        
        # Add settings components to right panel
        right_layout.addWidget(settings_tabs)
        
        # Settings buttons layout
        settings_buttons_layout = QHBoxLayout()
        settings_buttons_layout.addWidget(self.save_settings_button)
        settings_buttons_layout.addWidget(self.reset_settings_button)
        right_layout.addLayout(settings_buttons_layout)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 2)  # 2/3 of width
        main_layout.addWidget(right_panel, 1)  # 1/3 of width
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def start_camera(self):
        # Update network settings before starting
        self.settings['network']['ip_address'] = self.ip_input.text()
        self.settings['network']['port'] = self.port_input.value()
        
        # Show loading message in camera feed
        loading_pixmap = QPixmap(self.camera_feed.width(), self.camera_feed.height())
        loading_pixmap.fill(QColor('#f0f0f0'))
        painter = QPainter(loading_pixmap)
        painter.setPen(QPen(QColor('#009900'), 2))
        font = QFont('Arial', 20)
        painter.setFont(font)
        painter.drawText(loading_pixmap.rect(), Qt.AlignCenter, "Initializing camera...\nPlease wait")
        painter.end()
        self.camera_feed.setPixmap(loading_pixmap)
        self.command_label.setText("Command: INITIALIZING...")
        QApplication.processEvents()
        
        # Disable start button to prevent multiple clicks
        self.start_button.setEnabled(False)
        
        # Disable all parameter controls while camera is running
        self.ip_input.setEnabled(False)
        self.port_input.setEnabled(False)
        self.detection_conf_slider.setEnabled(False)
        self.tracking_conf_slider.setEnabled(False)
        self.turn_threshold_slider.setEnabled(False)
        self.forward_zone_editor.setEnabled(False)
        self.backward_zone_editor.setEnabled(False)
        self.save_settings_button.setEnabled(False)
        self.reset_settings_button.setEnabled(False)
        
        # Create and start camera thread
        self.camera_thread = CameraThread(self.settings)
        self.camera_thread.update_frame.connect(self.update_frame)
        self.camera_thread.update_command.connect(self.update_command)
        self.camera_thread.initialization_complete.connect(self.on_camera_initialized)
        self.camera_thread.start()
    
    def stop_camera(self):
        if self.camera_thread is not None:
            # Disable stop button to prevent multiple clicks
            self.stop_button.setEnabled(False)
            self.command_label.setText("Command: STOPPING...")
            QApplication.processEvents()
            
            # Stop the thread safely
            try:
                self.camera_thread.running = False  # Signal thread to stop first
                QApplication.processEvents()  # Process events to allow thread to respond
                self.camera_thread.stop()
                self.camera_thread.wait(3000)  # Wait with timeout to prevent hanging
                if self.camera_thread.isRunning():
                    print("Warning: Camera thread did not terminate properly")
                self.camera_thread = None
            except Exception as e:
                print(f"Error stopping camera thread: {e}")
            
            # Clear the camera feed
            try:
                blank_pixmap = QPixmap(self.camera_feed.width(), self.camera_feed.height())
                blank_pixmap.fill(QColor('#f0f0f0'))
                self.camera_feed.setPixmap(blank_pixmap)
                self.command_label.setText("Command: STOPPED")
            except Exception as e:
                print(f"Error clearing camera feed: {e}")
        
        # Update UI
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Re-enable all parameter controls
        self.ip_input.setEnabled(True)
        self.port_input.setEnabled(True)
        self.detection_conf_slider.setEnabled(True)
        self.tracking_conf_slider.setEnabled(True)
        self.turn_threshold_slider.setEnabled(True)
        self.forward_zone_editor.setEnabled(True)
        self.backward_zone_editor.setEnabled(True)
        self.save_settings_button.setEnabled(True)
        self.reset_settings_button.setEnabled(True)
    
    def update_frame(self, image):
        try:
            if not self.camera_feed or not image or image.isNull():
                return
                
            pixmap = QPixmap.fromImage(image)
            self.camera_feed.setPixmap(pixmap.scaled(self.camera_feed.width(), 
                                                    self.camera_feed.height(), 
                                                    Qt.KeepAspectRatio))
        except Exception as e:
            print(f"Error updating frame: {e}")
    
    def update_command(self, command):
        self.command_label.setText(f"Command: {command}")
    
    def update_detection_conf(self):
        value = self.detection_conf_slider.value() / 10
        self.settings['detection']['min_detection_confidence'] = value
        self.detection_conf_value.setText(f"{value:.1f}")
        if self.camera_thread is not None:
            self.camera_thread.update_settings(self.settings)
    
    def update_tracking_conf(self):
        value = self.tracking_conf_slider.value() / 10
        self.settings['detection']['min_tracking_confidence'] = value
        self.tracking_conf_value.setText(f"{value:.1f}")
        if self.camera_thread is not None:
            self.camera_thread.update_settings(self.settings)
    
    def update_turn_threshold(self):
        value = self.turn_threshold_slider.value()
        self.settings['zones']['turn_angle_threshold'] = value
        self.turn_threshold_value.setText(f"{value}°")
        if self.camera_thread is not None:
            self.camera_thread.update_settings(self.settings)
    
    def update_zone(self, zone_data):
        # Update the settings with the new zone data
        for zone_name, zone_values in zone_data.items():
            self.settings['zones'][zone_name] = zone_values
        
        # Update camera thread if running
        if self.camera_thread is not None:
            self.camera_thread.update_settings(self.settings)
    
    def save_current_settings(self):
        # Update network settings from input fields
        self.settings['network']['ip_address'] = self.ip_input.text()
        self.settings['network']['port'] = self.port_input.value()
        
        # Save settings to file
        save_settings(self.settings)
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")
    
    def reset_to_defaults(self):
        # Ask for confirmation
        reply = QMessageBox.question(self, "Reset Settings", 
                                    "Are you sure you want to reset all settings to defaults?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Reset to defaults
            self.settings = DEFAULT_SETTINGS.copy()
            save_settings(self.settings)
            
            # Update UI with default values
            self.ip_input.setText(self.settings['network']['ip_address'])
            self.port_input.setValue(self.settings['network']['port'])
            
            self.detection_conf_slider.setValue(int(self.settings['detection']['min_detection_confidence'] * 10))
            self.tracking_conf_slider.setValue(int(self.settings['detection']['min_tracking_confidence'] * 10))
            self.turn_threshold_slider.setValue(self.settings['zones']['turn_angle_threshold'])
            
            # Update zone editors
            self.forward_zone_editor.zone_data = self.settings['zones']['forward_zone']
            self.backward_zone_editor.zone_data = self.settings['zones']['backward_zone']
            
            # Refresh UI
            self.forward_zone_editor.x_slider.setValue(int(self.settings['zones']['forward_zone']['x'] * 100))
            self.forward_zone_editor.y_slider.setValue(int(self.settings['zones']['forward_zone']['y'] * 100))
            self.forward_zone_editor.width_slider.setValue(int(self.settings['zones']['forward_zone']['width'] * 100))
            self.forward_zone_editor.height_slider.setValue(int(self.settings['zones']['forward_zone']['height'] * 100))
            
            self.backward_zone_editor.x_slider.setValue(int(self.settings['zones']['backward_zone']['x'] * 100))
            self.backward_zone_editor.y_slider.setValue(int(self.settings['zones']['backward_zone']['y'] * 100))
            self.backward_zone_editor.width_slider.setValue(int(self.settings['zones']['backward_zone']['width'] * 100))
            self.backward_zone_editor.height_slider.setValue(int(self.settings['zones']['backward_zone']['height'] * 100))
            
            # Update camera thread if running
            if self.camera_thread is not None:
                self.camera_thread.update_settings(self.settings)
            
            QMessageBox.information(self, "Settings Reset", "All settings have been reset to defaults.")
    
    def on_camera_initialized(self, success):
        if success:
            # Enable stop button once camera is initialized
            self.stop_button.setEnabled(True)
        else:
            # Show error message and reset UI if initialization failed
            QMessageBox.critical(self, "Camera Error", "Failed to initialize camera. Please check your camera connection.")
            # Re-enable all parameter controls if initialization failed
            self.ip_input.setEnabled(True)
            self.port_input.setEnabled(True)
            self.detection_conf_slider.setEnabled(True)
            self.tracking_conf_slider.setEnabled(True)
            self.turn_threshold_slider.setEnabled(True)
            self.forward_zone_editor.setEnabled(True)
            self.backward_zone_editor.setEnabled(True)
            self.save_settings_button.setEnabled(True)
            self.reset_settings_button.setEnabled(True)
            self.stop_camera()
    
    def closeEvent(self, event):
        # Stop camera thread when closing the application
        self.stop_camera()
        event.accept()

# Main application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GestureControlApp()
    window.show()
    sys.exit(app.exec_())