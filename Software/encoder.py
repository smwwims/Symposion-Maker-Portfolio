import sys, io
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()
import requests

SYMPOSION_PATH_URL = "http://127.0.0.1:5000/getMotor"
SYMPOSION_UPDATE_URL = "http://127.0.0.1:5000/updateHeight"

encoder_old = 0

def start(RV):
    print("start")

def step(RV):
    global encoder_old
    print("step")

    try:
        motor_response = requests.get(SYMPOSION_PATH_URL)
        if motor_response.status_code == 200:
            motor_enable = motor_response.json().get('motor_enable')
            encoder_reset = motor_response.json().get('encoder_reset')
            encoder_direction = motor_response.json().get('encoder_direction')
        else:
            print("Failed to retrieve search ID:", motor_response.text)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

    RV.writeFloat(1, motor_enable)
    RV.writeFloat(2, encoder_direction)
    RV.writeFloat(3, encoder_reset)

    encoder_new = RV.readFloat(1)
    if encoder_old != 0.0 and encoder_new == 0.0:
        try:
            params = {'encoder_value': encoder_old}
            r = requests.post(url=SYMPOSION_UPDATE_URL, params=params)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            return f"Error: {e}", 500
    encoder_old = encoder_new  
    

def stop(RV):
    print('stop')

def cleanup(RV):
    print('cleanup')