from robot import Robot
import time

bot = Robot()
print(bot.get_distance())
time.sleep(1)
bot.full_turn(100)
time.sleep(3)
bot.reset()