# Zone-Based Control Examples

This directory contains examples that use screen zones for gesture detection rather than specific finger positions.

## Examples

### 1. rectangle_zones.py
**Zone-based gesture control with angle detection**

- **Purpose**: Demonstrates area-based control with hand angle calculation
- **Control Method**:
  - Top red zone: BACKWARD
  - Bottom red zone: FORWARD
  - Hand tilt angle > 20°: RIGHT
  - Hand tilt angle < -20°: LEFT
  - Default: STOP

**Features**:
- Real-time angle calculation and visualization
- Visual control zones with labels
- Key landmark highlighting (yellow and cyan circles)
- Angle indicator line
- Command history tracking
- Color-coded command display

**Usage:**
```bash
python rectangle_zones.py
```

## How Zone-Based Control Works

### Zone Detection
The system defines rectangular areas on the screen:
```python
# Top zone (BACKWARD)
top_box = (center_x - 100, 0, 200, 200)

# Bottom zone (FORWARD)  
bottom_box = (center_x - 100, height - 200, 200, 200)
```

When specific hand landmarks (index MCP and middle PIP) are both within a zone, the corresponding command is triggered.

### Angle-Based Turning
The system calculates the angle between the wrist and middle finger MCP:
```python
angle = math.atan2(wrist.y - middle_mcp.y, wrist.x - middle_mcp.x)
angle_degrees = math.degrees(angle) - 90
```

This angle determines left/right turns:
- Angle > 20°: RIGHT turn
- Angle < -20°: LEFT turn

## Visual Indicators

### Control Zones
- **Red rectangles**: Active control zones
- **Zone labels**: "FORWARD" and "BACKWARD" text
- **Zone positioning**: Top and bottom of screen

### Hand Tracking
- **Yellow circle**: Index finger MCP (landmark 9)
- **Cyan circle**: Middle finger PIP (landmark 13)
- **Green line**: Hand angle visualization
- **White skeleton**: Complete hand landmarks

### Command Display
- **Background color**: Changes based on current command
  - Green: FORWARD
  - Red: BACKWARD
  - Blue: LEFT
  - Magenta: RIGHT
  - Gray: STOP

## Configuration

### Adjusting Zone Size
```python
# Make zones larger
zone_width = 200  # Increase from 200
zone_height = 250  # Increase from 200

top_box_top_left = (center_x - zone_width//2, 0)
top_box_bottom_right = (center_x + zone_width//2, zone_height)
```

### Changing Angle Sensitivity
```python
# More sensitive turning (smaller angles)
elif angle > 15:  # Decrease from 20
    command = "RIGHT"
elif angle < -15:  # Increase from -20
    command = "LEFT"
```

### Camera Resolution
```python
# Higher resolution for more precision
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
```

## Advantages of Zone-Based Control

1. **Intuitive**: Natural hand movements in screen areas
2. **Reliable**: Less sensitive to exact finger positions
3. **Accessible**: Works with various hand sizes and positions
4. **Visual**: Clear indication of control areas
5. **Adjustable**: Easy to modify zone sizes and positions

## Use Cases

- **Robot navigation**: Intuitive directional control
- **Presentation control**: Slide navigation
- **Game control**: Character movement
- **Accessibility**: Alternative to keyboard/mouse
- **Remote control**: Device operation from distance

## Troubleshooting

### Zones Not Responding
- Ensure both key landmarks (yellow and cyan circles) are in the zone
- Check lighting conditions for better hand detection
- Adjust zone size if hands are too large/small

### Angle Detection Issues
- Verify the green angle line is visible
- Check that hand is flat and parallel to camera
- Adjust angle thresholds for your hand movement style

### Performance Issues
- Reduce camera resolution for better frame rate
- Close other applications using camera
- Ensure sufficient lighting

## Customization Examples

### Multiple Zone Layout
```python
# Create a 3x3 grid of zones
zones = []
for row in range(3):
    for col in range(3):
        x = col * width // 3
        y = row * height // 3
        w = width // 3
        h = height // 3
        zones.append((x, y, w, h))
```

### Gesture Smoothing
```python
# Add command history for stability
command_history = []

def smooth_command(new_command):
    command_history.append(new_command)
    if len(command_history) > 5:
        command_history.pop(0)
    
    # Return most frequent command
    return max(set(command_history), key=command_history.count)
```

### Custom Zone Shapes
```python
# Circular zones instead of rectangular
def is_in_circle(point, center, radius):
    distance = math.sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2)
    return distance < radius
```

## Next Steps

1. Try different zone layouts and sizes
2. Experiment with angle thresholds
3. Add more zones for additional commands
4. Combine with GUI applications in `/examples/gui_applications/`
5. Explore the full-featured application in `/src/`

## Performance Tips

1. **Optimize for your setup**:
   - Adjust camera resolution based on your hardware
   - Modify zone sizes for your hand size
   - Tune angle thresholds for your natural hand position

2. **Improve reliability**:
   - Use consistent lighting
   - Keep camera at a stable position
   - Maintain steady hand movements

3. **Reduce latency**:
   - Only send commands when they change
   - Process every nth frame if needed
   - Use smaller camera resolution for faster processing