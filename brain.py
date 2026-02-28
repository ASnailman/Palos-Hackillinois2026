import serial
import time

try:
    arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    time.sleep(2)
    print("Wireless link established with Arduino!")
    
    print("Commanding: FORWARD")
    arduino.write(b"F,150\n")
    time.sleep(2) 

    arduino.write(b"R,150\n")
    time.sleep(1)
    
    print("Commanding: STOP")
    arduino.write(b"S,0\n")
    
except Exception as e:
    print(f"Error connecting to Arduino: {e}")