# from flask_pymongo import PyMongo
import bson

from flask import current_app, g
from werkzeug.local import LocalProxy
from flask_pymongo import  MongoClient
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.objectid import ObjectId
from bson.errors import InvalidId
# Setup MongoDB here

client = MongoClient("mongodb+srv://test:asdfghjkl@cluster0.raozdxg.mongodb.net/webhook_db?retryWrites=true&w=majority")
db = client["webhook_db"]



def store_webhook_data(data):
    """
    Store webhook data in MongoDB
    """
    try:
        result = db.webhooks.insert_one(data)
        return str(result.inserted_id)
    except DuplicateKeyError:
        return "Duplicate entry"
    except OperationFailure as e:
        return f"Database operation failed: {str(e)}"
    
def format_event(event):
    action = event.get("action")
    author = event.get("author")
    from_branch = event.get("from_branch")
    to_branch = event.get("to_branch")
    timestamp = event.get("timestamp")
    if action == "push":
        return f'{author} pushed to {to_branch} on {timestamp}'
    elif action == "pull_request":
        return f'{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}'
    elif action == "merge":
        return f'{author} merged branch {from_branch} to {to_branch} on {timestamp}'
    return "Unknown action"
