from flask import Blueprint, request, jsonify
from app.extensions import store_webhook_data, db, format_event
from datetime import datetime

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')


@webhook.route('/receiver', methods=["POST"])
def receiver():
    print("Received webhook data:", request.json)
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    print("Event type:", event_type)
    if event_type == "push":
        print("head commit id:", data["head_commit"]["id"])
        already_present = db.webhooks.find_one({"request_id": data["head_commit"]["id"]})
        if already_present:
            print("Webhook data already present or from merged pull request:", already_present)
        else:
            store_webhook_data({
                "request_id": data["head_commit"]["id"],
                "action": "push",
                "author": data["pusher"]["name"],
                "to_branch": data["ref"].split("/")[-1],
                "timestamp": datetime.now().strftime('%d %B %Y - %I:%M %p UTC')
        })
    elif event_type == "pull_request":
        if data["action"] == "opened":
            pr = data["pull_request"]
            store_webhook_data({
                "request_id": pr["id"],
                "action": "pull_request",
                "author": pr["user"]["login"],
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": datetime.now().strftime('%d %B %Y - %I:%M %p UTC')
            })
        elif data["action"] == "closed" and data["pull_request"]["merged"]:
            pr = data["pull_request"]
            store_webhook_data({
                "request_id": pr["id"],
                "action": "merge",
                "author": pr["merged_by"]["login"],
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": datetime.now().strftime('%d %B %Y - %I:%M %p UTC')
            })
    else:
        pass

    return jsonify({"status": "received"}), 200


@webhook.route("/events", methods=["GET"])
def get_events():
    events = list(db.webhooks.find().sort("_id", -1))
    formatted = [format_event(e) for e in events]
    return jsonify(formatted)
