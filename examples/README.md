# Examples Directory

This directory contains various implementations and demonstrations of the gesture-controlled robot system. Each subdirectory focuses on different aspects and approaches to gesture recognition and robot control.

## 📁 Directory Structure

```
examples/
├── simple_gestures/          # Basic gesture recognition examples
│   ├── finger_gestures.py    # Finger-based gesture detection
│   ├── udp_gesture_control.py # Network-enabled gesture control
│   └── README.md             # Simple gestures documentation
├── zone_based_control/       # Area-based gesture detection
│   ├── rectangle_zones.py    # Zone-based control with angles
│   └── README.md             # Zone control documentation
├── gui_applications/         # Graphical user interfaces
│   ├── simple_gui.py         # Simplified GUI controller
│   └── README.md             # GUI applications documentation
└── README.md                 # This file
```

## 🚀 Quick Start Guide

### 1. Choose Your Starting Point

**New to gesture recognition?**
→ Start with `simple_gestures/finger_gestures.py`

**Want intuitive control?**
→ Try `zone_based_control/rectangle_zones.py`

**Prefer GUI interfaces?**
→ Use `gui_applications/simple_gui.py`

**Ready for full features?**
→ Go to `/src/gesture_control_gui.py`

### 2. Installation

```bash
# Install core requirements
pip install opencv-python mediapipe numpy

# For GUI examples, also install:
pip install PyQt5

# Or install everything:
pip install -r ../requirements.txt
```

### 3. Hardware Setup

For network-enabled examples, you'll need:
- ESP32 development board
- Robot hardware (motors, chassis)
- WiFi network connection

See [Hardware Setup Guide](../docs/hardware_setup.md) for detailed instructions.

## 📖 Example Categories

### Simple Gestures
**Focus**: Basic finger position recognition

**Examples**:
- `finger_gestures.py`: Pure gesture recognition demo
- `udp_gesture_control.py`: Network-enabled version

**Best for**:
- Learning gesture recognition basics
- Understanding MediaPipe fundamentals
- Quick prototyping

**Key concepts**:
- Finger landmark detection
- Distance calculations
- Basic gesture logic
- UDP communication

### Zone-Based Control
**Focus**: Screen area-based gesture detection

**Examples**:
- `rectangle_zones.py`: Zone control with angle detection

**Best for**:
- Intuitive robot navigation
- Reliable gesture detection
- User-friendly interfaces

**Key concepts**:
- Zone definition and detection
- Hand angle calculation
- Visual feedback systems
- Coordinate transformations

### GUI Applications
**Focus**: User-friendly graphical interfaces

**Examples**:
- `simple_gui.py`: Clean, professional interface

**Best for**:
- End-user applications
- Real-time parameter adjustment
- Visual feedback and monitoring
- Production-ready interfaces

**Key concepts**:
- PyQt5 application development
- Real-time video integration
- Settings management
- User experience design

## 🎯 Learning Path

### Beginner Level
1. **Start here**: `simple_gestures/finger_gestures.py`
   - Learn basic gesture recognition
   - Understand hand landmarks
   - See real-time processing

2. **Add networking**: `simple_gestures/udp_gesture_control.py`
   - Learn UDP communication
   - Connect to ESP32
   - Control real hardware

### Intermediate Level
3. **Zone control**: `zone_based_control/rectangle_zones.py`
   - More intuitive control method
   - Learn coordinate systems
   - Understand angle calculations

4. **GUI interface**: `gui_applications/simple_gui.py`
   - Professional user interface
   - Real-time parameter adjustment
   - Better user experience

### Advanced Level
5. **Full application**: `/src/gesture_control_gui.py`
   - Complete feature set
   - Advanced configuration
   - Production-ready code

## 🛠️ Customization Guide

### Adding New Gestures

```python
def custom_gesture_recognizer(landmarks):
    """Add your own gesture recognition logic."""
    # Example: Peace sign detection
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    # Check if only index and middle fingers are up
    if (index_tip.y < landmarks[6].y and  # Index extended
        middle_tip.y < landmarks[10].y and  # Middle extended
        ring_tip.y > landmarks[14].y and   # Ring folded
        pinky_tip.y > landmarks[18].y):    # Pinky folded
        return "PEACE_SIGN"
    
    return "UNKNOWN"
```

### Modifying Control Zones

```python
# Create custom zone layout
def create_directional_zones(width, height):
    """Create 4-directional control zones."""
    center_x, center_y = width // 2, height // 2
    zone_size = 100
    
    zones = {
        'FORWARD': (center_x - zone_size//2, 0, zone_size, zone_size),
        'BACKWARD': (center_x - zone_size//2, height - zone_size, zone_size, zone_size),
        'LEFT': (0, center_y - zone_size//2, zone_size, zone_size),
        'RIGHT': (width - zone_size, center_y - zone_size//2, zone_size, zone_size)
    }
    
    return zones
```

### Adding Visual Effects

```python
def draw_gesture_trail(frame, landmarks, trail_history):
    """Draw a trail following hand movement."""
    wrist = landmarks[0]
    current_pos = (int(wrist.x * frame.shape[1]), int(wrist.y * frame.shape[0]))
    
    trail_history.append(current_pos)
    if len(trail_history) > 20:
        trail_history.pop(0)
    
    # Draw trail
    for i in range(1, len(trail_history)):
        alpha = i / len(trail_history)
        color = (int(255 * alpha), int(100 * alpha), 0)
        cv2.line(frame, trail_history[i-1], trail_history[i], color, 3)
```

## 🔧 Common Modifications

### Performance Optimization

```python
# Reduce processing load
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Lower resolution
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

hands = mp_hands.Hands(
    max_num_hands=1,           # Process only one hand
    model_complexity=0,        # Use simpler model
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Process every nth frame
frame_count = 0
if frame_count % 2 == 0:  # Process every other frame
    result = hands.process(rgb_frame)
```

### Network Configuration

```python
# Robust UDP sending with retries
def send_command_with_retry(command, ip, port, retries=3):
    for attempt in range(retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(1.0)
                sock.sendto(command.encode(), (ip, port))
                return True
        except Exception as e:
            if attempt == retries - 1:
                print(f"Failed to send after {retries} attempts: {e}")
                return False
            time.sleep(0.1)
```

### Enhanced Visual Feedback

```python
def draw_command_history(frame, command_history):
    """Show recent command history."""
    for i, cmd in enumerate(command_history[-5:]):  # Last 5 commands
        y_pos = 100 + i * 30
        alpha = 0.3 + 0.14 * i  # Fade older commands
        color = (int(255 * alpha), int(255 * alpha), int(255 * alpha))
        cv2.putText(frame, cmd, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
```

## 📊 Comparison Matrix

| Example | Complexity | Features | Use Case |
|---------|------------|----------|----------|
| finger_gestures.py | ⭐ | Basic gesture recognition | Learning, prototyping |
| udp_gesture_control.py | ⭐⭐ | + Network communication | Robot control testing |
| rectangle_zones.py | ⭐⭐⭐ | + Zone control, angles | Intuitive navigation |
| simple_gui.py | ⭐⭐⭐⭐ | + GUI, real-time config | End-user applications |
| gesture_control_gui.py | ⭐⭐⭐⭐⭐ | + Full features, settings | Production deployment |

## 🚨 Troubleshooting

### Common Issues Across Examples

1. **Camera not detected**
   ```python
   # Test camera availability
   for i in range(3):
       cap = cv2.VideoCapture(i)
       if cap.isOpened():
           print(f"Camera found at index {i}")
           break
       cap.release()
   ```

2. **Poor hand detection**
   - Improve lighting conditions
   - Use plain background
   - Keep hand fully visible
   - Adjust detection confidence

3. **Network connectivity**
   - Verify ESP32 IP address
   - Check firewall settings
   - Ensure same network
   - Test with ping command

4. **Performance issues**
   - Reduce camera resolution
   - Limit to one hand detection
   - Close other applications
   - Use simpler MediaPipe model

### Example-Specific Issues

**finger_gestures.py**:
- Adjust pinch distance threshold for hand size
- Modify gesture logic for personal preference

**rectangle_zones.py**:
- Resize zones for different screen resolutions
- Tune angle thresholds for natural hand movement

**simple_gui.py**:
- Install PyQt5 if GUI won't start
- Check camera permissions on some systems

## 🔗 Integration Examples

### Combining Multiple Approaches

```python
class HybridGestureController:
    """Combine finger and zone-based detection."""
    
    def __init__(self):
        self.finger_detector = FingerGestureDetector()
        self.zone_detector = ZoneGestureDetector()
    
    def process_frame(self, frame, landmarks):
        # Try finger gestures first
        finger_command = self.finger_detector.detect(landmarks)
        if finger_command != "UNKNOWN":
            return finger_command
        
        # Fall back to zone detection
        zone_command = self.zone_detector.detect(frame, landmarks)
        return zone_command
```

### Multi-Robot Control

```python
class MultiRobotController:
    """Control multiple robots with gestures."""
    
    def __init__(self, robot_configs):
        self.robots = []
        for config in robot_configs:
            robot = RobotConnection(config['ip'], config['port'])
            self.robots.append(robot)
    
    def broadcast_command(self, command):
        for robot in self.robots:
            robot.send_command(command)
    
    def selective_command(self, robot_id, command):
        if robot_id < len(self.robots):
            self.robots[robot_id].send_command(command)
```

## 📚 Further Reading

- [MediaPipe Hand Documentation](https://mediapipe.dev/solutions/hands)
- [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [ESP32 Arduino Reference](https://docs.espressif.com/projects/arduino-esp32/)

## 🤝 Contributing

To add your own example:

1. Create a new subdirectory or add to existing one
2. Include comprehensive comments in your code
3. Add a README.md explaining the example
4. Test with different hardware configurations
5. Submit a pull request

## 💡 Tips for Success

1. **Start Simple**: Begin with basic examples before advancing
2. **Test Incrementally**: Verify each component before combining
3. **Document Changes**: Keep track of modifications that work
4. **Share Examples**: Contribute back to the community
5. **Experiment**: Try different approaches and combinations

Happy coding! 🚀