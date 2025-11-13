import cv2
import mediapipe as mp
import math
import socket

# WiFi Configuration
ESP32_IP = "192.168.137.205"  # Replace with your ESP32's IP
ESP32_PORT = 4210  # Port used by your ESP32

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Initialize Camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Calculate the screen center and box coordinates
width = 1280
height = 720
center_x = width // 2
center_y = height // 2

# Define the top and bottom box coordinates
top_box_top_left = (center_x - 100, 0)
top_box_bottom_right = (center_x + 100, 200)
bottom_box_top_left = (center_x - 100, height - 200)
bottom_box_bottom_right = (center_x + 100, height)

# Function to send commands to ESP32
def send_command_to_esp32(command):
    """Send UDP command to ESP32."""
    try:
        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # Send the command over UDP
            sock.sendto(command.encode(), (ESP32_IP, ESP32_PORT))
            print(f"Sent command: {command}")
    except Exception as e:
        print(f"Failed to send command: {e}")

print("Zone-Based Hand Gesture Control")
print("Controls:")
print("- Top red zone: BACKWARD")
print("- Bottom red zone: FORWARD") 
print("- Hand angle > 20°: RIGHT")
print("- Hand angle < -20°: LEFT")
print("- Default: STOP")
print("Press 'q' to quit")

# Main loop
last_command = ""
frame_count = 0

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Flip frame for a mirrored effect
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe
        result = hands.process(rgb_frame)

        command = "STOP"  # Default command

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
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

                # Determine if landmarks[9] and landmarks[13] are in the boxes
                index_mcp = landmarks[9]
                middle_pip = landmarks[13]

                # Convert normalized coordinates to pixel coordinates
                index_mcp_x = int(index_mcp.x * width)
                index_mcp_y = int(index_mcp.y * height)
                middle_pip_x = int(middle_pip.x * width)
                middle_pip_y = int(middle_pip.y * height)

                # Draw circles at key landmarks for debugging
                cv2.circle(frame, (index_mcp_x, index_mcp_y), 8, (255, 255, 0), -1)
                cv2.circle(frame, (middle_pip_x, middle_pip_y), 8, (0, 255, 255), -1)

                # Check if the hand is inside the top box (BACKWARD)
                if (top_box_top_left[0] < index_mcp_x < top_box_bottom_right[0] and
                    top_box_top_left[1] < index_mcp_y < top_box_bottom_right[1] and
                    top_box_top_left[0] < middle_pip_x < top_box_bottom_right[0] and
                    top_box_top_left[1] < middle_pip_y < top_box_bottom_right[1]):
                    command = "BACKWARD"

                # Check if the hand is inside the bottom box (FORWARD)
                elif (bottom_box_top_left[0] < index_mcp_x < bottom_box_bottom_right[0] and
                      bottom_box_top_left[1] < index_mcp_y < bottom_box_bottom_right[1] and
                      bottom_box_top_left[0] < middle_pip_x < bottom_box_bottom_right[0] and
                      bottom_box_top_left[1] < middle_pip_y < bottom_box_bottom_right[1]):
                    command = "FORWARD"

                # Check for left or right turns based on angle
                elif angle > 20:
                    command = "RIGHT"
                elif angle < -20:
                    command = "LEFT"

                # Display the angle for debugging
                cv2.putText(frame, f"Angle: {angle:.1f}°", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Draw angle visualization line
                center_point = (int(wrist.x * width), int(wrist.y * height))
                end_x = int(center_point[0] + 100 * math.cos(math.radians(angle + 90)))
                end_y = int(center_point[1] + 100 * math.sin(math.radians(angle + 90)))
                cv2.line(frame, center_point, (end_x, end_y), (0, 255, 0), 3)

        # Draw the control boxes
        cv2.rectangle(frame, top_box_top_left, top_box_bottom_right, (0, 0, 255), 3)
        cv2.rectangle(frame, bottom_box_top_left, bottom_box_bottom_right, (0, 0, 255), 3)
        
        # Add zone labels
        cv2.putText(frame, "BACKWARD", (top_box_top_left[0], top_box_top_left[1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(frame, "FORWARD", (bottom_box_top_left[0], bottom_box_top_left[1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Display current command with background
        command_text = f"Command: {command}"
        text_size = cv2.getTextSize(command_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        
        # Command color coding
        command_colors = {
            "FORWARD": (0, 255, 0),
            "BACKWARD": (0, 0, 255),
            "LEFT": (255, 0, 0),
            "RIGHT": (255, 0, 255),
            "STOP": (128, 128, 128)
        }
        
        command_color = command_colors.get(command, (255, 255, 255))
        cv2.rectangle(frame, (40, 20), (text_size[0] + 60, text_size[1] + 50), command_color, -1)
        cv2.putText(frame, command_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Send command only if it changed (reduce network traffic)
        if command != last_command:
            send_command_to_esp32(command)
            last_command = command

        # Display frame info
        cv2.putText(frame, f"Frame: {frame_count}", (width - 150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Display the frame
        cv2.imshow("Zone-Based Hand Gesture Control", frame)

        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Send final stop command
    print("Stopping robot...")
    send_command_to_esp32("STOP")
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    
    print("Zone-based gesture control ended.")