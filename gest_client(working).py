import cv2
import mediapipe as mp
import socket

# WiFi Configuration
ESP32_IP = "192.168.137.54"  # Replace with the actual IP address of your ESP32
ESP32_PORT = 4210  # Your ESP32's UDP port (make sure it matches the port on the ESP32 side)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Define the hand tracking module
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

def recognize_gesture(landmarks):
    wrist = landmarks[0]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    thumb_tip = landmarks[4]

    # Calculate distance between index and thumb
    distance = ((landmarks[8].x - landmarks[4].x) ** 2 + (landmarks[8].y - landmarks[4].y) ** 2) ** 0.5

    # Debugging: Print distance to verify gesture recognition
    print(f"Distance between index and thumb: {distance}")

    if distance < 0.1:
        return "BACKWARD"

    if index_tip.y < middle_tip.y and index_tip.y < ring_tip.y and index_tip.y < pinky_tip.y:
        if index_tip.x < wrist.x:
            return "RIGHT"
        else:
            return "LEFT"

    if all(finger.y < wrist.y for finger in [index_tip, middle_tip, ring_tip, pinky_tip]):
        return "FORWARD"

    return "UNKNOWN"

def send_command_to_esp32(command):
    try:
        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # Send the command over UDP
            sock.sendto(command.encode(), (ESP32_IP, ESP32_PORT))
            print(f"Sent command: {command}")
    except Exception as e:
        print(f"Failed to send command: {e}")

# Open the PC's camera (device index 0)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB as MediaPipe uses RGB format
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    # If hands are detected, process them
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw hand landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            landmarks = hand_landmarks.landmark
            command = recognize_gesture(landmarks)

            # Debugging: Print the recognized command
            print(f"Recognized command: {command}")

            # Display the command on the screen
            cv2.putText(frame, f"Command: {command}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # If a valid gesture is detected (command is not "UNKNOWN"), send the command
            if command != "UNKNOWN":
                send_command_to_esp32(command)

    # Show the frame with the recognized gestures and control command
    cv2.imshow("Hand Gesture Control", frame)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
