from flask import Flask, request, jsonify
import json, config

app = Flask(__name__)

def connect_call():
    json_body = {
        "callflow": [
             {
                "action": "makeCall",
                "params": {
                    "source": config.SOURCE_PN,
                    "destination": config.DESTINATION_PN
                }
            }
        ]
    }

    return jsonify(json_body)

def hangup():
    json_body = {
        "callflow": [
        {
          "action": "hangup"
        }
        ]
    }

    return jsonify(json_body)

def send_ivr_response(promptMessage):
    # Define the JSON body
    json_body = {
        "callflow": [
            {
            "action": "sayAndCapture",
            "params": {
                    "promptMessage": promptMessage,
                    "voiceProfile": "en-US-BenjaminRUS",
                    "repetition": 1,
                    "speed": 1,
                    "minDigits": 1,
                    "maxDigits": 1,
                    "digitTimeout": 10000,
                    "overallTimeout": 10000,
                    "completeOnHash": False,
                    "noOfTries": 2,
                    "successMessage": None,
                    "failureMessage": "Invalid input, please try again"
              }
            }
        ]
    }   

    return jsonify(json_body)
    
@app.route('/vss_webhook', methods=['GET', 'POST'])
def vss_webhook():
    request_data = request.get_data(as_text=True)

    try:
        json_data=json.loads(request_data)
        pretty_request_data=json.dumps(json_data,indent=2)
    except json.JSONDecodeError:
        pretty_request_data=request_data
    
    # Here you can choose to log the information from a call in your system, in this example we only print the information.
    if json_data["eventType"] == "SESSION_SUMMARY":
        print(pretty_request_data)
    else:
        print("Not a VSS Webhook")

    return {}

@app.route('/vca_webhook', methods=['GET', 'POST'])
def vca_webhook():
    # Parse Webhook Data
    request_data = request.get_data(as_text=True)
    try:
        webhook_data=json.loads(request_data)
        pretty_request_data=json.dumps(webhook_data,indent=2)
    except json.JSONDecodeError:
        pretty_request_data=request_data
    
    # Print out webhook body
    print(pretty_request_data)

    # Handle VCA Webhook
    if webhook_data["eventType"] == "CALL_ACTION":
        if webhook_data["payload"]["dtmf"] == "1":
            return hangup()
        elif webhook_data["payload"]["dtmf"] == "2":
            return connect_call()
        else:
            return send_ivr_response("Sorry, we did not understand your response. If you have resolved your issue already, press one. Or press two to speak to an agent.")
            
    else: # Not a VCA Webhook, print message.
        print("Not a VCA Webhook")
        return {}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)