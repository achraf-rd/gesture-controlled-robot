import cv2
import mediapipe as mp
import math
import socket

# WiFi Configuration
ESP32_IP = "192.168.137.205"  # Replace with your ESP32's IP
ESP32_PORT = 4210  # Port used by your ESP32

class GestureController:
    def __init__(self, esp32_ip=ESP32_IP, esp32_port=ESP32_PORT):
        # Network configuration
        self.esp32_ip = esp32_ip
        self.esp32_port = esp32_port
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.7
        )
        
        # Initialize Camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Calculate the screen center and box coordinates
        self.width = 1280
        self.height = 720
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Define the top and bottom box coordinates
        self.top_box_top_left = (center_x - 100, 0)
        self.top_box_bottom_right = (center_x + 100, 200)
        self.bottom_box_top_left = (center_x - 100, self.height - 200)
        self.bottom_box_bottom_right = (center_x + 100, self.height)
        
        self.running = False
    
    def send_command_to_esp32(self, command):
        """Send UDP command to ESP32."""
        try:
            # Create a UDP socket
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                # Send the command over UDP
                sock.sendto(command.encode(), (self.esp32_ip, self.esp32_port))
                print(f"Sent command: {command}")
        except Exception as e:
            print(f"Failed to send command: {e}")
    
    def process_frame(self, frame):
        """Process a single frame and return the command."""
        # Flip frame for a mirrored effect
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe
        result = self.hands.process(rgb_frame)
        
        command = "STOP"  # Default command
        
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
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
                index_mcp_x = int(index_mcp.x * self.width)
                index_mcp_y = int(index_mcp.y * self.height)
                middle_pip_x = int(middle_pip.x * self.width)
                middle_pip_y = int(middle_pip.y * self.height)
                
                # Check if the hand is inside the top box (BACKWARD)
                if (self.top_box_top_left[0] < index_mcp_x < self.top_box_bottom_right[0] and
                    self.top_box_top_left[1] < index_mcp_y < self.top_box_bottom_right[1] and
                    self.top_box_top_left[0] < middle_pip_x < self.top_box_bottom_right[0] and
                    self.top_box_top_left[1] < middle_pip_y < self.top_box_bottom_right[1]):
                    command = "BACKWARD"
                
                # Check if the hand is inside the bottom box (FORWARD)
                elif (self.bottom_box_top_left[0] < index_mcp_x < self.bottom_box_bottom_right[0] and
                      self.bottom_box_top_left[1] < index_mcp_y < self.bottom_box_bottom_right[1] and
                      self.bottom_box_top_left[0] < middle_pip_x < self.bottom_box_bottom_right[0] and
                      self.bottom_box_top_left[1] < middle_pip_y < self.bottom_box_bottom_right[1]):
                    command = "FORWARD"
                
                # Check for left or right turns based on angle
                elif angle > 20:
                    command = "RIGHT"
                elif angle < -20:
                    command = "LEFT"
                
                # Display the command on the frame
                cv2.putText(frame, f"Command: {command}", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Draw the control boxes
        cv2.rectangle(frame, self.top_box_top_left, self.top_box_bottom_right, (0, 0, 255), 2)
        cv2.rectangle(frame, self.bottom_box_top_left, self.bottom_box_bottom_right, (0, 0, 255), 2)
        cv2.putText(frame, "BACKWARD", (self.top_box_top_left[0], self.top_box_top_left[1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "FORWARD", (self.bottom_box_top_left[0], self.bottom_box_top_left[1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame, command
    
    def run(self):
        """Main loop for gesture control."""
        print("Starting gesture control...")
        print("Press 'q' to quit")
        
        self.running = True
        
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read frame from camera")
                break
            
            # Process frame and get command
            processed_frame, command = self.process_frame(frame)
            
            # Send command to ESP32
            self.send_command_to_esp32(command)
            
            # Display the frame
            cv2.imshow("Hand Gesture Control", processed_frame)
            
            # Check for quit command
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        print("Cleaning up...")
        self.running = False
        
        # Send stop command to ESP32
        self.send_command_to_esp32("STOP")
        
        # Release resources
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
        if self.hands:
            self.hands.close()

def main():
    """Main function to run the gesture controller."""
    try:
        # You can customize the IP and port here
        controller = GestureController(ESP32_IP, ESP32_PORT)
        controller.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Gesture control stopped")

if __name__ == "__main__":
    main()