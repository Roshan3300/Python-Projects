import cv2
import mediapipe as mp
import os
import numpy as np

# Load header images from folder
folderPath = "header"
myList = os.listdir(folderPath)
print(myList)

overlayList = [cv2.imread(f'{folderPath}/{imPath}') for imPath in myList]
print(f"Loaded {len(overlayList)} images")
header = overlayList[0]  # Default header image

# Initialize Video Capture
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height

# Initialize MediaPipe Hand Detection
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

hand_detector = mp_hands.Hands(
    model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5
)

# Drawing Variables
drawColor = (255, 0, 255)  # Default drawing color (pink)
brushThickness = 15
eraserThickness = 70
xp, yp = 0, 0  # Previous x and y coordinates
imgCanvas = np.zeros((720, 1280, 3), np.uint8)  # Canvas for drawing

# Header Dimensions
headerHeight = 118  # Height of the header image

# Define regions for color and eraser selection
colorRegions = {
    "pink": (150, 300),
    "red": (300, 500),
    "green": (600, 900),
    "eraser": (900, 1050)
}

while True:
    # Read frame from webcam
    r, frame = cap.read()
    if not r:
        break

    frame = cv2.flip(frame, 1)  # Flip the frame for mirror effect

    # Convert frame to RGB for MediaPipe
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hand_detector.process(imgRGB)

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            # Draw landmarks on the frame
            mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the landmark positions
            lmList = []
            for id, lm in enumerate(landmarks.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

            if len(lmList) != 0:
                # Check which fingers are up
                fingers = []
                # Thumb
                if lmList[4][1] > lmList[3][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
                # Index, Middle, Ring, Pinky
                for tip in [8, 12, 16, 20]:
                    if lmList[tip][2] < lmList[tip - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                # Selection Mode: Two fingers up (Index and Middle)
                if fingers[1] == 1 and fingers[2] == 1:
                    xp, yp = 0, 0  # Reset previous points
                    # Check if the hand is in the header area
                    if lmList[8][2] < headerHeight:  # Index finger in header area
                        # Select the tool/color based on the x position
                        for color, (x1, x2) in colorRegions.items():
                            if x1 < lmList[8][1] < x2:
                                if color == "eraser":
                                    drawColor = (0, 0, 0)  # Eraser (black)
                                else:
                                    if color == "pink":
                                        drawColor = (255, 0, 255)  # Pink
                                    elif color == "green":
                                        drawColor = (0, 255, 0)  # Green
                                    elif color == "red":
                                        drawColor = (0, 0, 255)  # Red
                                    elif color == "erase":
                                        drawColor = (0, 0, 0)  # Red
                                break

                # Drawing Mode: Index finger up
                if fingers[1] == 1 and fingers[2] == 0:
                    # Ensure drawing happens below the header
                    if lmList[8][2] > headerHeight:
                        cv2.circle(frame, (lmList[8][1], lmList[8][2]), 15, drawColor, cv2.FILLED)
                        if xp == 0 and yp == 0:
                            xp, yp = lmList[8][1], lmList[8][2]

                        # Draw on the canvas
                        if drawColor == (0, 0, 0):  # Eraser
                            cv2.line(imgCanvas, (xp, yp), (lmList[8][1], lmList[8][2]), drawColor, eraserThickness)
                        else:
                            cv2.line(imgCanvas, (xp, yp), (lmList[8][1], lmList[8][2]), drawColor, brushThickness)

                        xp, yp = lmList[8][1], lmList[8][2]

    # Merge the canvas and the frame
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    frame = cv2.bitwise_and(frame, imgInv)
    frame = cv2.bitwise_or(frame, imgCanvas)

    # Display header at the top
    frame[0:headerHeight, 0:1015] = header

    cv2.imshow("Virtual Drawing", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()