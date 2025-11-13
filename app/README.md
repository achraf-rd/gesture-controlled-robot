# Gesture Control Application

This application allows you to control devices using hand gestures captured through your webcam. It features a modern UI with configurable parameters for network settings, detection sensitivity, and control zones.

## Features

- Real-time hand gesture detection using MediaPipe
- Configurable control zones for FORWARD and BACKWARD commands
- Adjustable turn angle threshold for LEFT and RIGHT commands
- Network settings for connecting to an ESP32 device
- Modern UI with live camera feed and command display
- Save and load user settings

## Requirements

- Python 3.7 or higher
- Webcam
- ESP32 device (configured to receive UDP commands)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

1. Run the application:

```
python main.py
```

2. Configure the ESP32 IP address and port in the Network tab
3. Adjust the detection sensitivity and control zones as needed
4. Click "Start Camera" to begin gesture detection
5. Use the following gestures to control your device:
   - Place your hand in the top zone for FORWARD command
   - Place your hand in the bottom zone for BACKWARD command
   - Tilt your hand left/right for LEFT/RIGHT commands
6. Click "Save Settings" to save your configuration for future use

## Customization

- **Network Settings**: Configure the IP address and port of your ESP32 device
- **Detection Settings**: Adjust the hand detection and tracking confidence thresholds
- **Control Zones**: Modify the position and size of the FORWARD and BACKWARD control zones
- **Turn Angle**: Change the angle threshold for LEFT and RIGHT commands

## Troubleshooting

- If the camera doesn't start, ensure your webcam is properly connected and not in use by another application
- If commands aren't being received by the ESP32, verify the IP address and port settings
- For better hand detection, ensure good lighting conditions