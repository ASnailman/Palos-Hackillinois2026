from drivers import board, leveler_motors, sonar
import time

class Robot:
    def __init__(self):
        self.leveler = leveler_motors.LevelerMotors()
        self.sonar = sonar.Sonar()
        
    def get_distance(self):
        return self.sonar.get_distance()

    def full_turn(self, speed):
        self.leveler.set_power(speed)
        
    def reset(self):
        self.leveler.reset()