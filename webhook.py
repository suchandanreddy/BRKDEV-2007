from flask import Flask, request, jsonify
from flask_basicauth import BasicAuth
from ciscosparkapi import CiscoSparkAPI, SparkApiError
import json
import os
import time
import datetime
import pytz

webhook_username = os.environ.get("webhook_username")
webhook_password = os.environ.get("webhook_password")
bearer_token = os.environ.get("bearer_token")
room_id = os.environ.get("room_id")

if bearer_token is None or room_id is None or webhook_username is None or webhook_password is None:
    print("\nWebhook Server Login details, Webex Teams Authorization and roomId details must be set via environm
ent variables using below commands on macOS or Ubuntu workstation")
    print("export webhook_username=<webhook username>")
    print("export webhook_password=<webhook password>")
    print("export bearer_token=<authorization bearer token>")
    print("export room_id=<webex teams room-id>")
    print("\nWebhook Server Login details, Webex Teams Authorization and roomId details must be set via environm
ent variables using below commands on Windows workstation")
    print("set webhook_username=<webhook username>")
    print("set webhook_password=<webhook password>")
    print("set bearer_token=<authorization bearer token>")
    print("set room_id=<webex teams room-id>")
    exit()

app = Flask(__name__)
basic_auth = BasicAuth(app)

app.config['BASIC_AUTH_USERNAME'] = webhook_username
app.config['BASIC_AUTH_PASSWORD'] = webhook_password

@app.route('/',methods=['POST'])
@basic_auth.required
def alarms():
   try:
      PDT = pytz.timezone('America/Los_Angeles')
      data = json.loads(request.data)
      print(data)
      message =  '''Team, Alarm event : **''' + data['rule_name_display'] + '''** is recieved from vManage and h
ere are the complete details <br><br>'''

      temp_time = datetime.datetime.utcfromtimestamp(data['entry_time']/1000.)
      temp_time = pytz.UTC.localize(temp_time)
      message = message + '**Alarm Date & Time:** ' + temp_time.astimezone(PDT).strftime('%c') + ' PDT'
      temp = data['values_short_display']
      for item in temp:
          for key, value in item.items():
              message = message + '<br> **' + key + ':** ' + value

      message = message + '<br> **' + 'Details:' + '** ' + "https://sdwanlab.cisco.com/#/app/monitor/alarms/deta
ils/" + data['uuid']

      api = CiscoSparkAPI(access_token=bearer_token)
      res=api.messages.create(roomId=room_id, markdown=message)
      print(res)


   except Exception as exc:
      print(exc)
      return jsonify(str(exc)), 500

   return jsonify("Message sent to Webex Teams"), 200

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5001, debug=True)
