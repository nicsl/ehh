from flask import Flask, render_template, jsonify, request, Response, make_response
from dateutil import parser 

from fhirclient import client
import fhirclient.models.patient as p
import fhirclient.models.observation as o

import requests
import json

app = Flask(__name__)

# Testing rooms
# For future: Each device should be configured via Bluetooth
# Configuration should provide PatientId on that device and room number
room_1 = [1, 1431, 1516, 1970, 2177]
room_2 = [2395, 2592, 2871, 3021, 3294]

rooms = [0, 1]
patients = [room_1, room_2]

# patient
# Retrieves via GET the patient data from FHIR, based on ID
# Return: Simplified JSON data with name, birthdate, gender and patient database ID
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

# getMeasurement
# Receives simplified measurement data from a sensor, makes a POST to FHIR Observation
# Return: Nothing
@app.route("/measurement", methods=["POST"])
def getMeasurement():
    data = request.data
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

    requests.post(url, json=jsonData, headers=headers)
    return {}

# retrieveMeasurements
# Retrieve all the urinary output measurements from a patient
# Return: JSON data with all the measurements (Timestamp and Value)
@app.route('/retrieveMeasurements',methods=["POST","GET"])
def retrieveMeasurements():
    patientId = request.form['patientId']
    url = 'https://fhir.qezkenhd5wep.static-test-account.isccloud.io/Observation?code={}&patient=Patient/{}'.format('urn:my-system|urinary-output', int(patientId))
    headers = {'accept': 'application/fhir+json', 'x-api-key':'oiCise6rK32rBFcLqLjKs6Tw75Hb3ks82qZYbsb7'}
    content = requests.get(url, headers=headers)
    allMeasurements = content.json()

    measurementList = []

    if(allMeasurements['total'] > 0):
        for i in allMeasurements['entry']:
            datetime = parser.parse(o.Observation(i['resource']).effectiveDateTime.isostring) 
            measurementList.append({'time': str(datetime.time()), 'value':o.Observation(i['resource']).valueQuantity.value})

    response = make_response(json.dumps(measurementList))
    response.content_type = 'application/json'
    return response

# patientsInRoom
# Gets the IDs of all the patients in a room
# Return: JSON data with all the patients in that room
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

@app.route('/')
def main():
    return render_template('index.html', rooms=rooms)

if __name__ == "__main__":
    app.run(host='172.16.88.241')
