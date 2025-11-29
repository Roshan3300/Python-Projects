import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    model_complexity=0,  # Lightweight model
    min_detection_confidence=0.5,  # Lower detection confidence
    min_tracking_confidence=0.5  # Lower tracking confidence
)

# Initialize Video Capture
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Lower resolution for faster processing
cap.set(4, 480)

# Get screen size
screen_width, screen_height = pyautogui.size()

# Variables for mouse control
pinch_threshold = 50  # Distance threshold for pinch gesture
dragging = False  # Flag to check if dragging is active
prev_x, prev_y = 0, 0  # Previous cursor position

while True:
    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip the frame for mirror effect
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Hands
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get landmark positions
            landmarks = hand_landmarks.landmark

            # Get index finger tip (landmark 8) and thumb tip (landmark 4)
            index_tip = landmarks[8]
            thumb_tip = landmarks[4]
            middle_tip = landmarks[12]

            # Convert normalized coordinates to pixel values
            h, w, _ = frame.shape
            index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            middle_x, middle_y = int(middle_tip.x * w), int(middle_tip.y * h)
            es
            screen_x = np.interp(index_x, (0, w), (0, screen_width))
            screen_y = np.interp(index_y, (0, h), (0, screen_height))

            # Only move the cursor if the hand has moved significantlyqqq
            if abs(screen_x - prev_x) > 5 or abs(screen_y - prev_y) > 5:
                pyautogui.moveTo(screen_x, screen_y)
                prev_x, prev_y = screen_x, screen_y

            # Check for pinch gesture (index and thumb close together)
            # Map hand coordinates to screen coordinat
            distance = ((index_x - thumb_x) ** 2 + (index_y - thumb_y) ** 2) ** 0.5
            if distance < pinch_threshold:
                if not dragging:
                    pyautogui.mouseDown(button="left")  # Left click
                    dragging = True
            else:
                if dragging:
                    pyautogui.mouseUp(button="left")  # Release left click
                    dragging = False

            # Check for right click (middle and thumb close togetqqher)
            distance_right = ((middle_x - thumb_x) ** 2 + (middle_y - thumb_y) ** 2) ** 0.5
            if distance_right < pinch_threshold:
                pyautogui.rightClick()

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release resourcesqq
cap.release()
cv2.destroyAllWindows()