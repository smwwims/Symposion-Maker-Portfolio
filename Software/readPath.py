import sys, io
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()
import csv
import requests

SYMPOSION_PATH_URL = "http://127.0.0.1:5000/getPath"
csv_filename = "/home/robotino/Desktop/Symposion/data/routes.csv"
newStart, oldStart = 0, 0
path = ""

def start(RV):
    print("start")

def step(RV):
    global newStart, oldStart, path
    print("step")

    try:
        search_id_response = requests.get(SYMPOSION_PATH_URL)
        if search_id_response.status_code == 200:
            search_id = search_id_response.json().get('search_id')
            print("Search ID:", search_id)
        else:
            print("Failed to retrieve search ID:", search_id_response.text)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

    try:
        with open(csv_filename, mode='r') as file:
            csv_reader = csv.reader(file)
            print("File opened")
            for row in csv_reader:
                print(row)
                if row[0] == search_id:
                    print("Found ID")
                    path = row[1]
                    RV.writeString(1, row[1])
    except FileNotFoundError:
        print("File not found")
    except Exception as e:
        print(e)
    finally:
        file.close()

    if path:
        newStart = 1
    else:
        newStart = 0

    if (newStart == 1 and oldStart == 0):
        RV.writeFloat(2, 1)
    else:
        RV.writeFloat(2, 0)
    oldStart = newStart

def stop(RV):
    print('stop')

def cleanup(RV):
    print('cleanup')