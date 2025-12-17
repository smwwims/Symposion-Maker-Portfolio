from flask import Flask, render_template, url_for, request, redirect, url_for, jsonify, send_from_directory
import requests
import json
import csv  # Store paths in a csv file
import time
import os
from playsound import playsound


# REST API
ROBOTINOIP = "192.168.0.1"
ODOMETRY_URL = "http://" + ROBOTINOIP + "/data/odometry"
DISTATUS_URL = "http://" + ROBOTINOIP + "/data/digitalinputarray"
DQSTATUS_URL = "http://" + ROBOTINOIP + "/data/digitaloutputstatus"
DQSET_URL = "http://" + ROBOTINOIP + "/data/digitaloutputarray"

# Directories
AUDIO_FOLDER = "/home/robotino/Desktop/Symposion/audio/music/"
IMAGE_FOLDER = "C:/Users/simon/Desktop/Mechatronik/Werkstätte Mechatronik/8. Klasse/Gesellenprojekt/Software/Symposion/images"
ROUTES_FILE = '/home/robotino/Desktop/Symposion/data/routes.csv'
DATA_PATH = '/home/robotino/Desktop/Symposion/data/'

# Predefined functions
# Height Adjustment
def readHeight():
    try:
        with open('data/height.txt', 'r') as file:
            number = int(file.read().strip())
            return number
    except FileNotFoundError:
        print(f"Error: File '{'data/height.txt'}' not found.")
        return None
    except ValueError:
        print(f"Error: File '{'data/height.txt'}' does not contain a valid integer.")
        return None
    
def updateHeight(new_height):
    try:
        with open('data/height.txt', 'w') as file:
            file.write(str(new_height))  # Write new height to the file
        return True
    except Exception as e:
        print(f"Error: Failed to update height in file '{'data/height.txt'}': {e}")
        return False


# Global Variables
# Teaching
path = None
poses = 0
homeX = None
homeY = None
homeRot = None

# Route Following
search_id = None

# Height Adjustment
motor_enable = 0
encoder_reset = 1
encoder_direction = 0


app = Flask(__name__)


# Page Links
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pageTeaching')
def teaching():
    global poses
    return render_template('teaching.html', poscounter = str(poses))

@app.route('/pageDrive')
def drive():
    with open(ROUTES_FILE, mode='r') as file:
        csv_reader = csv.reader(file)
        routes = [row[0] for row in csv_reader]
    return render_template('drive.html', routes=routes, search_id=search_id)

@app.route('/pageHeight')
def height():
    return render_template('height.html', heightDisplay = readHeight())

@app.route('/pageLight')
def light():
    return render_template('light.html')

@app.route('/pagePresentation')
def presentation():
    songs = os.listdir(AUDIO_FOLDER)
    images = [image for image in os.listdir(IMAGE_FOLDER) if image.endswith(('jpg', 'jpeg', 'png', 'gif'))]
    songs.sort()
    return render_template('presentation.html', songs=songs, images=images)

@app.route('/pageDebug')
def debug():
    url_params = request.args
    if 'setDQ' in url_params:
        out = url_params.get('setDQ')
        setDQ(out)
    return render_template('debug.html')


# Teaching
@app.route("/teaching/deletePoint", methods=["POST"])
def delete_point():
    global path, poses
    if path:
        # Split the path into individual points
        points = path.split(") (")
        if len(points) > 1:
            # Remove the last point
            points.pop()
            # Join the remaining points
            path = ") (".join(points)
            # Ensure the format remains correct
            poses -= 1
            # Ensure path has the right format
            if not path.startswith("("):
                path = "(" + path
            if not path.endswith(")"):
                path += ")"
        else:
            # If there's only one point, clear the path
            poses = 0
            path = ""
    return render_template('teaching.html', poscounter = str(poses))
       
@app.route("/teaching/savePoint", methods=["POST"])
def savePoint():
    global path, poses, homeX, homeY, homeRot
    r = requests.get(url=ODOMETRY_URL)
    if r.status_code == requests.codes.ok:
        data = r.json()
        x, y, rot = data[0], data[1], data[2]
        # Zero Offset
        if not homeX and not homeY and not homeRot:
            homeX, homeY, homeRot = x, y, rot
        x = (x - homeX) * 1000 # RobotinoView uses 1000 times the value of odometry
        y = (y - homeY) * 1000 # RobotinoView uses 1000 times the value of odometry
        rot = (rot - homeRot) * (180/3.14159265) # RobotinoView uses degrees, Odometry radians
        new_point = f"(({x} {y}) {rot})"
        poses += 1
        if path:
            path += f" {new_point}"
        else:
            path = new_point
        return render_template('teaching.html', poscounter = str(poses))
    else:
        raise RuntimeError(f"Error: GET from {ODOMETRY_URL} failed")
    
@app.route("/teaching/savePath/submitPath", methods=["POST"])
def submit_path():
    global path, poses, homeX, homeY, homeRot
    route_name = request.form['route_name']
    if route_name and path:
        # Add parentheses around the entire path string
        formatted_path = f"({path})"
        # Save to CSV file
        with open('data/routes.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([route_name, formatted_path])
        # Reset global variables
        poses = 0
        path = ""
        homeX = None
        homeY = None
        homeRot = None
        return render_template('index.html')
    else:
        return "Error: Route name or path is missing"

@app.route("/teaching/savePath", methods=["POST"])
def submitTeaching():
    return render_template('teaching-submit.html')
    
@app.route("/teaching/cancel", methods=["GET"])
def cancelTeaching():
    return render_template('teaching-cancel.html')

@app.route("/teaching/close", methods=["GET"])
def closeTeaching():
    global path, poses
    path = ""
    poses = 0
    return render_template('index.html')


# Route Following
@app.route("/pageDrive/start", methods=["POST"])
def startDrive():
    global search_id
    search_id = request.form['route']
    return redirect(url_for('drive'))


# Height Adjustment
@app.route("/pageHeight/up", methods=["POST"])
def heightUp():
    global motor_enable, encoder_direction, encoder_reset
    startHeight = readHeight()
    if readHeight() < 110:
        motor_enable = 1
        encoder_direction = 1
        encoder_reset = 0
        time.sleep(3)
        motor_enable = 0
        encoder_direction = 0
        encoder_reset = 1
    time.sleep(0.5)
    endHeight = readHeight()
    if startHeight == endHeight:
        return render_template('error.html', reference="101", cause="Motor wird angesteuert aber Encoder-Wert verändert sich nicht", fix="Überprüfen Sie, ob sich der Motor dennoch dreht. Dreht er sich, liegt ein Problem beim Encoder vor, falls nicht handelt es sich um ein Motorproblem. Prüfen Sie zuerst die Versorgungskabel und anschließend den Sensor/Aktor selbst.")
    return render_template('height.html', heightDisplay = readHeight())

@app.route("/pageHeight/down", methods=["POST"])
def heightDown():
    global motor_enable, encoder_direction, encoder_reset
    di = requests.get(url=DISTATUS_URL)
    startHeight = readHeight()
    if readHeight() > 84 and di.json()[1] == 0 and di.status_code == requests.codes.ok:
        motor_enable = -1
        encoder_direction = -1

        encoder_reset = 0
        time.sleep(3)
        motor_enable = 0
        encoder_direction = 0
        encoder_reset = 1
    time.sleep(0.5)
    endHeight = readHeight()
    if startHeight == endHeight:
        return render_template('error.html', reference="101", cause="Motor wird angesteuert aber Encoder-Wert verändert sich nicht", fix="Überprüfen Sie, ob sich der Motor dennoch dreht. Dreht er sich, liegt ein Problem beim Encoder vor, falls nicht handelt es sich um ein Motorproblem. Prüfen Sie zuerst die Versorgungskabel und anschließend den Sensor/Aktor selbst.")
    return render_template('height.html', heightDisplay = readHeight())

@app.route("/pageHeight/reference", methods=["POST"])
def heightReference():
    global motor_enable
    di = requests.get(url=DISTATUS_URL)
    startTime = time.time()
    while di.json()[1] == 0 and di.status_code == requests.codes.ok:
        motor_enable = -1
        di = requests.get(url=DISTATUS_URL)
        time.sleep(0.5)
        if time.time() - startTime > 60:
            motor_enable = 0
            return render_template('error.html', reference="100", cause="Endlagenschalter wurde nicht in der definierten Zeit erreicht", fix="Überprüfen Sie, ob die Plattform über die Limits verfahren wurde. Falls die Plattform ein Limit überfährt, fällt es von der Spindel. In diesem Fall setzen Sie die Mitnehmerplattform wieder auf die Spindel auf.")
    motor_enable = 0
    updateHeight(82)
    return render_template('height.html', heightDisplay = readHeight())


# Light
@app.route("/pageLight/changeLight", methods=["POST"])
def changeLight():
    hex_color = request.form.get('color')
    hex_color = hex_color.lstrip('#')
    with open(DATA_PATH + "rgbw.txt", 'w') as file:
        file.write(hex_color)
    return render_template('light.html')

@app.route("/pageLight/rainbow", methods=["POST"])
def rainbow():
    with open(DATA_PATH + "rgbw.txt", 'w') as file:
        file.write('rainbow')
    return render_template('light.html')
    

# Presentation
@app.route('/play', methods=['POST'])
def play():
    song = request.json.get('song')
    # Return the URL to the selected song
    return jsonify({'url': f'/audio/{song}'})

@app.route('/audio/<filename>')
def audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route('/playlist', methods=['GET'])
def playlist():
    # List all audio files in the audio folder
    songs = os.listdir(AUDIO_FOLDER)
    songs.sort()  # Sort the songs alphabetically or any preferred order
    return jsonify({'songs': songs})


@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)


# Debug
@app.route("/updateDIO", methods=['GET'])
def updateClasses():
    try:
        di = requests.get(url=DISTATUS_URL)
        dq = requests.get(url=DQSTATUS_URL)
        if di.status_code == requests.codes.ok and dq.status_code == requests.codes.ok:
            di_data = di.json()
            dq_data = dq.json()
            dio_data = di_data + dq_data
            return json.dumps(dio_data)
    except requests.exceptions.RequestException as e:
        return f"Error: {e}", 500
    
@app.route("/setDQ", methods=['POST'])
def setDQ():
    try:
        url_params = request.args
        out = int(url_params.get('DQ')) - 1
        dqpackage = requests.get(url=DQSTATUS_URL)
        if dqpackage.status_code == requests.codes.ok:
            dqarray = dqpackage.json()
            dqarray[out] = 1 - dqarray[out]
            r = requests.put(url=DQSET_URL, json=dqarray)
            r.raise_for_status()
            print("DQ{} set to: {}".format(out, dqarray[out]))
            return render_template('debug.html')
    except requests.exceptions.RequestException as e:
        return f"Error: {e}", 500  
    
# Software Requests
@app.route("/getPath", methods=['GET'])
def getPath():
    global search_id
    return json.dumps({'search_id': search_id})

@app.route("/getMotor", methods=['GET'])
def getMotor():
    return json.dumps({'motor_enable': motor_enable, 'encoder_reset': encoder_reset, 'encoder_direction': encoder_direction})

@app.route("/updateHeight", methods=['POST'])
def calculateHeight():
    try:
        url_params = request.args
        encoder_value = float(url_params.get('encoder_value'))
        encoder_resolution_up = (10 / 3) * 98 # spindle pitch 3 mm = 0.3 cm; encoder has 98 ticks per turn
        encoder_resolution_down = encoder_resolution_up * 2 # encoder counts more ticks if motor drives down
        if (encoder_value < 0):
            cmDifference = encoder_value / encoder_resolution_down
        else:
            cmDifference = encoder_value / encoder_resolution_up
        currentHeight = readHeight()
        if currentHeight is None:
            return "Error: Failed to read current height", 500
        updateHeight(int(currentHeight + cmDifference))
        return "Height updated successfully"
    except requests.exceptions.RequestException as e:
        return f"Error: {e}", 500

@app.route("/collision", methods=['POST'])
def collision():
    try:
        with open('/home/robotino/Desktop/Symposion/data/rgbw.txt', 'r') as file:
            oldColor = file.read().strip()
        with open('/home/robotino/Desktop/Symposion/data/rgbw.txt', 'w') as file:
            file.write("ff0000")
        playsound('/home/robotino/Desktop/Symposion/audio/signs/collision_warning.mp3')
        with open('/home/robotino/Desktop/Symposion/data/rgbw.txt', 'w') as file:
            file.write(oldColor) 
        return "Height updated successfully"
    except requests.exceptions.RequestException as e:
        return f"Error: {e}", 500    

if __name__ == '__main__':
    app.run(debug=True)