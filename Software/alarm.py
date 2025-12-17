import sys, io
from playsound import playsound
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()
oldIn = 0
oldColor = '000000'

DATA_PATH = '/home/robotino/Desktop/Symposion/data/'
COLLISION_WARNING = '/home/robotino/Desktop/Symposion/audio/signs/collision_warning.mp3'

def start(RV):
    print('start')

def step(RV):
    global oldIn, oldColor
    print('step')
    newIn = RV.readFloat(1)
    if (newIn == 1 and oldIn == 0):
        oldIn = 1
        with open(DATA_PATH + 'rgbw.txt', 'r') as file:
            oldColor = file.read().strip()
        with open(DATA_PATH + 'rgbw.txt', 'w') as file:
            file.write("ff0000")
        playsound(COLLISION_WARNING)
    elif (newIn == 0 and oldIn == 1):
        oldIn = 0
        with open(DATA_PATH + 'rgbw.txt', 'w') as file:
            file.write(oldColor)

def stop(RV):
    print('stop')

def cleanup(RV):
    print('cleanup')