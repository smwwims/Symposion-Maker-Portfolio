#!/bin/bash

cd /home/robotino/Desktop/Symposion
nohup python3 app.py &
nohup python3 k3_communication.py &
nohup firefox http://127.0.0.1:5000 &