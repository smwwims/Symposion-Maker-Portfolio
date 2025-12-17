import serial
import time

rainbowState = 0  # Current state of the rainbow effect
pwmRed, pwmGreen, pwmBlue = 0, 0, 0  # PWM values for the RGB LEDs

def write_to_file(filename, data):
    with open(filename, 'w') as file:
        file.write(str(data))

def read_rgbw_file(filename):
    try:
        with open(filename, 'r') as file:
            data = file.readline().strip()
            if data:
                return data
    except FileNotFoundError:
        pass
    return None

def get_hex_color(r, g, b):
    return "{:02x}{:02x}{:02x}".format(r, g, b)

def Rainbow():
    global pwmRed, pwmGreen, pwmBlue, rainbowState

    if rainbowState == 0:
        pwmRed = 255
        pwmGreen = 0
        pwmBlue = 0
        rainbowState = 1

    elif rainbowState == 1:
        pwmRed -= 5
        pwmGreen += 5
        if pwmRed <= 0 or pwmGreen >= 255:
            pwmRed = 0
            pwmGreen = 255
            rainbowState = 2

    elif rainbowState == 2:
        pwmGreen -= 5
        pwmBlue += 5
        if pwmGreen <= 0 or pwmBlue >= 255:
            pwmGreen = 0
            pwmBlue = 255
            rainbowState = 3

    elif rainbowState == 3:
        pwmBlue -= 5
        pwmRed += 5
        if pwmBlue <= 0 or pwmRed >= 255:
            pwmBlue = 0
            pwmRed = 255
            rainbowState = 0

    return get_hex_color(pwmRed, pwmGreen, pwmBlue)

#arduino_port = 'COM7'      # Windows Host
arduino_port = '/dev/ttyUSB0' # Robotino Host
RGBW_PATH = '/home/robotino/Desktop/Symposion/data/rgbw.txt'
IR_PATH = '/home/robotino/Desktop/Symposion/data/ir.txt'
TOF_LEFT_PATH = '/home/robotino/Desktop/Symposion/data/tof_left.txt'
TOF_MIDDLE_PATH = '/home/robotino/Desktop/Symposion/data/tof_middle.txt'
TOF_RIGHT_PATH = '/home/robotino/Desktop/Symposion/data/tof_right.txt'
baud_rate = 9600
connection_established = False

while not connection_established:
    try:
        k3 = serial.Serial(port=arduino_port, baudrate=baud_rate, timeout=1)
        connection_established = True
        print("Connection established")
    except serial.SerialException as e:
        print(f"Error opening {arduino_port}: {e}")
        print("Retrying in 3 seconds...")
        time.sleep(3)

previous_time = time.time()

while True:
    current_time = time.time()
    try:
        # Send RGBW values every 500 ms
        if current_time - previous_time >= 0.5:
            print("Sending RGBW values")
            previous_time = current_time
            rgbw_str = read_rgbw_file(RGBW_PATH)
            if rgbw_str:
                print(f"Sending RGBW values: {rgbw_str}")
                if rgbw_str.lower() == 'rainbow':
                    rainbow_color = Rainbow()
                    rainbow_str = str(int(rainbow_color, 16))
                    k3.write(("#" + rainbow_str).encode())
                    print(f"Sent rainbow color: {rainbow_color}")
                else:
                    rgbw_str = str(int(rgbw_str, 16))
                    k3.write(("#" + rgbw_str).encode())
                    print(f"Sent RGBW values: {rgbw_str}")

        # Read incoming sensor data
        while k3.in_waiting > 0:
            sensor_data = k3.readline().decode('utf-8').strip()
            if sensor_data:
                irSignal, distanceLeft, distanceMiddle, distanceRight = map(int, sensor_data.split(','))
                write_to_file(IR_PATH, irSignal)
                write_to_file(TOF_LEFT_PATH, distanceLeft)
                write_to_file(TOF_MIDDLE_PATH, distanceMiddle)
                write_to_file(TOF_RIGHT_PATH, distanceRight)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        print("Attempting to reconnect...")
        k3.close()
        connection_established = False
        while not connection_established:
            try:
                k3 = serial.Serial(port=arduino_port, baudrate=baud_rate, timeout=1)
                connection_established = True
                print("Reconnected successfully")
            except serial.SerialException as e:
                print(f"Error opening {arduino_port}: {e}")
                print("Retrying in 3 seconds...")
                time.sleep(3)