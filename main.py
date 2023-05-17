#? |-----------------------------------------------------------------------------------------------|
#? |  main.py                                                                                      |
#? |                                                                                               |
#? |  Copyright (c) 2021 Belikhun. All right reserved                                              |
#? |  Licensed under the MIT License. See LICENSE in the project root for license information.     |
#? |-----------------------------------------------------------------------------------------------|

import libs.ehook
from libs.log import log

from colorama import init, Fore
log("OKAY", "Imported: colorama")

from webhook import Webhook
log("OKAY", "Imported: webhook")

import json
log("OKAY", "Imported: json")

from flask import Flask, abort
log("OKAY", "Imported: flask")

from subprocess import Popen, PIPE
log("OKAY", "Imported: subprocess")

from multiprocessing import Process, Queue
log("OKAY", "Imported: multiprocessing")

log("INFO", "Reading Configuration File")
config = {}

with open("config.json", "r", encoding = "utf-8") as file:
	try:
		config = json.loads(file.read())
	except ValueError:
		log("ERRR", "Errored While Reading Configuration File")
		log("ERRR", "{} → Reason: {}JSON Decode Error (config.json)".format(Fore.WHITE, Fore.LIGHTBLACK_EX))
		exit(-1)

app = Flask(__name__)
webhook = Webhook(app, endpoint=config['endpoint'])

@app.route("/")
def index():
    abort(501)

@webhook.hook(event_type="ping")
def on_ping(data):
    log("INFO", "PONG!")
    return "PONG!", 200

# On Push to repository event
@webhook.hook(event_type="push")
def on_push(data):
    log("INFO", f"Got push event at {data['ref']}, triggered by {data['pusher']['name']}")

    # Parse target branch name
    branch = data["ref"].split("/")[2]

    if (config["branch"] == branch):
        p = Process(target=handle_push, args=(data,))
        p.start()

        return "Success", 200

    return "No Update", 200

def handle_push(data):
    for command in config["command"]:
        log("INFO", f"Executing Command: {Fore.LIGHTYELLOW_EX}\"{command}\" {Fore.WHITE}at {Fore.LIGHTCYAN_EX}\"{config['path']}\"")

        process = Popen(command.split(" "), cwd=config["path"], stdout=PIPE)
        (output, error) = process.communicate()
        exitCode = process.wait()

        output = output.decode("utf-8")

        if (exitCode != 0 or ("ERROR" in output) or error != None):
            log("ERRR", "{} → ProcessError: {}\"{}\" returned non-zero status code: {}".format(Fore.LIGHTRED_EX, Fore.LIGHTBLACK_EX, command, str(exitCode)))
            log("ERRR", f"   STDOUT: {output}")
            log("ERRR", f"   STDERR: {error}")
            raise Exception(f"Process returned bad status code: {exitCode}")

        log("OKAY", "Command Completed Successfully")

        # Line By Line Logging
        outputLines = output.split("\n")
        for line in outputLines:
            log("DEBG", f"\t{Fore.LIGHTBLACK_EX}{line}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config["port"])
