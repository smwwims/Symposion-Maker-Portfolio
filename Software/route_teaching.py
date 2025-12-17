from flask import Flask, render_template, url_for, request
import requests
import json

ROBOTINOIP = "192.168.0.1"
ODOMETRY_URL = "http://" + ROBOTINOIP + "/data/odometry"

HTML = '''
{% extends 'base.html' %}

{% block head %}
    <title>Symposion Home</title>
{% endblock %}

{% block body %}
    <h1>Symposion Odometrie</h1>
    <p>Welcome to the symposion homepage.</p>
    <form method="PUT" action="Odometry"><input type="submit" value="SetOdometry" /></form>
    <form method="GET" action="Odometry"><input type="submit" value="GetOdometry" /></form>
{% endblock %}
'''

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/Odometry", methods=["PUT", "GET"])
def Odometry():
    if request.method == "PUT":
        try:
            # Construct the data payload for the PUT request
            data = [0, 0, 0, 0, 0, 0, 0]
            # Send the PUT request with JSON payload
            r = requests.put(url=ODOMETRY_URL, json=data)
            r.raise_for_status()  # Raise an error if the request was not successful
            return "Success: Odometry set to 0"
        except requests.exceptions.RequestException as e:
            return f"Error: {e}", 500
    elif request.method == "GET":
        r = requests.get(url=ODOMETRY_URL)
        if r.status_code == requests.codes.ok:
            data = r.json()
            return str(data)
        else:
            raise RuntimeError(f"Error: GET from {ODOMETRY_URL} failed")
        
if __name__ == '__main__':
    app.run(debug=True)