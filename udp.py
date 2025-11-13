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
    wrist = landmarks[0]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    thumb_tip = landmarks[4]

    # Calculate distance between index and thumb
    distance = ((landmarks[8].x - landmarks[4].x) ** 2 + (landmarks[8].y - landmarks[4].y) ** 2) ** 0.5

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
    try:
        udp_socket.sendto(command.encode(), (ESP32_IP, ESP32_PORT))
        print(f"Sent command: {command}")
    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"Failed to send command: {e}")


cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = hand_landmarks.landmark
            command = recognize_gesture(landmarks)

            cv2.putText(frame, f"Command: {command}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if command != "STOP":
                send_command_to_esp32(command)

    cv2.imshow("Hand Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
