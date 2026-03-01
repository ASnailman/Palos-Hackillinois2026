from flask import Flask, render_template_string, request, Response
import serial
import time
import cv2
from robot import Robot


app = Flask(__name__)
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640) 
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

bot = Robot()

# --- Arduino Initialization ---
try:
    arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.1)
    time.sleep(2)
    print("Arduino Connected. Web Server starting...")
except Exception as e:
    print(f"Connection failed: {e}")
    exit()

SPEED = 200

def send_to_arduino(cmd):
    arduino.write(f"{cmd}\n".encode('utf-8'))

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success: break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/')
def index():
    return render_template_string("""
    <img id="videoFeed" src='/video_feed' width='60%'> 

    <h1>Robot Web Teleop</h1>
    <p>Press WASD to move. Hold to continue moving.</p>
    <div id="status">Status: IDLE</div>
    <script>
    const pressedKeys = { w: 0, a: 0, s: 0, d: 0 };
    const cameraKeys = { "i": 0, "j": 0, "k": 0, "l": 0 };
    let cameraPitch = 1500;
    let cameraYaw = 1500;

    let currentCommand = "";

    function sendCommand(newCommand) {
        if (newCommand !== currentCommand) {
            fetch('/move/' + newCommand);
            currentCommand = newCommand;
            document.getElementById('status').innerText = "Sending: " + newCommand;
        }
    }

    function sendCamera() {
        if(cameraKeys["i"] == 1) {
            cameraYaw += 80;
        } 
        if(cameraKeys["j"] == 1) {
            cameraPitch -= 80;
        }
        if(cameraKeys["k"] == 1) {
            cameraYaw -= 80;
        } 
        if(cameraKeys["l"] == 1) {
            cameraPitch += 80;
        }
        if(cameraYaw < 500) {
            cameraYaw = 500;
        }
        if(cameraYaw > 2500) {
            cameraYaw = 2500;
        }
        if(cameraPitch < 500) {
            cameraPitch = 500;
        }
        if(cameraPitch > 2500) {
            cameraPitch = 2500;
        }

        pCommand = '/cam/' +  cameraPitch + ',' + cameraYaw;
        fetch(pCommand);

    }

    // --- Immediate Action ---
    document.onkeydown = (e) => {
        let key = e.key.toLowerCase();
        if (pressedKeys.hasOwnProperty(key)) {
            pressedKeys[key] = 1;
            let command = `${pressedKeys.w}${pressedKeys.a}${pressedKeys.s}${pressedKeys.d}`;
            sendCommand(command);
        }
        if(cameraKeys.hasOwnProperty(key)) {
            cameraKeys[key] = 1;
            sendCamera();
        }

    };

    document.onkeyup = (e) => {
        let key = e.key.toLowerCase();
        if (pressedKeys.hasOwnProperty(key)) {
            pressedKeys[key] = 0;
            let command = `${pressedKeys.w}${pressedKeys.a}${pressedKeys.s}${pressedKeys.d}`;
            sendCommand(command);
        }
        if(cameraKeys.hasOwnProperty(key)) {
            cameraKeys[key] = 0;
            sendCamera();
        }

    };

    // --- Periodic Heartbeat to keep Arduino from idling ---
</script>
    """)

@app.route('/move/<state>')
def move(state):
    print(state)
    w, a, s, d = [int(x) for x in state]

    # --- Movement logic ---
    if w:
        send_to_arduino(f"F,{SPEED}")
    elif s:
        send_to_arduino(f"B,{SPEED}")
    elif d:
        send_to_arduino("T,-30") 
    elif a:
        send_to_arduino("T,30")
    else:
        send_to_arduino("S,0")

    return "OK", 200

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/cam/<angle>')
def cam(angle):
    p,y = angle.split(',')
    iP = int(p)
    iY = int(y)
    if(iP > 2500):
        iP = 2500
    if(iP < 500):
        iP = 500
    if(iY > 2500):
        iY = 2500
    if(iY < 500):
        iY = 500

    bot.set_head(iY,iP)

    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)





    # setInterval(() => {
    #     if (currentCommand !== "0000") {
    #         // Re-send current active command to prevent Arduino timeout
    #         fetch('/move/' + currentCommand);
    #     }
    # }, 200); // Every 200ms
