import sys, io, time
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

oldIn = 0
startTimer = time.time()

def start(RV):
    print('start')

def step(RV):
    global oldIn, startTimer
    print('step')
    newIn = RV.readFloat(1)
    if (newIn == 1 and oldIn == 0):
        startTimer = time.time()
        oldIn = 1
    elif (newIn == 0 and oldIn == 1):
        oldIn = 0

    if (time.time() - startTimer > 1 and newIn == 1):
        RV.writeFloat(1, 1)
    else:
        RV.writeFloat(1, 0)
        
        

def stop(RV):
    print('stop')

def cleanup(RV):
    print('cleanup')