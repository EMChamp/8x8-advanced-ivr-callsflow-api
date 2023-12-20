from flask import Flask, request, jsonify
import json, config

app = Flask(__name__)

def connect_call(clientActionId):
    json_body = {
        "clientActionId": clientActionId,
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

def say_message_and_hangup(text):
    json_body = {
        "callflow": [
        {
            "action": "say",
            "params": {
                    "text": text,
                    "voiceProfile": "en-US-BenjaminRUS",
                    "speed": 1
                }
        },
        {
          "action": "hangup"
        }
        ]
    }

    return jsonify(json_body)

def send_ivr_response(clientActionId, promptMessage):
    # Define the JSON body
    json_body = {
        "clientActionId": clientActionId,
        "callflow": [
            {
            "action": "sayAndCapture",
            "params": {
                    "promptMessage": promptMessage,
                    "voiceProfile": "en-US-BenjaminRUS",
                    "speed": 1,
                    "minDigits": 1,
                    "maxDigits": 1,
                    "digitTimeout": 10000,
                    "overallTimeout": 10000,
                    "noOfTries": 2
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
        if webhook_data["payload"].get("clientActionId"): # Not Initial level of IVR, check which submenu
            client_action_id = webhook_data["payload"]["clientActionId"]

            # Reservations Menu
            if client_action_id == "reservations":
                if webhook_data["payload"]["dtmf"] == "1":
                    return send_ivr_response("book_table", "Reserving a Table, Press 1 to reserve a table for today, Press 2 to reserve a table for tomorrow")
                elif webhook_data["payload"]["dtmf"] == "2":
                    return send_ivr_response("reschedule_table", "Rescheduling your reservation, Press 1 to keep your current reservation, press 2 to change your reservation to tomorrow")
                elif webhook_data["payload"]["dtmf"] == "3":
                    return send_ivr_response("main_menu", "Welcome to ABC Restaurant, to book a table press 1, to speak to a representative press 2, to hear our restaurant hours press 3.")
                else:
                    return say_message_and_hangup("Invalid input, please call again.")
            
            # Connect Call Menu
            elif client_action_id == "connect_call":
                if webhook_data["payload"]["dtmf"] == "1":
                    return connect_call("post_call")
                elif webhook_data["payload"]["dtmf"] == "2":
                    return send_ivr_response("main_menu", "Welcome to ABC Restaurant, to book a table press 1, to speak to a representative press 2, to hear our restaurant hours press 3.")
                else:
                    return say_message_and_hangup("Invalid input, please call again.")

            # Book Table Menu
            elif client_action_id == "book_table":
                if webhook_data["payload"]["dtmf"] == "1":
                    return say_message_and_hangup("We have booked your table for today, thank you.")
                elif webhook_data["payload"]["dtmf"] == "2":
                    return say_message_and_hangup("We have booked your table for tomorrow, thank you.")
                else:
                    return say_message_and_hangup("Invalid input, please call again.")
            
            # Reschedule Table Menu
            elif client_action_id == "reschedule_table":
                if webhook_data["payload"]["dtmf"] == "1":
                    return say_message_and_hangup("Keeping your current reservation, thank you.")
                elif webhook_data["payload"]["dtmf"] == "2":
                    return say_message_and_hangup("Changing your reservation to tomorrow thank you.")
                else:
                    return say_message_and_hangup("Invalid input, please call again.")
                

            elif client_action_id == "post_call":
                return say_message_and_hangup("Thank you for speaking to ABC Restaurant, have a great day.")
            
            # Repeat of Main Menu
            elif client_action_id == "main_menu":
                if webhook_data["payload"]["dtmf"] == "1":
                    return send_ivr_response("reservations", "Press 1 to make a new reservation, press 2 to reschedule an existing reservation, press 3 to return to main menu.")
                elif webhook_data["payload"]["dtmf"] == "2":
                    return send_ivr_response("connect_call", "Connecting you to the next available representative. Press 1 to connect now, press 2 to return to main menu")
                elif webhook_data["payload"]["dtmf"] == "3":
                    return say_message_and_hangup("Our restaurant hours are between 9AM and 9PM every day of the week.")
                else:
                    return say_message_and_hangup("Invalid input, please call again.")

            else:
                say_message_and_hangup("Invalid input, please call again.")
        # Main Menu / Initial Menu
        else:
            if webhook_data["payload"]["dtmf"] == "1":
                return send_ivr_response("reservations", "Press 1 to make a new reservation, press 2 to reschedule an existing reservation, press 3 to return to main menu.")
            elif webhook_data["payload"]["dtmf"] == "2":
                return send_ivr_response("connect_call", "Connecting you to the next available representative. Press 1 to connect now, press 2 to return to main menu")
            elif webhook_data["payload"]["dtmf"] == "3":
                return say_message_and_hangup("Our restaurant hours are between 9AM and 9PM every day of the week.")
            else:
                return say_message_and_hangup("Invalid input, please call again.")
            
    else: # Not a VCA Webhook, print message.
        print("Not a VCA Webhook")
        return {}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
