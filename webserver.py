from flask import Flask, render_template, jsonify, request, Response
from typing import NamedTuple

from fhirclient import client
import fhirclient.models.patient as p
import fhirclient.models.observation as o

import requests
import json

import random
import time
from datetime import datetime

app = Flask(__name__)

room_1 = [1223, 1431, 1516, 1970, 2177]
room_2 = [2395, 2592, 2871, 3021, 3422]

rooms = [0, 1]
patients = [room_1, room_2]

random.seed() 

@app.route("/patient/<patientId>")
def patient(patientId):
    url = 'https://fhir.qezkenhd5wep.static-test-account.isccloud.io/Patient/{}'.format(patientId)
    headers = {'accept': 'application/fhir+json', 'x-api-key':'oiCise6rK32rBFcLqLjKs6Tw75Hb3ks82qZYbsb7'}
    content = requests.get(url, headers=headers)
    patient = p.Patient(content.json())
    patientName = str(patient.name[0].family) + " " + str(patient.name[0].given[0])
    return jsonify(
        name= patientName,
        birthdate = patient.birthDate.isostring,
        gender = patient.gender,
        patientId = patientId
    )

@app.route("/room/<roomId>")
def room(roomId):
    return jsonify(
        patients = rooms[int(roomId)]
    )

@app.route('/chart-data')
def chart_data():
    def generate_random_data(patientId):
        while True:
            url = 'https://fhir.qezkenhd5wep.static-test-account.isccloud.io/Observation?code={}&patient=Patient/{}'.format('urn:my-system|urinary-output', patientId)
            headers = {'accept': 'application/fhir+json', 'x-api-key':'oiCise6rK32rBFcLqLjKs6Tw75Hb3ks82qZYbsb7'}
            content = requests.get(url, headers=headers)
            allMeasurements = content.json()

            measurementList = []
    
            for i in allMeasurements['entry']:
                measurementList.append({'time':o.Observation(i['resource']).effectiveDateTime.isostring, 'value':o.Observation(i['resource']).valueQuantity.value})

            json_data = json.dumps(measurementList)
            yield f"data:{json_data}\n\n"
            time.sleep(3)

    return Response(generate_random_data(1), mimetype='text/event-stream')

@app.route('/')
def main():
    return render_template('index.html', rooms=rooms)
 
@app.route("/patientsInRoom",methods=["POST","GET"])
def patientsInRoom():  
    if request.method == 'POST':
        roomId = request.form['roomId']
        patientsInRoom = patients[int(roomId)]
        output = []
        for patient in patientsInRoom:
            pObj = {
                'id': patient
                }
            output.append(pObj)
    return jsonify(output)

@app.route('/graph')
def index():
    return render_template('graph.html')

if __name__ == "__main__":
    app.run(threaded = True)
