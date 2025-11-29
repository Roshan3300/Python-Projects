# === UPGRADED VISUAL 3D AIR TENNIS GAME ===
# Includes: Neon effects, energy trails, 3D illusion, glowing paddles

import cv2
import numpy as np
import mediapipe as mp
import random
import math
import threading
import time
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit

# === Flask Setup ===
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
player2_x = 400

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <title>Player 2 Paddle</title>
  <style>
    html, body { margin: 0; height: 100%; background: #000; overflow: hidden; }
    #court { width: 100%; height: 100%; background: #111; position: relative; }
    #paddle { width: 60px; height: 20px; background: magenta; position: absolute; top: 10px; left: 50%; transform: translateX(-50%); border-radius: 10px; box-shadow: 0 0 20px magenta; }
  </style>
</head>
<body>
  <div id="court">
    <div id="paddle"></div>
  </div>
  <script src="https://cdn.socket.io/4.6.1/socket.io.min.js"></script>
  <script>
    const socket = io();
    const paddle = document.getElementById('paddle');
    document.addEventListener('mousemove', e => {
      const x = e.clientX;
      paddle.style.left = x + 'px';
      socket.emit('paddle_update', { x });
    });
  </script>
</body>
</html>
""")

@socketio.on('paddle_update')
def handle_paddle(data):
    global player2_x
    player2_x = data['x']

# === MediaPipe ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8)

# === Game Constants ===
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 12
PADDLE_RADIUS = 35
BALL_SPEED = 6

ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_vel = [random.uniform(-BALL_SPEED, BALL_SPEED), BALL_SPEED]
player1_x = WIDTH // 2
player2_x_local = WIDTH // 2
player_score = 0
opponent_score = 0
game_active = False
ball_trail = []


def reset_ball():
    global ball_pos, ball_vel, game_active, ball_trail
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    angle = random.uniform(-1, 1)
    ball_vel = [angle * BALL_SPEED, BALL_SPEED * random.choice([-1, 1])]
    ball_trail = []
    game_active = False


def draw_table(frame):
    bg = np.zeros_like(frame)
    cv2.rectangle(bg, (50, 50), (WIDTH - 50, HEIGHT - 50), (40, 40, 40), 2)
    for i in range(1, 6):
        y = 50 + i * (HEIGHT - 100) // 6
        cv2.line(bg, (50, y), (WIDTH - 50, y), (30, 30, 30), 1)
    cv2.addWeighted(bg, 0.3, frame, 0.7, 0, frame)


def draw_glowing_circle(frame, center, radius, color):
    overlay = frame.copy()
    glow = frame.copy()
    for i in range(3):
        cv2.circle(glow, center, radius + i * 5, color, 2)
    cv2.addWeighted(glow, 0.3, overlay, 0.7, 0, frame)
    cv2.circle(frame, center, radius, color, -1)
    cv2.circle(frame, center, radius, (255, 255, 255), 2)


def draw_ball(frame, x, y):
    global ball_trail
    depth = 1 - abs((y - HEIGHT // 2) / (HEIGHT // 2))
    radius = int(BALL_RADIUS * (0.7 + 0.5 * depth))
    ball_trail.append((int(x), int(y), radius))
    if len(ball_trail) > 10:
        ball_trail.pop(0)

    for i, (tx, ty, tr) in enumerate(ball_trail):
        alpha = i / len(ball_trail)
        cv2.circle(frame, (tx, ty), tr, (255, 255, 255), -1)
        cv2.circle(frame, (tx, ty), tr, (100, 255, 255), 1)


def game_loop():
    global player1_x, player2_x_local, ball_pos, ball_vel
    global player_score, opponent_score, game_active

    cap = cv2.VideoCapture(0)
    cap.set(3, WIDTH)
    cap.set(4, HEIGHT)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        draw_table(frame)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            x_landmark = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            player1_x = int(x_landmark.x * WIDTH)
            game_active = True

        player2_x_local = np.clip(player2_x, 50, WIDTH - 50)

        if game_active:
            ball_pos[0] += ball_vel[0]
            ball_pos[1] += ball_vel[1]

            if ball_pos[0] <= 50 or ball_pos[0] >= WIDTH - 50:
                ball_vel[0] *= -1

            if HEIGHT - 70 < ball_pos[1] < HEIGHT - 50:
                if abs(ball_pos[0] - player1_x) < PADDLE_RADIUS:
                    ball_vel[1] *= -1
                    offset = (ball_pos[0] - player1_x) / PADDLE_RADIUS
                    ball_vel[0] += offset * 3

            if 50 < ball_pos[1] < 70:
                if abs(ball_pos[0] - player2_x_local) < PADDLE_RADIUS:
                    ball_vel[1] *= -1
                    offset = (ball_pos[0] - player2_x_local) / PADDLE_RADIUS
                    ball_vel[0] += offset * 3

            if ball_pos[1] <= 30:
                player_score += 1
                reset_ball()
            elif ball_pos[1] >= HEIGHT - 30:
                opponent_score += 1
                reset_ball()

        draw_ball(frame, ball_pos[0], ball_pos[1])
        draw_glowing_circle(frame, (player1_x, HEIGHT - 60), PADDLE_RADIUS, (0, 255, 255))
        draw_glowing_circle(frame, (int(player2_x_local), 60), PADDLE_RADIUS, (255, 0, 255))

        cv2.putText(frame, f"You: {player_score}", (WIDTH - 220, HEIGHT - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Opponent: {opponent_score}", (50, HEIGHT - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow("🔥 Air Tennis: Visual FX Edition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    threading.Thread(target=game_loop).start()
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
