import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils  # Drawing utilities
hands = mp_hands.Hands(
    model_complexity=1,  # Use complex model
    min_detection_confidence=0.75,  # Higher detection confidence
    min_tracking_confidence=0.75  # Better tracking stability
)

# Initialize Video Capture
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)  # Height

# Keyboard layout
keys = [
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '⌫'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ' ', ',', '.']
]

# Keyboard dimensions
key_width = 85
key_height = 85
key_gap = 10
key_roundness = 15  # Rounded corners

# Color scheme
colors = {
    "key": (51, 51, 51),
    "hover": (102, 204, 255),
    "text": (255, 255, 255),
    "special": (255, 102, 102),
    "bg": (240, 240, 240)
}

text = ""
last_key_press_time = 0
cooldown = 0.5  # Prevent repeated keypresses
key_pressed = False


def draw_rounded_rect(frame, x, y, w, h, color, radius):
    """
    Draw a rectangle with rounded corners.
    """
    cv2.rectangle(frame, (x + radius, y), (x + w - radius, y + h), color, -1)
    cv2.rectangle(frame, (x, y + radius), (x + w, y + h - radius), color, -1)
    cv2.circle(frame, (x + radius, y + radius), radius, color, -1)
    cv2.circle(frame, (x + w - radius, y + radius), radius, color, -1)
    cv2.circle(frame, (x + radius, y + h - radius), radius, color, -1)
    cv2.circle(frame, (x + w - radius, y + h - radius), radius, color, -1)


def draw_keyboard(frame):
    """
    Draw the virtual keyboard on the frame.
    """
    overlay = frame.copy()  # Create a copy for transparency effect

    # Reduce background brightness for better hand visibility
    cv2.addWeighted(frame, 0.5, overlay, 0.5, 0, frame)

    # Display text area
    draw_rounded_rect(overlay, 50, 50, 1180, 80, (255, 255, 255), 15)
    cv2.putText(overlay, text[-35:], (70, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    # Draw keys
    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            x = j * (key_width + key_gap) + 50
            y = i * (key_height + key_gap) + 150

            key_color = colors["special"] if key == '⌫' else colors["key"]
            draw_rounded_rect(overlay, x, y, key_width, key_height, key_color, key_roundness)

            text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            text_x = x + (key_width - text_size[0]) // 2
            text_y = y + (key_height + text_size[1]) // 2
            cv2.putText(overlay, key, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors["text"], 2)

    # Blend the overlay onto the frame (transparent effect)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)


def get_hovered_key(x, y):

    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            key_x = j * (key_width + key_gap) + 50
            key_y = i * (key_height + key_gap) + 150

            if key_x - 5 < x < key_x + key_width + 5 and key_y - 5 < y < key_y + key_height + 5:
                return key, key_x, key_y
    return None, 0, 0


while True:
    ret, frame = cap.read()
    # if not ret:
    #     print("⚠️ Camera not working! Check your webcam.")
    #     break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    current_time = cv2.getTickCount() / cv2.getTickFrequency()

    # Draw hand landmarks **before** keyboard, so they are visible
    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            # Get landmarks for thumb and index finger
            thumb_tip = hand.landmark[4]
            index_tip = hand.landmark[8]
            index_mcp = hand.landmark[5]  # Middle of the index finger (MCP joint)

            h, w, _ = frame.shape
            ix, iy = int(index_tip.x * w), int(index_tip.y * h)  # Index finger tip
            tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)  # Thumb tip
            mx, my = int(index_mcp.x * w), int(index_mcp.y * h)  # Middle of index finger

            # Calculate distance between thumb and index finger (tip and middle)
            distance_tip = np.hypot(ix - tx, iy - ty)  # Distance between thumb tip and index tip
            distance_mid = np.hypot(mx - tx, my - ty)  # Distance between thumb tip and index middle

            # Use the minimum distance to determine the pinch gesture
            distance = min(distance_tip, distance_mid)

            hovered_key, kx, ky = get_hovered_key(ix, iy)

            # Draw hover effect
            if hovered_key:
                draw_rounded_rect(frame, kx, ky, key_width, key_height, colors["hover"], key_roundness)
                text_size = cv2.getTextSize(hovered_key, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                text_x = kx + (key_width - text_size[0]) // 2
                text_y = ky + (key_height + text_size[1]) // 2
                cv2.putText(frame, hovered_key, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

            # Key Press Logic (Ensures keys don't get stuck)
            if distance < 30:  # Adjusted pinch threshold
                if not key_pressed or (current_time - last_key_press_time) > cooldown:
                    if hovered_key:
                        if hovered_key == '⌫':
                            text = text[:-1]  # Delete last character
                        else:
                            text += hovered_key.lower()
                        last_key_press_time = current_time
                        key_pressed = True
            else:
                key_pressed = False

    draw_keyboard(frame)  # Keyboard drawn **after** landmarks
    cv2.imshow("Premium Virtual Keyboard", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()