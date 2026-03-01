import time
from . import board

class LevelerMotors:
    def __init__(self):
        # No geometry or wheel diameter needed anymore!
        pass

    def set_power(self, speed):
        """
        Spins all 4 motors to power the leveling mechanism.
        speed: Integer representing motor power (e.g., -100 to 100)
        """
        
        speed = int(speed)
        
        board.setMotor(1, speed)
        time.sleep(0.005) # 5ms delay to prevent I2C packet dropping
        board.setMotor(2, speed)
        time.sleep(0.005)
        board.setMotor(3, speed)
        time.sleep(0.005)
        board.setMotor(4, speed)

    def reset(self):
        """
        Safely halts all 4 motors.
        """
        board.setMotor(1, 0)
        time.sleep(0.005)
        board.setMotor(2, 0)
        time.sleep(0.005)
        board.setMotor(3, 0)
        time.sleep(0.005)
        board.setMotor(4, 0)