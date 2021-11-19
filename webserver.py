from flask import Flask, render_template, jsonify

from fhirclient import client
import fhirclient.models.patient as p
import fhirclient.models.observation as o

import requests
import json

app = Flask(__name__)

room_1 = [1223, 1431, 1516, 1970, 2177]
room_2 = [2395, 2592, 2871, 3021, 3422]

rooms = [room_1, room_2]

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

@app.route("/measurement/<patientId>")
def measurement(patientId):
    url = 'https://fhir.qezkenhd5wep.static-test-account.isccloud.io/Observation?code={}&patient=Patient/{}'.format('urn:my-system|urinary-output', patientId)
    headers = {'accept': 'application/fhir+json', 'x-api-key':'oiCise6rK32rBFcLqLjKs6Tw75Hb3ks82qZYbsb7'}
    content = requests.get(url, headers=headers)
    allMeasurements = content.json()

    measurementList = []
    
    for i in allMeasurements['entry']:
        measurementList.append(o.Observation(i['resource']).valueQuantity.value)

    return jsonify(
        measurements = measurementList
    )
    
    return content.content

if __name__ == "__main__":
    app.run()
