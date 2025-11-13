# GUI Applications Examples

This directory contains graphical user interface applications that provide user-friendly control interfaces for gesture recognition.

## Examples

### 1. simple_gui.py
**Simplified GUI gesture controller**

- **Purpose**: Demonstrates a clean, user-friendly interface for gesture control
- **Features**:
  - Live camera feed with gesture visualization
  - Adjustable control zones via sliders
  - Real-time connection testing
  - Activity log with timestamps
  - Color-coded command display
  - Professional UI styling

**Interface Sections**:
- **Video Feed**: Live camera view with gesture overlays
- **ESP32 Connection**: IP address and port configuration
- **Control Zones**: Adjustable zone heights
- **Camera Control**: Start/stop buttons
- **Status & Commands**: Current command and activity log

**Usage:**
```bash
python simple_gui.py
```

## GUI Features Overview

### Real-Time Video Display
- **Mirrored camera feed** for natural interaction
- **Control zone visualization** with colored rectangles
- **Hand landmark detection** with visual indicators
- **Command overlay** showing current gesture state

### Connection Management
- **IP Configuration**: Easy ESP32 address setup
- **Port Settings**: Configurable UDP port
- **Connection Testing**: Automatic connectivity verification
- **Status Indicators**: Visual connection status

### Zone Configuration
- **Top Zone Adjustment**: Slider for forward zone height
- **Bottom Zone Adjustment**: Slider for backward zone height
- **Real-time Updates**: Immediate visual feedback
- **Intuitive Controls**: Simple slider interface

### Activity Monitoring
- **Timestamped Log**: All actions with time stamps
- **Command History**: Track sent commands
- **Error Reporting**: Network and camera issues
- **Auto-scrolling**: Always shows latest activity

## User Interface Components

### Camera Feed Panel
```
┌─────────────────────────────────┐
│                                 │
│        Live Camera Feed         │
│     with Gesture Overlays       │
│                                 │
│    [Green] FORWARD Zone         │
│         Hand Tracking           │
│    [Red] BACKWARD Zone          │
│                                 │
└─────────────────────────────────┘
```

### Control Panel
```
┌─────────────────┐
│ ESP32 Connection│
│ IP: [_________] │
│ Port: [____]    │
├─────────────────┤
│ Control Zones   │
│ Top: [====|====]│
│ Bottom: [==|===]│
├─────────────────┤
│ Camera Control  │
│ [▶ Start]       │
│ [⏹ Stop]        │
├─────────────────┤
│ Status & Log    │
│ Command: STOP   │
│ [Log Output]    │
└─────────────────┘
```

## Getting Started

### 1. Installation
```bash
# Install GUI requirements
pip install PyQt5 opencv-python mediapipe
```

### 2. Running the Application
```bash
cd examples/gui_applications/
python simple_gui.py
```

### 3. Basic Setup
1. **Configure ESP32**: Enter IP address and port
2. **Start Camera**: Click "▶ Start Camera" button
3. **Adjust Zones**: Use sliders to set control areas
4. **Test Connection**: Watch for connection status in log
5. **Start Gesturing**: Move hand in control zones

## Control Methods

### Zone-Based Control
- **Forward Zone**: Green rectangle at top of screen
- **Backward Zone**: Red rectangle at bottom of screen
- **Hand Detection**: Yellow circle shows hand position
- **Zone Activation**: Hand must be fully within zone

### Visual Feedback
- **Command Display**: Large text showing current command
- **Color Coding**:
  - Green: FORWARD command
  - Red: BACKWARD command
  - Gray: STOP (no gesture)
- **Real-time Updates**: Instant command changes

## Configuration Options

### Network Settings
```python
# Default values (can be changed in GUI)
ESP32_IP = "192.168.137.205"
ESP32_PORT = 4210
```

### Zone Adjustment
```python
# Slider ranges (pixels)
TOP_ZONE_RANGE = (50, 300)      # Min/max height
BOTTOM_ZONE_RANGE = (50, 300)   # Min/max height
DEFAULT_ZONE_HEIGHT = 150       # Starting value
```

### Camera Settings
```python
# Optimized for GUI performance
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FRAME_RATE = 20  # FPS (50ms timer)
```

## Advanced Features

### Connection Testing
- **Automatic Testing**: Tests connection when camera starts
- **Timeout Handling**: 2-second timeout for ESP32 response
- **Error Reporting**: Clear error messages in log
- **Status Indicators**: Visual connection status

### Smart Command Sending
- **Change Detection**: Only sends when command changes
- **Network Optimization**: Reduces UDP traffic
- **Error Handling**: Graceful failure handling
- **Timeout Protection**: Prevents hanging

### Professional Styling
- **Modern UI**: Clean, professional appearance
- **Responsive Layout**: Adapts to window resizing
- **Color Themes**: Consistent color scheme
- **Button States**: Visual feedback for actions

## Customization Guide

### Adding New Zones
```python
def create_custom_zones(self, w, h):
    """Create additional control zones."""
    left_zone = (0, h//3, w//4, h//3)
    right_zone = (3*w//4, h//3, w//4, h//3)
    return left_zone, right_zone

def detect_custom_gestures(self, hand_pos, left_zone, right_zone):
    """Detect gestures in custom zones."""
    if self.point_in_zone(hand_pos, left_zone):
        return "LEFT"
    elif self.point_in_zone(hand_pos, right_zone):
        return "RIGHT"
    return None
```

### Modifying UI Layout
```python
def customize_layout(self):
    """Customize the user interface layout."""
    # Add new panels
    settings_panel = self.create_settings_panel()
    advanced_panel = self.create_advanced_panel()
    
    # Modify layout
    self.control_layout.addWidget(settings_panel)
    self.control_layout.addWidget(advanced_panel)
```

### Adding Settings Persistence
```python
import json

def save_settings(self):
    """Save current settings to file."""
    settings = {
        'ip': self.ip_input.text(),
        'port': int(self.port_input.text()),
        'top_zone': self.top_slider.value(),
        'bottom_zone': self.bottom_slider.value()
    }
    
    with open('gui_settings.json', 'w') as f:
        json.dump(settings, f)

def load_settings(self):
    """Load settings from file."""
    try:
        with open('gui_settings.json', 'r') as f:
            settings = json.load(f)
            
        self.ip_input.setText(settings['ip'])
        self.port_input.setText(str(settings['port']))
        self.top_slider.setValue(settings['top_zone'])
        self.bottom_slider.setValue(settings['bottom_zone'])
    except FileNotFoundError:
        pass  # Use defaults
```

## Troubleshooting

### GUI Won't Start
```bash
# Check PyQt5 installation
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"

# Install if missing
pip install PyQt5
```

### Camera Issues
- **Permission Errors**: Ensure camera access permissions
- **Multiple Applications**: Close other camera applications
- **Driver Issues**: Update camera drivers

### Connection Problems
- **Firewall**: Allow Python through firewall
- **Network**: Ensure both devices on same network
- **ESP32**: Verify ESP32 is running and accessible

### Performance Issues
- **High CPU**: Reduce camera resolution in code
- **Lag**: Close unnecessary applications
- **Memory**: Monitor memory usage over time

## Integration with Main Application

This GUI example demonstrates simplified concepts that are expanded in the main application (`/src/gesture_control_gui.py`):

### Differences from Main App
- **Simplified**: Fewer configuration options
- **Basic Zones**: Only top/bottom zones (no angle detection)
- **Single Hand**: Processes only one hand
- **Essential Features**: Core functionality only

### Upgrading to Main App
- **Advanced Zones**: Configurable zone positions and sizes
- **Angle Detection**: Hand tilt for left/right control
- **Full Settings**: Complete configuration management
- **Multiple Gestures**: More gesture types
- **Robust Error Handling**: Comprehensive error management

## Best Practices

### UI Design
1. **Keep It Simple**: Start with essential features
2. **Visual Feedback**: Always show current state
3. **Error Handling**: Graceful failure management
4. **Responsive Design**: Handle window resizing
5. **Consistent Styling**: Unified visual theme

### Performance Optimization
1. **Frame Rate**: Balance quality vs. performance
2. **Processing**: Only update when necessary
3. **Memory Management**: Proper cleanup on exit
4. **Network**: Minimize UDP traffic

### User Experience
1. **Clear Instructions**: Obvious how to use
2. **Immediate Feedback**: Instant response to actions
3. **Status Visibility**: Always show what's happening
4. **Error Recovery**: Easy to fix problems

## Future Enhancements

Possible improvements for this GUI:
- **Settings Persistence**: Save/load configurations
- **Multiple Cameras**: Camera selection dropdown
- **Recording**: Save gesture sessions
- **Calibration**: Zone adjustment wizard
- **Themes**: Multiple visual themes
- **Shortcuts**: Keyboard shortcuts for common actions

## Development Notes

This example serves as a foundation for building more complex gesture control interfaces. It demonstrates:
- **PyQt5 Integration**: Modern GUI framework usage
- **Real-time Processing**: Camera feed with gesture detection
- **Network Communication**: UDP protocol implementation
- **User Experience**: Intuitive interface design
- **Error Handling**: Robust failure management

Use this as a starting point for your own custom gesture control applications!