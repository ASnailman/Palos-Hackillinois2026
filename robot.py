from drivers import board, leveler_motors, sonar
import time

class Robot:
    def __init__(self):
        self.leveler = leveler_motors.LevelerMotors()
        self.sonar = sonar.Sonar()
        self.pan_id = 2
        self.tilt_id = 1
        self.pan_center = 1500
        self.tilt_center = 2200
        
        self.reset()
        print("Robot On")

        
    def get_distance(self):
        td = 0
        for i in range(50):
            td += self.sonar.get_distance()/10
        td = td/50
        print("Back Sonar: " + str(td))
        if(td < 5):
            return 1000
        return td

    def get_distance2(self):
        return min(self.sonar.get_distance()/10.0, 50)

    def full_turn(self, speed):
        self.leveler.set_power(speed)
        
    def reset(self):
        self.leveler.reset()

    def beep(self, duration=0.2):
        board.setBuzzer(1)
        time.sleep(duration)
        board.setBuzzer(0)

    def beep_succession(self, count, duration):
        for i in range(count):
            board.setBuzzer(1)
            time.sleep(duration)
            board.setBuzzer(0)
            time.sleep(duration)

    def set_head(self, pan_pulse, tilt_pulse):
        board.setPWMServoPulse(self.pan_id, pan_pulse, 400)
        board.setPWMServoPulse(self.tilt_id, tilt_pulse, 400)
