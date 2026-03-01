from . import board

class Servo:
    """
    Interface for a single PWM Servo on the Hiwonder expansion board.
    """
    def __init__(self, servo_id):
        """
        :param servo_id: The ID of the servo (1-6)
        """
        self.servo_id = servo_id
        self.current_pulse = 1500 # Default middle position

    def set_pulse(self, pulse, use_time=500):
        """
        Sets the servo pulse width.
        :param pulse: Pulse width in microseconds (500-2500)
        :param use_time: Time in milliseconds to reach the position
        """
        pulse = max(500, min(2500, pulse))
        board.setPWMServoPulse(self.servo_id, pulse, use_time)
        self.current_pulse = pulse

    def set_angle(self, angle, use_time=500):
        """
        Converts an angle (0-180) to a pulse (500-2500).
        :param angle: Angle in degrees (0-180)
        """
        # Linear mapping: 0 deg -> 500 pulse, 180 deg -> 2500 pulse
        pulse = int(500 + (angle / 180.0) * 2000)
        self.set_pulse(pulse, use_time)