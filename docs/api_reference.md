# API Reference

This document provides a comprehensive reference for the gesture-controlled robot API.

## Core Classes

### GestureController

The main class for simple gesture control.

#### Constructor

```python
GestureController(esp32_ip="192.168.137.205", esp32_port=4210)
```

**Parameters:**
- `esp32_ip` (str): IP address of the ESP32 device
- `esp32_port` (int): UDP port for communication

**Example:**
```python
from src.gesture_control_simple import GestureController

controller = GestureController("192.168.1.100", 4210)
controller.run()
```

#### Methods

##### `process_frame(frame)`
Process a single video frame and return the detected command.

**Parameters:**
- `frame` (numpy.ndarray): Input video frame from camera

**Returns:**
- `tuple`: (processed_frame, command)
  - `processed_frame` (numpy.ndarray): Frame with overlays and annotations
  - `command` (str): Detected command ("FORWARD", "BACKWARD", "LEFT", "RIGHT", "STOP")

##### `send_command_to_esp32(command)`
Send a UDP command to the ESP32.

**Parameters:**
- `command` (str): Command string to send

**Raises:**
- `Exception`: If UDP communication fails

##### `run()`
Start the main gesture control loop.

**Example:**
```python
controller = GestureController()
controller.run()  # Runs until 'q' is pressed
```

##### `cleanup()`
Clean up resources and stop the controller.

### GestureControlApp (GUI)

The PyQt5-based GUI application for advanced control.

#### Constructor

```python
GestureControlApp()
```

Loads settings from `settings.json` or uses defaults.

#### Settings Management

##### `load_settings()`
Load configuration from settings file.

**Returns:**
- `dict`: Configuration dictionary with network, detection, and zone settings

##### `save_settings(settings)`
Save configuration to settings file.

**Parameters:**
- `settings` (dict): Configuration dictionary to save

#### Camera Control

##### `start_camera()`
Initialize and start the camera thread.

##### `stop_camera()`
Stop the camera thread and clean up resources.

## Configuration

### Settings Structure

```python
{
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
```

### Network Settings

- **ip_address**: ESP32 device IP address
- **port**: UDP communication port (usually 4210)

### Detection Settings

- **min_detection_confidence**: Hand detection threshold (0.1-1.0)
- **min_tracking_confidence**: Hand tracking threshold (0.1-1.0)

### Zone Settings

- **forward_zone/backward_zone**: Control zone definitions
  - `x`, `y`: Top-left corner position (0.0-1.0, normalized coordinates)
  - `width`, `height`: Zone dimensions (0.0-1.0, normalized)
- **turn_angle_threshold**: Angle threshold for left/right turns (degrees)

## Commands

### Robot Commands

| Command    | Description                    | Trigger Condition |
|------------|--------------------------------|-------------------|
| `FORWARD`  | Move robot forward            | Hand in forward zone |
| `BACKWARD` | Move robot backward           | Hand in backward zone |
| `LEFT`     | Turn robot left               | Hand tilted left > threshold |
| `RIGHT`    | Turn robot right              | Hand tilted right > threshold |
| `STOP`     | Stop all movement             | Default state |

### ESP32 Communication

Commands are sent via UDP to the ESP32 using the following format:

```python
import socket

def send_command(ip, port, command):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(command.encode(), (ip, port))
```

## Gesture Recognition

### Hand Landmarks

The system uses MediaPipe hand landmarks for gesture detection:

- **Landmark 0**: Wrist
- **Landmark 9**: Index finger MCP (middle joint)
- **Landmark 13**: Middle finger PIP (upper joint)

### Zone-Based Detection

```python
# Check if hand is in zone
def is_hand_in_zone(landmarks, zone_rect, width, height):
    index_mcp = landmarks[9]
    middle_pip = landmarks[13]
    
    # Convert normalized coordinates to pixels
    index_x = int(index_mcp.x * width)
    index_y = int(index_mcp.y * height)
    middle_x = int(middle_pip.x * width)
    middle_y = int(middle_pip.y * height)
    
    # Check if both points are in zone
    return (zone_rect[0] < index_x < zone_rect[0] + zone_rect[2] and
            zone_rect[1] < index_y < zone_rect[1] + zone_rect[3] and
            zone_rect[0] < middle_x < zone_rect[0] + zone_rect[2] and
            zone_rect[1] < middle_y < zone_rect[1] + zone_rect[3])
```

### Angle-Based Detection

```python
import math

def calculate_hand_angle(landmarks):
    wrist = landmarks[0]
    middle_mcp = landmarks[9]
    
    # Calculate angle between wrist and middle finger
    angle = math.atan2(wrist.y - middle_mcp.y, wrist.x - middle_mcp.x)
    angle_degrees = math.degrees(angle) - 90
    
    # Normalize angle to [-180, 180]
    if angle_degrees <= -180:
        angle_degrees += 360
    elif angle_degrees > 180:
        angle_degrees -= 360
        
    return angle_degrees
```

## Error Handling

### Common Exceptions

#### `CameraError`
Raised when camera initialization fails.

```python
try:
    controller.run()
except Exception as e:
    if "camera" in str(e).lower():
        print("Camera error: Check camera connection")
```

#### `NetworkError`
Raised when ESP32 communication fails.

```python
try:
    controller.send_command_to_esp32("FORWARD")
except Exception as e:
    print(f"Network error: {e}")
```

### Debug Mode

Enable debug output for troubleshooting:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or add print statements in development
def debug_landmarks(landmarks):
    for i, landmark in enumerate(landmarks):
        print(f"Landmark {i}: ({landmark.x:.3f}, {landmark.y:.3f})")
```

## Performance Optimization

### Frame Rate Optimization

```python
# Reduce camera resolution for better performance
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Limit MediaPipe processing
hands = mp_hands.Hands(
    max_num_hands=1,  # Process only one hand
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
```

### Memory Management

```python
# Ensure proper cleanup
try:
    controller.run()
finally:
    controller.cleanup()
```

## Integration Examples

### Custom Gesture Recognition

```python
def custom_gesture_recognizer(landmarks):
    """Custom gesture recognition function."""
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    
    # Calculate distance between thumb and index
    distance = ((thumb_tip.x - index_tip.x)**2 + 
                (thumb_tip.y - index_tip.y)**2)**0.5
    
    if distance < 0.1:
        return "CUSTOM_STOP"
    
    return "UNKNOWN"

# Integrate with main controller
def process_custom_frame(frame, hands):
    result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    if result.multi_hand_landmarks:
        landmarks = result.multi_hand_landmarks[0].landmark
        command = custom_gesture_recognizer(landmarks)
        return command
    
    return "STOP"
```

### Multiple Robot Control

```python
class MultiRobotController:
    def __init__(self, robot_configs):
        self.robots = []
        for config in robot_configs:
            robot = GestureController(config['ip'], config['port'])
            self.robots.append(robot)
    
    def broadcast_command(self, command):
        for robot in self.robots:
            robot.send_command_to_esp32(command)

# Usage
configs = [
    {'ip': '192.168.1.100', 'port': 4210},
    {'ip': '192.168.1.101', 'port': 4210}
]
multi_controller = MultiRobotController(configs)
multi_controller.broadcast_command("FORWARD")
```

## Testing and Validation

### Unit Testing

```python
import unittest
from unittest.mock import Mock, patch

class TestGestureController(unittest.TestCase):
    def setUp(self):
        self.controller = GestureController()
    
    @patch('socket.socket')
    def test_send_command(self, mock_socket):
        self.controller.send_command_to_esp32("FORWARD")
        mock_socket.assert_called_once()
    
    def test_angle_calculation(self):
        # Test angle calculation with known landmarks
        pass
```

### Integration Testing

```python
def test_full_pipeline():
    """Test complete gesture recognition pipeline."""
    # Load test image
    test_frame = cv2.imread('test_hand.jpg')
    
    # Process frame
    controller = GestureController()
    processed_frame, command = controller.process_frame(test_frame)
    
    # Validate result
    assert command in ['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT', 'STOP']
    assert processed_frame is not None
```

## Troubleshooting Guide

### Common Issues

1. **Hand not detected**: Adjust lighting, camera position
2. **False positives**: Tune detection confidence thresholds
3. **Laggy response**: Reduce frame size, optimize network
4. **ESP32 disconnection**: Check WiFi stability, power supply

### Debug Commands

```python
# Test ESP32 connectivity
def test_esp32_connection(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(5)
            sock.sendto(b"TEST", (ip, port))
            print("ESP32 connection successful")
    except:
        print("ESP32 connection failed")

# Test camera
def test_camera():
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("Camera initialized successfully")
        cap.release()
    else:
        print("Camera initialization failed")
```

For more examples and advanced usage, see the `/examples` directory.