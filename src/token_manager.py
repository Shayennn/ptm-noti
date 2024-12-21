import json
from datetime import datetime, timedelta

import requests

from config import Config
from logger import log_json
from utils import current_req_dtm, load_state, random_uuid, save_state


class TokenManager:
    def __init__(self):
        self.state = load_state(Config.STATE_FILE)

    def get_valid_token(self):
        accessToken = self.state.get("accessToken")
        refreshToken = self.state.get("refreshToken")
        expiresAt = self.state.get("expiresAt")

        if not accessToken or not expiresAt:
            log_json(20, "No valid token, authenticating")
            return self.authenticate()

        now = datetime.utcnow()
        remaining = (expiresAt - now).total_seconds()
        if remaining < Config.NEAR_EXPIRY_THRESHOLD:
            log_json(20, "Token near expiry, refreshing")
            new_access, new_refresh, new_expiresAt = self.refresh_access_token(
                accessToken, refreshToken
            )
            if not new_access:
                log_json(20, "Refresh failed, re-authenticating")
                return self.authenticate()
            return new_access, new_refresh, new_expiresAt
        else:
            log_json(20, "Token valid", remaining_seconds=remaining)
            return accessToken, refreshToken, expiresAt

    def authenticate(self):
        headers = {
            "reqBy": "ETICKET",
            "reqDtm": current_req_dtm(),
            "reqID": random_uuid(),
            "src": "ETICKET",
            "Content-Type": "application/json",
        }

        payload = {
            "citizen": Config.CITIZEN_ID,
            "password": Config.USER_PASSWORD,
            "grant_type": "password",
            "reqDtm": current_req_dtm(),
        }

        response = requests.post(
            Config.BASE_URL_AUTH,
            headers=headers,
            auth=(Config.USERNAME, Config.PASSWORD),
            json=payload,
        )
        if response.status_code != 200:
            log_json(40, "Authentication failed", status=response.status_code)
            raise Exception("Authentication failed")

        outer = response.json()
        data = json.loads(outer["value"])
        accessToken = data.get("accessToken")
        refreshToken = data.get("refreshToken")
        expiresIn = data.get("expiresIn", 0)

        if not accessToken:
            log_json(40, "No access token in auth response")
            raise Exception("No access token found")

        expiresAt = datetime.utcnow() + timedelta(seconds=expiresIn)
        self.state["accessToken"] = accessToken
        self.state["refreshToken"] = refreshToken
        self.state["expiresAt"] = expiresAt
        save_state(Config.STATE_FILE, self.state)
        log_json(20, "Authenticated successfully")
        return accessToken, refreshToken, expiresAt

    def refresh_access_token(self, accessToken, refreshToken):
        if not refreshToken:
            return None, None, None

        headers = {
            "reqBy": "ETICKET",
            "reqDtm": current_req_dtm(),
            "reqID": random_uuid(),
            "src": "ETICKET",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {accessToken}",
        }

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refreshToken,
            "reqDtm": current_req_dtm(),
            "citizen": Config.CITIZEN_ID,
        }

        response = requests.post(Config.BASE_URL_REFRESH, headers=headers, json=payload)
        if response.status_code != 200:
            return None, None, None

        outer = response.json()
        data = json.loads(outer["value"])
        if data.get("status") != "000":
            return None, None, None

        new_access = data.get("accessToken")
        new_refresh = data.get("refreshToken")
        expiresIn = data.get("expiresIn", 0)
        if not new_access:
            return None, None, None

        expiresAt = datetime.utcnow() + timedelta(seconds=expiresIn)
        self.state["accessToken"] = new_access
        self.state["refreshToken"] = new_refresh
        self.state["expiresAt"] = expiresAt
        save_state(Config.STATE_FILE, self.state)
        log_json(20, "Token refreshed successfully")
        return new_access, new_refresh, expiresAt
