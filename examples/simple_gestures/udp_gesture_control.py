import cv2
import mediapipe as mp
import socket

# WiFi Configuration
ESP32_IP = "192.168.137.154"  # Replace with the actual IP address of your ESP32
ESP32_PORT = 4210  # Port for UDP communication

# Initialize UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

def recognize_gesture(landmarks):
    """
    Enhanced gesture recognition with UDP communication.
    
    This example combines finger gesture recognition with
    network communication to control a remote robot.
    """
    wrist = landmarks[0]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    thumb_tip = landmarks[4]

    # Calculate distance between index and thumb
    distance = ((landmarks[8].x - landmarks[4].x) ** 2 + 
               (landmarks[8].y - landmarks[4].y) ** 2) ** 0.5

    if distance < 0.1:
        return "BACKWARD"

    if index_tip.y < middle_tip.y and index_tip.y < ring_tip.y and index_tip.y < pinky_tip.y:
        if index_tip.x < wrist.x:
            return "RIGHT"
        else:
            return "LEFT"

    if all(finger.y < wrist.y for finger in [index_tip, middle_tip, ring_tip, pinky_tip]):
        return "FORWARD"

    return "STOP"

def send_command_to_esp32(command):
    """Send UDP command to ESP32 with error handling."""
    try:
        udp_socket.sendto(command.encode(), (ESP32_IP, ESP32_PORT))
        print(f"Sent command: {command}")
        return True
    except socket.error as e:
        print(f"Socket error: {e}")
        return False
    except Exception as e:
        print(f"Failed to send command: {e}")
        return False

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Gesture Control with UDP Communication")
print(f"Connecting to ESP32 at {ESP32_IP}:{ESP32_PORT}")
print("Commands: FORWARD (all fingers), BACKWARD (pinch), LEFT/RIGHT (point)")
print("Press 'q' to quit")

last_command = ""
frame_count = 0

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        current_command = "STOP"
        
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                landmarks = hand_landmarks.landmark
                current_command = recognize_gesture(landmarks)
                
                # Add visual indicators for landmarks
                h, w, _ = frame.shape
                
                # Draw key landmarks
                key_points = [0, 4, 8, 12, 16, 20]  # wrist, thumb, fingers
                for point_id in key_points:
                    landmark = landmarks[point_id]
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(frame, (x, y), 5, (255, 255, 0), -1)
                
        # Only send command if it changed (reduce network traffic)
        if current_command != last_command:
            if send_command_to_esp32(current_command):
                last_command = current_command

        # Display status information
        cv2.putText(frame, f"Command: {current_command}", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.putText(frame, f"ESP32: {ESP32_IP}:{ESP32_PORT}", (50, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.putText(frame, f"Last sent: {last_command}", (50, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Connection status indicator
        connection_color = (0, 255, 0) if last_command else (0, 0, 255)
        cv2.circle(frame, (20, 20), 10, connection_color, -1)

        cv2.imshow("Gesture Control with UDP", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Cleanup
    print("Stopping robot...")
    send_command_to_esp32("STOP")
    
    cap.release()
    cv2.destroyAllWindows()
    udp_socket.close()
    hands.close()
    
    print("Gesture control stopped.")