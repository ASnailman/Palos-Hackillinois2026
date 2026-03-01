import time
from smbus2 import SMBus, i2c_msg

class Sonar:
    def __init__(self):
        self.i2c_addr = 0x77
        self.i2c = 1

    def setPixelColor(self, index, r, g, b):
        """Index 0 or 1. RGB 0-255"""
        if index not in [0, 1]: return
        start_reg = 3 if index == 0 else 6
        rgb = (r << 16) | (g << 8) | b
        
        try:
            with SMBus(self.i2c) as bus:
                bus.write_byte_data(self.i2c_addr, start_reg, 0xFF & (rgb >> 16))
                bus.write_byte_data(self.i2c_addr, start_reg+1, 0xFF & (rgb >> 8))
                bus.write_byte_data(self.i2c_addr, start_reg+2, 0xFF & rgb)
        except Exception as e:
            print(f"I2C LED Error: {e}")

    # Renamed to get_distance to match your robot.py!
    def get_distance(self):
        """Returns distance in mm"""
        dist = 99999
        try:
            with SMBus(self.i2c) as bus:
                msg = i2c_msg.write(self.i2c_addr, [0,])
                bus.i2c_rdwr(msg)
                
                read = i2c_msg.read(self.i2c_addr, 2)
                bus.i2c_rdwr(read)
                
                dist = int.from_bytes(bytes(list(read)), byteorder='little', signed=False)
                if dist > 5000: dist = 5000
                
        except Exception as e:
            # THIS IS THE MAGIC LINE! It will print exactly why it's failing.
            print(f"I2C Sonar Error: {e}") 
            
        return dist