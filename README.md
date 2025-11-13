# 🤖 Gesture-Controlled Robot Project

A comprehensive hand gesture recognition system that enables real-time control of robotic devices using computer vision and MediaPipe.

![Project Demo](docs/demo.gif)

## 🌟 Features

- **Real-time Hand Gesture Recognition**: Uses MediaPipe for accurate hand tracking
- **Multiple Control Methods**: Zone-based control, angle-based turning, and finger gesture recognition
- **Professional GUI Applications**: Modern PyQt5 interface with live camera feed
- **ESP32 Integration**: Wireless communication via UDP to control robotic hardware
- **Configurable Parameters**: Adjustable detection sensitivity, control zones, and network settings
- **Multiple Example Implementations**: From simple scripts to full-featured applications

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Webcam
- ESP32 development board (optional, for hardware control)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gesture-controlled-robot.git
cd gesture-controlled-robot
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the main application:
```bash
python src/gesture_control_gui.py
```

## 📁 Project Structure

```
gesture-controlled-robot/
├── src/                           # Main application code
│   ├── gesture_control_gui.py     # Advanced GUI application
│   ├── gesture_control_simple.py  # Simple command-line version
│   └── core/                      # Core modules
├── esp32/                         # ESP32 Arduino code
│   └── robot_controller/          # Main ESP32 firmware
├── examples/                      # Example implementations
│   ├── simple_gestures/           # Basic gesture recognition
│   ├── zone_based_control/        # Zone-based control methods
│   └── gui_applications/          # Different GUI versions
├── docs/                          # Documentation
│   ├── hardware_setup.md          # Hardware assembly guide
│   ├── api_reference.md           # API documentation
│   └── troubleshooting.md         # Common issues and solutions
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🎮 Gesture Controls

### Zone-Based Control
- **Forward Zone**: Place your hand in the top zone of the screen
- **Backward Zone**: Place your hand in the bottom zone of the screen
- **Left/Right Turns**: Tilt your hand left or right beyond the angle threshold

### Finger Gesture Control
- **Stop**: Pinch index finger and thumb together
- **Forward**: Point with index finger upward
- **Backward**: Close fist
- **Left/Right**: Point left or right with index finger

## 🔧 Hardware Setup

### Required Components
- ESP32 development board
- 2x DC motors
- Motor driver (L298N or similar)
- Robot chassis
- Power supply (7.4V recommended)
- Jumper wires

### ESP32 Connections
| ESP32 Pin | Component | Description |
|-----------|-----------|-------------|
| GPIO 2    | ML_Ctrl   | Left motor direction |
| GPIO 5    | ML_PWM    | Left motor speed |
| GPIO 4    | MR_Ctrl   | Right motor direction |
| GPIO 16   | MR_PWM    | Right motor speed |

For detailed hardware setup instructions, see [Hardware Setup Guide](docs/hardware_setup.md).

## ⚙️ Configuration

### Network Settings
Configure the ESP32 IP address and UDP port in the application or modify the settings directly:

```python
ESP32_IP = "192.168.137.205"  # Your ESP32's IP address
ESP32_PORT = 4210             # UDP communication port
```

### Detection Parameters
Adjust hand detection sensitivity:
- `min_detection_confidence`: Minimum confidence for hand detection (0.1-1.0)
- `min_tracking_confidence`: Minimum confidence for hand tracking (0.1-1.0)

### Control Zones
Customize control zones in the GUI or modify zone parameters:
- Position (X, Y coordinates)
- Size (width and height)
- Turn angle threshold

## 📖 Usage Examples

### Basic Gesture Recognition
```python
from src.core.gesture_recognizer import GestureRecognizer

recognizer = GestureRecognizer()
command = recognizer.process_frame(frame)
print(f"Detected command: {command}")
```

### UDP Communication
```python
from src.core.udp_client import UDPClient

client = UDPClient("192.168.137.205", 4210)
client.send_command("FORWARD")
```

## 🛠️ Development

### Adding New Gestures
1. Define gesture logic in `src/core/gesture_recognizer.py`
2. Add gesture to the recognition pipeline
3. Map gesture to robot commands
4. Test with the GUI application

### Customizing Robot Behavior
Modify the ESP32 code in `esp32/robot_controller/main.cpp` to change:
- Motor speeds
- Movement patterns
- Additional sensors integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-gesture`)
3. Commit your changes (`git commit -am 'Add new gesture recognition'`)
4. Push to the branch (`git push origin feature/new-gesture`)
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for hand tracking capabilities
- [OpenCV](https://opencv.org/) for computer vision functionality
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for the GUI framework

## 📞 Support

If you encounter any issues or have questions:
- Check the [Troubleshooting Guide](docs/troubleshooting.md)
- Open an issue on GitHub
- Contact the maintainers

## 🔮 Future Enhancements

- [ ] Voice command integration
- [ ] Mobile app for remote control
- [ ] Machine learning for custom gesture training
- [ ] Support for multiple robots
- [ ] Web-based control interface
- [ ] Advanced path planning algorithms

---

**Happy Coding! 🚀**