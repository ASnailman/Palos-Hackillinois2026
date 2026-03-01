import time
import RPi.GPIO as GPIO
from smbus2 import SMBus, i2c_msg
from rpi_ws281x import PixelStrip, Color as PixelColor

# Constants
SERVO_ADDR_CMD = 40
MOTOR_ADDR = 31
SERVO_ADDR = 21
I2C_ADDR = 0x7A
I2C_BUS = 1

# RGB Strip Config
RGB_COUNT = 2
RGB_PIN = 12
RGB_FREQ_HZ = 800000
RGB_DMA = 10
RGB_BRIGHTNESS = 120
RGB_CHANNEL = 0
RGB_INVERT = False

# Global State
_servo_pulse = [0] * 6
_motor_speed = [0] * 4

# Initialize GPIO & RGB
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(31, GPIO.OUT) # Buzzer

try:
    RGB = PixelStrip(RGB_COUNT, RGB_PIN, RGB_FREQ_HZ, RGB_DMA, RGB_INVERT, RGB_BRIGHTNESS, RGB_CHANNEL)
    RGB.begin()
    for i in range(RGB.numPixels()):
        RGB.setPixelColor(i, PixelColor(0,0,0))
    RGB.show()
except Exception as e:
    print(f"Warning: RGB Strip init failed: {e}")

def setMotor(index, speed):
    """Control Motor (1-4) with speed (-100 to 100)"""
    if index < 1 or index > 4:
        raise AttributeError(f"Invalid motor num: {index}")
    
    # Fix polarity based on Hiwonder SDK
    if index == 2 or index == 4:
        speed = speed
    else:
        speed = -speed
        
    speed = max(-100, min(100, speed))
    reg = MOTOR_ADDR + index - 1
    
    with SMBus(I2C_BUS) as bus:
        try:
            msg = i2c_msg.write(I2C_ADDR, [reg, speed.to_bytes(1, 'little', signed=True)[0]])
            bus.i2c_rdwr(msg)
            _motor_speed[index-1] = speed
        except Exception as e:
            print(f"I2C Motor Error: {e}")

def setPWMServoPulse(servo_id, pulse=1500, use_time=1000):
    """Control PWM Servo (1-6)"""
    if servo_id < 1 or servo_id > 6:
        raise AttributeError(f"Invalid Servo ID: {servo_id}")
        
    pulse = max(500, min(2500, pulse))
    use_time = max(0, min(30000, use_time))
    
    buf = [SERVO_ADDR_CMD, 1] + list(use_time.to_bytes(2, 'little')) + [servo_id,] + list(pulse.to_bytes(2, 'little'))
    
    with SMBus(I2C_BUS) as bus:
        try:
            msg = i2c_msg.write(I2C_ADDR, buf)
            bus.i2c_rdwr(msg)
            _servo_pulse[servo_id-1] = pulse
        except Exception as e:
            print(f"I2C Servo Error: {e}")

def setBuzzer(state):
    """0 = Off, 1 = On"""
    GPIO.output(31, state)

def getBattery():
    try:
        with SMBus(I2C_BUS) as bus:
            msg = i2c_msg.write(I2C_ADDR, [0,])
            bus.i2c_rdwr(msg)
            read = i2c_msg.read(I2C_ADDR, 2)
            bus.i2c_rdwr(read)
            val = int.from_bytes(bytes(list(read)), 'little')
            return val / 1000.0
    except:
        return 0.0