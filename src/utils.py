import json
import os
import uuid
from datetime import datetime


def current_req_dtm():
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def random_uuid():
    return str(uuid.uuid4())


def load_state(filename):
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        if "expiresAt" in data and isinstance(data["expiresAt"], str):
            data["expiresAt"] = datetime.fromisoformat(data["expiresAt"])
        return data
    except:
        return {}


def save_state(filename, state):
    if "expiresAt" in state and isinstance(state["expiresAt"], datetime):
        state["expiresAt"] = state["expiresAt"].isoformat()
    with open(filename, "w") as f:
        json.dump(state, f)


def parse_date_dmy(date_str):
    # date_str "dd/mm/yyyy"
    return datetime.strptime(date_str, "%d/%m/%Y")
