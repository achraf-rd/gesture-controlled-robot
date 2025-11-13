# Troubleshooting Guide

This guide helps you resolve common issues with the gesture-controlled robot project.

## Table of Contents
- [Camera Issues](#camera-issues)
- [Network/ESP32 Issues](#networkesp32-issues)
- [Hand Detection Issues](#hand-detection-issues)
- [Performance Issues](#performance-issues)
- [Hardware Issues](#hardware-issues)
- [Software Issues](#software-issues)

## Camera Issues

### Camera Not Detected
**Symptoms:** Error when starting camera, blank camera feed

**Solutions:**
1. **Check camera connections**
   ```bash
   # Windows: Check Device Manager
   # Linux: List video devices
   ls /dev/video*
   ```

2. **Test camera independently**
   ```python
   import cv2
   cap = cv2.VideoCapture(0)
   print(f"Camera opened: {cap.isOpened()}")
   cap.release()
   ```

3. **Try different camera indices**
   ```python
   # Try cameras 0, 1, 2, etc.
   for i in range(3):
       cap = cv2.VideoCapture(i)
       if cap.isOpened():
           print(f"Camera found at index {i}")
           cap.release()
   ```

4. **Update camera drivers**
   - Windows: Update through Device Manager
   - Linux: Update v4l2 drivers

### Poor Camera Quality
**Symptoms:** Blurry image, low resolution, poor colors

**Solutions:**
1. **Adjust camera settings**
   ```python
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
   cap.set(cv2.CAP_PROP_FPS, 30)
   cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
   ```

2. **Clean camera lens**
3. **Improve lighting conditions**
4. **Check USB bandwidth** (use USB 3.0 ports)

### Camera Lag or Freezing
**Symptoms:** Delayed video feed, frozen frames

**Solutions:**
1. **Reduce resolution**
   ```python
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
   ```

2. **Lower frame rate**
   ```python
   cap.set(cv2.CAP_PROP_FPS, 15)
   ```

3. **Close other applications** using the camera
4. **Check CPU usage** and close unnecessary programs

## Network/ESP32 Issues

### ESP32 Not Connecting to WiFi
**Symptoms:** ESP32 doesn't get IP address, WiFi connection fails

**Solutions:**
1. **Check WiFi credentials**
   ```cpp
   const char *ssid = "YourNetworkName";
   const char *password = "YourPassword";
   ```

2. **Verify network compatibility**
   - ESP32 supports 2.4GHz only (not 5GHz)
   - Check security type (WPA/WPA2)

3. **Check signal strength**
   - Move ESP32 closer to router
   - Add external antenna

4. **Reset ESP32**
   ```cpp
   // In setup(), add:
   WiFi.begin(ssid, password);
   delay(10000); // Longer delay for connection
   ```

### Commands Not Reaching ESP32
**Symptoms:** Python sends commands but ESP32 doesn't respond

**Solutions:**
1. **Verify IP address**
   ```python
   # Test connectivity
   import socket
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sock.settimeout(5)
   try:
       sock.sendto(b"TEST", ("192.168.137.205", 4210))
       print("Connection successful")
   except:
       print("Connection failed")
   sock.close()
   ```

2. **Check firewall settings**
   - Allow Python through firewall
   - Open UDP port 4210

3. **Verify ESP32 IP address**
   ```cpp
   // In ESP32 code, add debug prints:
   Serial.print("IP Address: ");
   Serial.println(WiFi.localIP());
   ```

4. **Test with UDP tool**
   ```bash
   # Linux/Mac: Test UDP with netcat
   echo "FORWARD" | nc -u 192.168.137.205 4210
   ```

### Network Timeout Issues
**Symptoms:** Intermittent connection, timeout errors

**Solutions:**
1. **Increase timeout values**
   ```python
   sock.settimeout(1.0)  # Increase from 0.5 to 1.0
   ```

2. **Add retry logic**
   ```python
   def send_command_with_retry(command, retries=3):
       for attempt in range(retries):
           try:
               send_command_to_esp32(command)
               return
           except Exception as e:
               if attempt == retries - 1:
                   raise e
               time.sleep(0.1)
   ```

3. **Check network stability**
4. **Use static IP** for ESP32

## Hand Detection Issues

### Hands Not Detected
**Symptoms:** No hand landmarks shown, commands not triggered

**Solutions:**
1. **Improve lighting**
   - Use bright, even lighting
   - Avoid backlighting
   - Remove shadows

2. **Adjust detection confidence**
   ```python
   hands = mp_hands.Hands(
       min_detection_confidence=0.5,  # Lower from 0.7
       min_tracking_confidence=0.5
   )
   ```

3. **Check hand position**
   - Keep hand in center of frame
   - Ensure full hand is visible
   - Avoid partial occlusion

4. **Skin tone considerations**
   - MediaPipe works with all skin tones
   - Ensure sufficient contrast with background

### False Positive Detection
**Symptoms:** Random commands triggered, detection on non-hands

**Solutions:**
1. **Increase detection confidence**
   ```python
   hands = mp_hands.Hands(
       min_detection_confidence=0.8,  # Increase from 0.7
       min_tracking_confidence=0.8
   )
   ```

2. **Add gesture validation**
   ```python
   def validate_hand_gesture(landmarks):
       # Check if landmarks form a valid hand shape
       wrist = landmarks[0]
       fingertips = [landmarks[4], landmarks[8], landmarks[12], landmarks[16], landmarks[20]]
       
       # Validate finger positions relative to wrist
       for tip in fingertips:
           if abs(tip.x - wrist.x) > 0.3 or abs(tip.y - wrist.y) > 0.3:
               return False
       return True
   ```

3. **Use plain background**
4. **Limit detection area**

### Inconsistent Gesture Recognition
**Symptoms:** Same gesture produces different commands

**Solutions:**
1. **Calibrate zones**
   ```python
   # Adjust zone sizes and positions
   forward_zone = {'x': 0.3, 'y': 0.0, 'width': 0.4, 'height': 0.25}
   ```

2. **Add gesture smoothing**
   ```python
   class GestureSmoothing:
       def __init__(self, window_size=5):
           self.window = []
           self.window_size = window_size
       
       def smooth_command(self, command):
           self.window.append(command)
           if len(self.window) > self.window_size:
               self.window.pop(0)
           
           # Return most common command in window
           return max(set(self.window), key=self.window.count)
   ```

3. **Tune angle thresholds**
   ```python
   # Increase turn threshold for stability
   turn_angle_threshold = 30  # Increase from 20
   ```

## Performance Issues

### Low Frame Rate
**Symptoms:** Choppy video, delayed response

**Solutions:**
1. **Optimize camera resolution**
   ```python
   # Use lower resolution
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
   ```

2. **Limit hand detection**
   ```python
   hands = mp_hands.Hands(
       max_num_hands=1,  # Process only one hand
       model_complexity=0  # Use simpler model
   )
   ```

3. **Skip frames**
   ```python
   frame_skip = 2  # Process every 2nd frame
   frame_count = 0
   
   while cap.isOpened():
       ret, frame = cap.read()
       frame_count += 1
       
       if frame_count % frame_skip == 0:
           # Process frame
           pass
   ```

### High CPU Usage
**Symptoms:** System sluggish, fan noise, heat

**Solutions:**
1. **Profile code performance**
   ```python
   import time
   
   start_time = time.time()
   result = hands.process(frame)
   processing_time = time.time() - start_time
   print(f"Processing time: {processing_time:.3f}s")
   ```

2. **Use threading**
   ```python
   import threading
   import queue
   
   def camera_thread(frame_queue):
       while True:
           ret, frame = cap.read()
           if not frame_queue.full():
               frame_queue.put(frame)
   ```

3. **Optimize imports**
   ```python
   # Import only what you need
   from mediapipe.python.solutions.hands import Hands
   ```

### Memory Leaks
**Symptoms:** Increasing RAM usage over time

**Solutions:**
1. **Proper cleanup**
   ```python
   try:
       # Main loop
       pass
   finally:
       cap.release()
       cv2.destroyAllWindows()
       hands.close()
   ```

2. **Monitor memory usage**
   ```python
   import psutil
   process = psutil.Process()
   print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
   ```

## Hardware Issues

### Motors Not Moving
**Symptoms:** ESP32 receives commands but motors don't rotate

**Solutions:**
1. **Check power supply**
   - Measure voltage at motor driver
   - Ensure sufficient current capacity (2-3A)
   - Check battery charge level

2. **Verify wiring**
   ```
   Multimeter Checks:
   - Continuity between ESP32 and motor driver
   - Motor resistance (should be 5-20 ohms)
   - Power supply voltage under load
   ```

3. **Test motor driver**
   ```cpp
   // Basic motor test code
   void testMotors() {
       digitalWrite(ML_Ctrl, HIGH);
       ledcWrite(PWM_CHANNEL_ML, 100);
       delay(1000);
       ledcWrite(PWM_CHANNEL_ML, 0);
   }
   ```

4. **Check PWM signals**
   - Use oscilloscope or logic analyzer
   - Verify PWM frequency and duty cycle

### Robot Moves Erratically
**Symptoms:** Unexpected movement, spinning, not following commands

**Solutions:**
1. **Calibrate motor directions**
   ```cpp
   // Test each motor individually
   void calibrateMotors() {
       // Left motor forward
       digitalWrite(ML_Ctrl, HIGH);
       ledcWrite(PWM_CHANNEL_ML, 150);
       delay(2000);
       
       // Left motor backward
       digitalWrite(ML_Ctrl, LOW);
       ledcWrite(PWM_CHANNEL_ML, 150);
       delay(2000);
       
       // Stop and repeat for right motor
   }
   ```

2. **Balance power distribution**
   - Match motor speeds
   - Ensure equal wheel sizes
   - Check weight distribution

3. **Add encoders** for precise control (advanced)

### ESP32 Resets Randomly
**Symptoms:** ESP32 restarts, loses WiFi connection

**Solutions:**
1. **Check power stability**
   - Add large capacitor (1000µF) across power supply
   - Use dedicated 3.3V regulator
   - Measure voltage ripple

2. **Add watchdog timer**
   ```cpp
   #include <esp_task_wdt.h>
   
   void setup() {
       esp_task_wdt_init(10, true); // 10 second timeout
       esp_task_wdt_add(NULL);
   }
   
   void loop() {
       esp_task_wdt_reset();
       // Main code
   }
   ```

3. **Check for code issues**
   - Add error handling
   - Avoid blocking operations
   - Use smaller delay values

## Software Issues

### Import Errors
**Symptoms:** ModuleNotFoundError, ImportError

**Solutions:**
1. **Install missing packages**
   ```bash
   pip install -r requirements.txt
   ```

2. **Check Python version**
   ```bash
   python --version  # Should be 3.7+
   ```

3. **Use virtual environment**
   ```bash
   python -m venv gesture_env
   # Windows:
   gesture_env\Scripts\activate
   # Linux/Mac:
   source gesture_env/bin/activate
   
   pip install -r requirements.txt
   ```

### GUI Issues
**Symptoms:** GUI doesn't open, crashes, display problems

**Solutions:**
1. **Check PyQt5 installation**
   ```python
   try:
       from PyQt5.QtWidgets import QApplication
       print("PyQt5 installed correctly")
   except ImportError:
       print("PyQt5 not found - install with: pip install PyQt5")
   ```

2. **Update graphics drivers**
3. **Run with debug output**
   ```bash
   python src/gesture_control_gui.py --debug
   ```

### Settings Not Saving
**Symptoms:** Configuration resets after restart

**Solutions:**
1. **Check file permissions**
   ```python
   import os
   settings_file = "settings.json"
   if os.access(settings_file, os.W_OK):
       print("File writable")
   else:
       print("Permission denied")
   ```

2. **Use absolute paths**
   ```python
   import os
   settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')
   ```

## Getting Help

If you're still experiencing issues:

1. **Enable debug logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check system requirements**
   - Python 3.7+
   - 4GB RAM minimum
   - USB camera
   - WiFi capability

3. **Create minimal test case**
4. **Gather system information**
   ```python
   import platform
   import sys
   print(f"Python: {sys.version}")
   print(f"Platform: {platform.platform()}")
   print(f"Architecture: {platform.architecture()}")
   ```

5. **Report issues** with:
   - Operating system and version
   - Python version
   - Error messages and stack traces
   - Steps to reproduce
   - Hardware configuration

For additional support, check the project's GitHub issues or create a new issue with detailed information.