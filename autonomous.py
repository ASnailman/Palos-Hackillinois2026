from flask import Flask, render_template_string, Response
import cv2
import time
from robot import Robot
import threading

app = Flask(__name__)
bot = Robot()

# --- Camera Setup ---
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# --- Stop signal from web ---
stop_robot = False

def autonomous_loop():
    global stop_robot
    print("Robot Started Moving")
    try:
        while not stop_robot:
            dist = bot.get_distance()
            if dist is None:
                dist = 100  # assume clear
            if dist > 20:
                bot.move_forward(100)  # Move forward
            else:
                bot.move_forward(0)   # Stop
                # bot.full_turn(50)   # Turn - commented out until leveler_motors is fixed
                time.sleep(0.2)
    finally:
        bot.move_forward(0)
        print("Robot Stopped")

# --- Web Routes ---
@app.route('/')
def index():
    return render_template_string("""
        <h1>Autonomous Robot</h1>
        <button onclick="fetch('/stop')">Stop Robot</button>
        <img src='/video_feed' width='60%'>
        <script>
            document.addEventListener('keydown', e => {
                if (e.key === "Escape") fetch('/stop');
            });
        </script>
    """)

@app.route('/stop')
def stop():
    global stop_robot
    stop_robot = True
    return "Stopping", 200

# --- Video Feed ---
def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# --- Main ---
if __name__ == '__main__':
    threading.Thread(target=autonomous_loop, daemon=True).start()
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        bot.move_forward(0)
        camera.release()