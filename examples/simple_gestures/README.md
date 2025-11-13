# Simple Gesture Examples

This directory contains basic gesture recognition examples that demonstrate different approaches to hand gesture detection.

## Examples

### 1. finger_gestures.py
**Basic finger-based gesture recognition**

- **Purpose**: Demonstrates gesture recognition using finger positions
- **Gestures**:
  - Pinch (thumb + index): BACKWARD
  - Point with index finger: LEFT/RIGHT
  - All fingers up: FORWARD
  - Default: STOP
- **Features**: 
  - Visual feedback with colored command display
  - Real-time landmark visualization
  - Simple gesture logic

**Usage:**
```bash
python finger_gestures.py
```

### 2. udp_gesture_control.py
**Network-enabled gesture control**

- **Purpose**: Adds UDP communication to finger gesture recognition
- **Features**:
  - Sends commands to ESP32 via UDP
  - Network status indicators
  - Command change detection to reduce network traffic
  - Visual landmark highlighting
- **Configuration**: 
  - Change `ESP32_IP` and `ESP32_PORT` at the top of the file

**Usage:**
```bash
python udp_gesture_control.py
```

## Getting Started

1. **Install requirements**:
   ```bash
   pip install opencv-python mediapipe numpy
   ```

2. **Connect your webcam**

3. **Run any example**:
   ```bash
   python finger_gestures.py
   ```

4. **For UDP examples**, ensure your ESP32 is:
   - Connected to the same network
   - Running the robot controller firmware
   - Configured with the correct IP address

## Gesture Guide

### Finger Gestures
- **Stop**: Natural hand position
- **Forward**: Raise all fingers (open hand)
- **Backward**: Pinch thumb and index finger together
- **Left**: Point left with index finger
- **Right**: Point right with index finger

## Troubleshooting

### Camera Issues
- Ensure webcam is connected and not in use by other applications
- Try different camera indices (0, 1, 2) if camera fails to open

### Hand Detection Issues
- Ensure good lighting conditions
- Keep hand fully visible in camera frame
- Avoid complex backgrounds

### Network Issues (UDP examples)
- Verify ESP32 IP address
- Check that both devices are on same network
- Ensure firewall allows Python UDP communication

## Customization

### Adjusting Gesture Sensitivity
```python
# In finger_gestures.py, modify the pinch distance threshold:
if pinch_distance < 0.08:  # More sensitive (was 0.1)
    return "BACKWARD"
```

### Adding New Gestures
```python
def recognize_gesture(landmarks):
    # Add your custom gesture logic here
    thumb_tip = landmarks[4]
    middle_tip = landmarks[12]
    
    # Example: Thumb up gesture
    if thumb_tip.y < landmarks[0].y:  # Thumb above wrist
        return "CUSTOM_COMMAND"
    
    # ... existing gesture logic
```

### Changing Network Settings
```python
# At the top of udp_gesture_control.py:
ESP32_IP = "192.168.1.100"  # Your ESP32's IP
ESP32_PORT = 4210           # Your ESP32's port
```

## Next Steps

After trying these examples:
1. Move to `/examples/zone_based_control/` for area-based gesture detection
2. Try `/examples/gui_applications/` for user-friendly interfaces
3. Explore the main application in `/src/` for full-featured control

## Example Output

When running finger_gestures.py, you should see:
```
Finger Gesture Recognition Demo
Gestures:
- Pinch (index + thumb): BACKWARD
- Point with index finger: LEFT/RIGHT
- All fingers up: FORWARD
- Default: STOP
Press 'q' to quit
```

The video window will show your hand with:
- Colored command display
- Hand landmark visualization
- Real-time gesture detection