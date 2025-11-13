import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Define the hand tracking module
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

def recognize_gesture(landmarks):
    """
    Recognize hand gestures based on finger positions.
    
    This is a finger-based gesture recognition system that analyzes
    the relative positions of fingertips to determine commands.
    """
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

    # Calculate distance between index finger and thumb (pinch gesture)
    pinch_distance = ((landmarks[8].x - landmarks[4].x)**2 + 
                     (landmarks[8].y - landmarks[4].y)**2)**0.5

    # Gesture recognition logic
    if pinch_distance < 0.1:
        return "BACKWARD"  # Pinch gesture = backward
    
    # Pointing gesture (only index finger up)
    if index_tip.y < middle_tip.y and index_tip.y < ring_tip.y and index_tip.y < pinky_tip.y:
        if index_tip.x < wrist.x:
            return "RIGHT"  # Point left (mirrored)
        else:
            return "LEFT"   # Point right (mirrored)

    # All fingers up = forward
    if all(finger.y < wrist.y + abs(pinky_tip.x - thumb_tip.x) 
           for finger in [index_tip, middle_tip, ring_tip, pinky_tip]):
        return "FORWARD"

    return "STOP"  # Default state

# Start video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Finger Gesture Recognition Demo")
print("Gestures:")
print("- Pinch (index + thumb): BACKWARD")
print("- Point with index finger: LEFT/RIGHT")
print("- All fingers up: FORWARD")
print("- Default: STOP")
print("Press 'q' to quit")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame horizontally for mirror effect
    frame = cv2.flip(frame, 1)
    
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

            # Display command with colored background
            text_size = cv2.getTextSize(f"Command: {command}", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            
            # Choose color based on command
            colors = {
                "FORWARD": (0, 255, 0),    # Green
                "BACKWARD": (0, 0, 255),   # Red
                "LEFT": (255, 0, 0),       # Blue
                "RIGHT": (255, 0, 255),    # Magenta
                "STOP": (128, 128, 128)    # Gray
            }
            color = colors.get(command, (255, 255, 255))
            
            # Draw background rectangle
            cv2.rectangle(frame, (10, 10), (text_size[0] + 20, text_size[1] + 30), color, -1)
            
            # Display command text
            cv2.putText(frame, f"Command: {command}", (15, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    else:
        # No hand detected
        cv2.putText(frame, "No hand detected", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Show the frame
    cv2.imshow("Finger Gesture Recognition", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
hands.close()

print("Finger gesture recognition demo ended.")