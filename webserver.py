from flask import Flask, render_template, jsonify, request, Response, make_response
from typing import NamedTuple

from fhirclient import client
import fhirclient.models.patient as p
import fhirclient.models.observation as o

import requests
import json

app = Flask(__name__)

room_1 = [1, 1431, 1516, 1970, 2177]
room_2 = [2395, 2592, 2871, 3021, 3294]

rooms = [0, 1]
patients = [room_1, room_2]

@app.route("/patient", methods=["POST"])
def patient():
    patientId = request.form['patientId']
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

@app.route("/measurement", methods=["POST"])
def getMeasurement():
    data = request.data
    print("Web server data: ", request.json)
    value = request.json['value']
    timestamp = request.json['time']
    patientId = request.json['patientId']

    jsonData = {"resourceType":"Observation","subject":
                {"reference":("Patient/"+str(patientId))},
                "effectiveDateTime":str(timestamp),
                "valueQuantity":{"value":value,"system":"http://unitsofmeasure.org","code":"g","unit":"g"},
                "status":"final",
                "code":{"coding":[{"system":"urn:my-system","code": "urinary-output"}]}
                }

    url = 'https://fhir.qezkenhd5wep.static-test-account.isccloud.io/Observation'
    headers = {'accept': 'application/fhir+json', 'Content-Type': 'application/fhir+json', 'x-api-key':'oiCise6rK32rBFcLqLjKs6Tw75Hb3ks82qZYbsb7'}

    print("json data: ", jsonData)
    x = requests.post(url, json=jsonData, headers=headers)
    print("response from measuremnte"+x.text)
    
    return {}

@app.route("/room/<roomId>")
def room(roomId):
    return jsonify(
        patients = rooms[int(roomId)]
    )

@app.route('/chart-data',methods=["POST","GET"])
def chart_data():
    patientId = request.form['patientId']
    url = 'https://fhir.qezkenhd5wep.static-test-account.isccloud.io/Observation?code={}&patient=Patient/{}'.format('urn:my-system|urinary-output', int(patientId))
    headers = {'accept': 'application/fhir+json', 'x-api-key':'oiCise6rK32rBFcLqLjKs6Tw75Hb3ks82qZYbsb7'}
    content = requests.get(url, headers=headers)
    allMeasurements = content.json()

    measurementList = []

    if(allMeasurements['total'] > 0):
        for i in allMeasurements['entry']:
            measurementList.append({'time':o.Observation(i['resource']).effectiveDateTime.isostring, 'value':o.Observation(i['resource']).valueQuantity.value})

    response = make_response(json.dumps(measurementList))
    response.content_type = 'application/json'
    return response

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
