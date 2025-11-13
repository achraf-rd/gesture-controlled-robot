import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Define the hand tracking module
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

def recognize_gesture(landmarks):
    # Extract key points
    wrist = landmarks[0]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    thumb_tip = landmarks[4]

    # Function to calculate Euclidean distance
    def distance(point1, point2):
        return np.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    # Check if all fingers are tightly curled (closed fist)
   
    # distance = ((index_tip.x - thumb_tip.x)**2 + (index_tip.y - thumb_tip.y)**2)**0.5
    distance = ((landmarks[8].x - landmarks[4].x)**2 + (landmarks[8].y - landmarks[4].y)**2)**0.5

    # Gesture recognition
     
    if distance < 0.1 :
        return "BACKWARD"
    
    if index_tip.y < middle_tip.y and index_tip.y < ring_tip.y and index_tip.y < pinky_tip.y:
        if index_tip.x < wrist.x:
            return "RIGHT"
        else:
            return "LEFT"

    if all(finger.y < wrist.y + abs(pinky_tip.x - thumb_tip.x) for finger in [index_tip, middle_tip, ring_tip, pinky_tip]):
        return "FORWARD"

    return "UNKNOWN"

# Start video capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    # Process detected hands
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Convert landmarks to list
            landmarks = hand_landmarks.landmark
            command = recognize_gesture(landmarks)

            # Display command
            cv2.putText(frame, f"Command: {command}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the frame
    cv2.imshow("Hand Gesture Control", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
