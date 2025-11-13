import cv2
import dlib
import numpy as np

# Load dlib's face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Download this file from dlib's website

# Camera intrinsic parameters (approximate values, can be calibrated for better accuracy)
focal_length = 950  # Focal length of the camera
center = (320, 240)  # Center of the frame (assuming 640x480 resolution)
camera_matrix = np.array([[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]], dtype=np.float32)

# Distortion coefficients (assume no lens distortion)
dist_coeffs = np.zeros((4, 1))

# 3D model points for the head
model_points = np.array([
    (0.0, 0.0, 0.0),          # Nose tip
    (0.0, -330.0, -65.0),     # Chin
    (-225.0, 170.0, -135.0),  # Left eye left corner
    (225.0, 170.0, -135.0),   # Right eye right corner
    (-150.0, -150.0, -125.0), # Left mouth corner
    (150.0, -150.0, -125.0)   # Right mouth corner
], dtype=np.float32)

# Function to calculate head pose
def get_head_pose(shape, frame):
    # 2D image points from facial landmarks
    image_points = np.array([
        (shape.part(30).x, shape.part(30).y),  # Nose tip
        (shape.part(8).x, shape.part(8).y),    # Chin
        (shape.part(36).x, shape.part(36).y),  # Left eye left corner
        (shape.part(45).x, shape.part(45).y),  # Right eye right corner
        (shape.part(48).x, shape.part(48).y),  # Left mouth corner
        (shape.part(54).x, shape.part(54).y)   # Right mouth corner
    ], dtype=np.float32)

    # Solve for pose
    success, rotation_vector, translation_vector = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs)

    # Project a 3D axis to visualize head pose
    axis = np.float32([[200, 0, 0], [0, 200, 0], [0, 0, 200]]).reshape(-1, 3)
    imgpts, _ = cv2.projectPoints(axis, rotation_vector, translation_vector, camera_matrix, dist_coeffs)
    frame = draw_axis(frame, image_points[0], imgpts)

    return rotation_vector, translation_vector

# Function to draw the 3D axis on the frame
def draw_axis(frame, nose_tip, imgpts):
    nose_tip = tuple(map(int, nose_tip))
    imgpts = np.int32(imgpts).reshape(-1, 2)
    cv2.line(frame, nose_tip, tuple(imgpts[0]), (0, 0, 255), 3)  # X-axis (Red)
    cv2.line(frame, nose_tip, tuple(imgpts[1]), (0, 255, 0), 3)  # Y-axis (Green)
    cv2.line(frame, nose_tip, tuple(imgpts[2]), (255, 0, 0), 3)  # Z-axis (Blue)
    return frame

# Capture video from the webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = detector(gray)

    for face in faces:
        # Predict facial landmarks
        shape = predictor(gray, face)

        # Get head pose
        rotation_vector, translation_vector = get_head_pose(shape, frame)

        # Convert rotation vector to rotation matrix
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

        # Extract head pose angles
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rotation_matrix)

        # Gesture recognition logic
        if angles[1] < -10:  # Head tilted to the left
            print("Left")
        elif angles[1] > 10:  # Head tilted to the right
            print("Right")
        elif angles[0] < -10:  # Head nodding down
            print("Forward")
        elif angles[0] > 10:  # Head nodding up
            print("Backward")
        else:
            print("No Gesture")

    # Display the frame
    cv2.imshow('Head Pose Estimation', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()