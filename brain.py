import serial
import time

try:
    arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.1)
    time.sleep(2)
except Exception as e:
    print(f"Connection failed: {e}")
    exit()

def execute_turn(degrees):
    """
    Sends a turn command and blocks the Python script until 
    the Arduino physically finishes the rotation.
    """
    print(f"Commanding turn: {degrees} degrees...")
    
    command = f"T,{degrees}\n"
    arduino.write(command.encode('utf-8'))
    
    turning = True
    while turning:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').strip()
            
            if line.startswith("DIST:"):
                pass 
                
            elif line == "TURN_COMPLETE":
                print(f"Turn of {degrees} degrees successfully completed!")
                turning = False
                
        time.sleep(0.01) 


def setPid(Kp,Ki,Kd):
    p = f"P,{Kp}\n"
    i = f"I,{Ki}\n"
    d = f"D,{Kd}\n"

    arduino.write(p.encode('utf-8'))
    time.sleep(0.05)
    arduino.write(i.encode('utf-8'))
    time.sleep(0.05)
    arduino.write(d.encode('utf-8'))
    time.sleep(0.05)

try:
    #PID
    setPid(2.4,0.2,0.01)
    time.sleep(1)

    # # Movement
    arduino.write(b"F,200\n")
    time.sleep(5)
    arduino.write(b"B,200\n")
    time.sleep(5)
    arduino.write(b"S,0\n")

except KeyboardInterrupt:
    print("Test aborted by user. Stopping.")
    arduino.write(b"S,0\n")