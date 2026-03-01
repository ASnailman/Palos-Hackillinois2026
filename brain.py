import serial
import time
from robot import Robot

bot = Robot()
tt = 22.5
bot.set_head(1500,1500)
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
            print(line)
            if line.startswith("DIST:"):
                pass 
                
            elif line == "TURN_COMPLETE":
                print(f"Turn of {degrees} degrees successfully completed!")
                turning = False
                
        time.sleep(0.5) 

def startingBeep():
    bot.beep()
    time.sleep(1)
    bot.beep()
    time.sleep(1)
    bot.beep()

    return

def clearLeft():
    while(True):
        
        parity = 0
        arduino.write(b"F,200\n")
        while(True):
            if(bot.get_distance() < 25):
                arduino.write(b"S,0\n")
                break
        print("Hit Wall\n")
        time.sleep(1)
        if(parity == 1):
            execute_turn(90)
        else:
            execute_turn(-90)

        if(bot.get_distance() < 25):
            #end
            return
        print("rotated a bit\n")
        arduino.write(b"F,100\n")
        time.sleep(1)
        arduino.write(b"S,0\n")
        time.sleep(1)
        if(parity == 1):
            execute_turn(90)
        else:
            execute_turn(-90)
        parity = 1- parity
        time.sleep(0.5)

def clearSand():
    clearLeft()    
    return 0

def getDistance():
    d = arduino.readline().decode().strip()
    print("Front Sonar: " + d)
    try:
        return float(d)
    except:
        return 10000

def turn_at_wall(direction):
    if direction == "forward":
        arduino.write(b"B,200\n")
        time.sleep(0.5)
        execute_turn(90)
        arduino.write(b"F,200\n")
        time.sleep(0.5)
        if(bot.get_distance() < tt):
            execute_turn(90)
            return True
        execute_turn(90)
        return False
    elif direction == "backward":
        arduino.write(b"B,200\n")
        time.sleep(0.5)
        execute_turn(-90)
        arduino.write(b"F,200\n")
        time.sleep(0.5)
        if(bot.get_distance() < tt):
            execute_turn(-90)
            return False

        execute_turn(-90)
        return True


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
    #Safety Feature
    # bot.beep_succession(3,0.8)
    #PID
    setPid(2.4,0.2,0.01)
    time.sleep(1.5)
    # arduino.write(b"S,0\n")

    # execute_turn(90)
    # arduino.write(b"F,200\n")
    # time.sleep(0.5)
    # arduino.write(b"S,0\n")
    # time.sleep(0.5)
    # execute_turn(90)
        
    # clearLeft()
    # arduino.write(b"F,200\n")
    # time.sleep(0.5)
    # arduino.write(b"S,0\n")
    # time.sleep(0.5)
    # execute_turn(-45)
    # time.sleep(1.0)

    # arduino.write(b"F,200\n")
    # time.sleep(0.5)
    # arduino.write(b"S,0\n")

    forward = True
    for i in range(6):
        while bot.get_distance2() > tt:
            arduino.write(b"F,200\n")    
        arduino.write(b"S,0\n")
        if (forward):
            forward = turn_at_wall("forward")
            
        else:
            forward = turn_at_wall("backward")

    # while(True):
    #     print(bot.get_distance2())

except KeyboardInterrupt:
    print("Test aborted by user. Stopping.")
    arduino.write(b"S,0\n")



#setPid(2.4,0.2,0.01)
