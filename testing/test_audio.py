# import subprocess
# import os

# def robot_speak(text):
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     model = os.path.join(base_dir, "..", "audio_models", "en_US-bryce-medium.onnx")
#     command = f'echo "{text}" | piper --model {model} --output_raw | aplay -r 22050 -f S16_LE -t raw'
#     subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# robot_speak("you should kill yourself now.")

from gtts import gTTS
import os

tts = gTTS("dih")
tts.save("speech.mp3")
os.system("mpg123 speech.mp3")
print("speech said")