import sys
import os

# Adds the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from robot import Robot
import time

bot = Robot()
bot.set_head(2000,500)