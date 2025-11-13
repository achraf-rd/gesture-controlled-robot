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
    try:
        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # Send the command over UDP
            sock.sendto(command.encode(), (ESP32_IP, ESP32_PORT))
            print(f"Sent command: {command}")
    except Exception as e:
        print(f"Failed to send command: {e}")

# Main loop
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

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

            # Check if the hand is inside the top box (FORWARD)
            if (top_box_top_left[0] < index_mcp_x < top_box_bottom_right[0] and
                top_box_top_left[1] < index_mcp_y < top_box_bottom_right[1] and
                top_box_top_left[0] < middle_pip_x < top_box_bottom_right[0] and
                top_box_top_left[1] < middle_pip_y < top_box_bottom_right[1]):
                command = "BACKWARD"

            # Check if the hand is inside the bottom box (BACKWARD)
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

            # Display the command on the frame
            cv2.putText(frame, f"Command: {command}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Draw the control boxes
    cv2.rectangle(frame, top_box_top_left, top_box_bottom_right, (0, 0, 255), 2)
    cv2.rectangle(frame, bottom_box_top_left, bottom_box_bottom_right, (0, 0, 255), 2)

    # Send the command
    send_command_to_esp32(command)

    # Display the frame
    cv2.imshow("Hand Gesture Control", frame)

    # Exit loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
