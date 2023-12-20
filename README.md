# 8x8-advanced-ivr-callsflow-api
This repo is intended to show a sample backend that integrates with the 8x8 CallsFlow API. The two examples so far show:

Simple IVR - One level IVR with a simple menu, you can either hang up to acknowledge the message, connect to another number or repeat the menu.

Advanced IVR - Multi Level IVR where it has several levels of menus to navigate, similarly you can connect to another number or navigate through the menu tree.

## Dependencies ##
1. Python3
3. An 8x8 Subaccount w/ corresponding Virtual Numbers tied to it in order to place voice calls.

## How to run ##
0. Modify config.py with your 8x8 virtual number and the number you would like to connect to.
1. Create Virtual Environment - python3 -m venv myenv
2. Use Virtual Environment - source myenv/bin/activate
3. Install Requirements - pip install -r requirements.txt
4. Run the server - pipenv run python main.py
5. Enter localhost:80 in the browser (Note: Edit app.py to use a different port if it is already taken)