from flask import Flask, Response, request, jsonify
import cv2
from hardware.robot import Robot
from hardware.camera import CameraService
from hardware.drivers import board, mecanum, sonar

import numpy as np

app = Flask(__name__)

# Initialize Hardware
bot = Robot()
# camera = CameraService()
# camera.start()
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640) 
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
turning = False
curAngle = 1500

ROBOT_STATE = {
    "speed": 0,         # Linear Speed (0-100)
    "direction": 90,    # Heading (0-360)
    "rotation": 0.0     # Angular Rate (-2.0 to 2.0)
}

def update_robot():
    bot.chassis.set_velocity(
        ROBOT_STATE["speed"], 
        ROBOT_STATE["direction"], 
        ROBOT_STATE["rotation"]
    )

def generate_frames():
    global has_saved_debug_image

    while True:
        # Capture frame-by-frame
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # Yield the output frame in the byte format required for MJPEG
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return """

    <h1>Robot Live Feed</h1>
    <img id="videoFeed" src='/video_feed' width='60%'> 
    <h1>Click Below for first person</h1>
    <canvas id="gameCanvas" width="1000" height="1000" style="border:1px solid #000000;"> </canvas>


    <script>
        let curAngle = 2200
        function updateMovement() {
            let route = "/move/";
            for (let i = 0; i < 5; i ++) {
                route += pressedKeys[movementKeys[i]];
            }
            console.log(route)
            fetch(route);
        }

        function updateCamera(dy,dx) {

            dxStr = dx.toString();
            turnRoute = "/turn/" + dxStr;
            fetch(turnRoute);

            curAngle += 3 * dy;
            if(curAngle > 2500){
                curAngle = 2500;
            }
            if(curAngle < 800){
                curAngle = 800;
            }
            dyStr = curAngle.toString();
            tiltRoute = "/tilt/" + dyStr
            fetch(tiltRoute);

        }


        const movementKeys = ['w', 'a', 's', 'd', 'f'];
        const cameraKeys = ['j', 'k'];
        const pressedKeys = {
            "w": '0',
            "a": '0',
            "s": '0', 
            "d": '0', 
            "f": '0', 
        };

        const canvas = document.getElementById('gameCanvas');

        canvas.addEventListener('click', () => {
            canvas.requestPointerLock();
        });

        document.addEventListener('pointerlockchange', () => {
            if (document.pointerLockElement === canvas) {
                console.log("Pointer locked");
            } else {
                console.log("Pointer unlocked");
            }
        });

        document.onkeydown = (e) => {
            console.log(e.key);
            if (e.key != e.key.toLowerCase()) {
                pressedKeys['f'] = '1';
            } else {
                pressedKeys['f'] = '0';

            }
            let pressedKey = e.key.toLowerCase();
            if (movementKeys.includes(pressedKey)) {
                if (!e.repeat) {
                    pressedKeys[pressedKey] = '1';
                    updateMovement();
                }
            }
        };


        document.onkeyup = (e) => {
            if (e.key != e.key.toLowerCase()) {
                pressedKeys['f'] = '0';
            }
            let releasedKey = e.key.toLowerCase();
            if (movementKeys.includes(releasedKey)) {
                pressedKeys[releasedKey] = '0';
                updateMovement();
            }
        };
    
        let mouseDeltaX = 0;
        let mouseDeltaY = 0;
        let turning = false;

        document.addEventListener('mousemove', (e) => {
            // Only update delta if pointer is locked
            if (document.pointerLockElement === canvas) {
                mouseDeltaX += e.movementX;
                mouseDeltaY += e.movementY;
            }
        });


        setInterval(() => {
            // Send movement to robot
            if(mouseDeltaX !== 0 ) {
                turning = true;
            }
            if ( turning) {
                updateCamera(mouseDeltaY,mouseDeltaX);
                turning = true;
                // Reset deltas after sending
                if(mouseDeltaX === 0) {
                    turning = false;
                }
                
                mouseDeltaX = 0;
                mouseDeltaY = 0;
            }
        }, 100); // every 50 ms (~20 updates per second)


    </script>
    """


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/move/<key>')
def move(key):
    s = int(key[4])
    y = int(key[0]) - int(key[2])
    x = int(key[3]) - int(key[1])
    if(x == 0 and y == 0):
        bot.chassis.set_velocity(0, 0, 0.0)
        return "OK", 200
    sp = 50
    if(s == 1):
        sp = 250
    angle = np.arctan2(y,x) * 180/(np.pi)
    bot.chassis.set_velocity(sp, angle, 0.0)
    # if 'f' in key:
    #     s = 75
    # if key == 'w':
    #     bot.chassis.set_velocity(s, 90, 0.0)
    # if key == 'd':
    #     bot.chassis.set_velocity(s, 0, 0.0a)
    # if key == 'a':
    #     bot.chassis.set_velocity(s, 180, 0.0)
    # if key == 's':
    #     bot.chassis.set_velocity(s, 270, 0.0)
    return "OK", 200


@app.route('/turn/<angle>')
def turn(angle):

    dx = float(angle)
    if(dx > 50 ):
        dx = 50
    if(dx <  -50):
        dx = -50
    if(np.abs(dx) < 10 and turning):
        bot.chassis.set_velocity(0,0,0)
        return "OK", 200
        
    bot.chassis.full_turn(dx)
    return "OK", 200

@app.route('/tilt/<angle>')
def tilt(angle):
    print(angle)
    board.setPWMServoPulse(1, int(angle), 400)
    return "OK", 200


@app.route('/stop')
def stop():
    bot.chassis.set_velocity(0, 0, 0.0)
    return "OK", 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        bot.stop()
        camera.stop()