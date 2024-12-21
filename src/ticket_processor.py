import json
from datetime import datetime

import requests

from config import Config
from logger import log_json
from notifier import send_notification
from utils import current_req_dtm, load_state, parse_date_dmy, random_uuid, save_state


class TicketProcessor:
    def __init__(self, accessToken, storage):
        self.accessToken = accessToken
        self.storage = storage
        self.state = load_state(Config.STATE_FILE)

    def common_headers(self):
        return {
            "reqBy": "ETICKET",
            "reqDtm": current_req_dtm(),
            "reqID": random_uuid(),
            "src": "ETICKET",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.accessToken}",
        }

    def get_all_tickets(self, paidStatus=""):
        payload = {
            "fromDate": self._one_year_ago_str(),
            "toDate": self._today_str(),
            "reqDtm": current_req_dtm(),
            "citizen": Config.CITIZEN_ID,
            "paidStatus": paidStatus,
        }
        response = requests.post(
            Config.BASE_URL_ALLTICKETS, headers=self.common_headers(), json=payload
        )
        if response.status_code != 200:
            log_json(40, "allTickets failed", status=response.status_code)
            raise Exception("allTickets failed")

        outer = response.json()
        data = json.loads(outer["value"])
        if data["status"] != "000" and data["msgEn"] != "Not found Ticket":
            log_json(40, "allTickets error", msgEn=data["msgEn"])
            raise Exception(f"allTickets error: {data['msgEn']}")
        elif data["msgEn"] == "Not found Ticket":
            return []
        return data["tickets"]

    def get_ticket_detail(self, ticketNo):
        payload = {"ticketNo": ticketNo, "reqDtm": current_req_dtm()}
        response = requests.post(
            Config.BASE_URL_TICKETDETAIL, headers=self.common_headers(), json=payload
        )
        if response.status_code != 200:
            log_json(40, "ticketDetail failed", status=response.status_code)
            raise Exception("ticketDetail failed")
        outer = response.json()
        data = json.loads(outer["value"])
        if data["status"] != "000":
            log_json(40, "ticketDetail error", msgEn=data["msgEn"])
            raise Exception(f"ticketDetail error: {data['msgEn']}")
        return data["ticketDetail"]

    def get_image_evidence(self, ticketNo):
        payload = {
            "citizen": Config.CITIZEN_ID,
            "ticketNo": ticketNo,
            "reqDtm": current_req_dtm(),
        }
        response = requests.post(
            Config.BASE_URL_IMAGEEVIDENCE, headers=self.common_headers(), json=payload
        )
        if response.status_code != 200:
            log_json(40, "imageevidence failed", status=response.status_code)
            raise Exception("imageevidence failed")
        outer = response.json()
        data = json.loads(outer["value"])
        if data["status"] != "000":
            log_json(40, "imageevidence error", msgEn=data["msgEn"])
            raise Exception(f"imageevidence error: {data['msgEn']}")
        return data

    def process_tickets(self):
        tickets = self.get_all_tickets()
        log_json(20, "Retrieved tickets", count=len(tickets))

        processedTickets = self.state.get("processedTickets", [])
        new_tickets = [t for t in tickets if t["ticketNo"] not in processedTickets]

        if not new_tickets:
            log_json(20, "No new tickets to process")
            return

        for ticket in new_tickets:
            ticketNo = ticket["ticketNo"]
            detail = self.get_ticket_detail(ticketNo)

            # Extract key ticket information
            ticket_info = {
                "ticketNo": ticketNo,
                "dateHappen": detail["dateHappen"],
                "fineAmount": detail.get("fineAmount"),
                "licensePlate": detail.get("plate"),
                "location": detail.get("road"),
                "offense": detail.get("accuse1Desc"),
                "paidStatus": detail.get("paidStatus"),
                "limitSpeed": detail.get("limitSpeed"),
                "speed": detail.get("speed"),
                "lane": detail.get("lane"),
                "orderDivision": detail.get("orderDivision"),
                "createDate": detail.get("createDate"),
                "orderName": detail.get("orderName"),
            }
            log_json(20, "Processing ticket", ticketInfo=ticket_info)

            # Prepare date for image filenames
            date_str = detail["dateHappen"].split(" ")[0]  # e.g., "01/12/2024"
            happen_dt = parse_date_dmy(date_str)
            date_for_name = happen_dt.strftime("%Y%m%d")

            # Get and save image evidence
            image_data = self.get_image_evidence(ticketNo)
            images = []
            attachments = []
            for i in range(1, 10):
                key = f"upImage{i}"
                if key in image_data and image_data[key]:
                    img_data = image_data[key]
                    img_bytes = self._decode_image(img_data)
                    filename = f"{date_for_name}_{ticketNo}_{i}.png"
                    self.storage.upload_image(filename, img_bytes)
                    images.append(filename)
                    # Attachments depend on storage backend
                    attachments.append(self.storage.get_image_access(filename))  # S3 URL

            # Add ticket to processed list
            processedTickets.append(ticketNo)
            self.state["processedTickets"] = processedTickets
            save_state(Config.STATE_FILE, self.state)

            # Notify with ticket information
            if Config.STORAGE_BACKEND == "file":
                send_notification(
                    self._format_notification_message(ticket_info, len(images)),
                    attachments=attachments,
                )
            else:
                # S3 mode: include image URLs in the message
                urls = "\n".join(attachments)
                message = self._format_notification_message(ticket_info, len(images)) + "\n" + urls
                send_notification(message)

        log_json(20, "Processing complete")

    def _format_notification_message(self, ticket_info, image_count):
        """
        Format the notification message with ticket info and image count.
        """
        text_msg = f"New ticket processed:\n"
        text_msg += f"- Ticket No: {ticket_info['ticketNo']}\n"
        text_msg += f"- Order Name: {ticket_info['orderName']}\n"
        text_msg += f"- Date: {ticket_info['dateHappen']}\n"
        text_msg += f"- Create Date: {ticket_info['createDate']}\n"
        text_msg += (
            f"- Order Division: {ticket_info['orderDivision']}\n"
            if ticket_info["orderDivision"]
            else ""
        )
        text_msg += f"- Fine Amount: {ticket_info['fineAmount']} THB\n"
        text_msg += f"- License Plate: {ticket_info['licensePlate']}\n"
        text_msg += f"- Location: {ticket_info['location']}\n"
        text_msg += f"- Offense: {ticket_info['offense']}\n"
        text_msg += (
            f"- Speed Limit: {ticket_info['limitSpeed']} km/h\n"
            if ticket_info["limitSpeed"]
            else ""
        )
        text_msg += f"- Speed: {ticket_info['speed']} km/h\n" if ticket_info["speed"] else ""
        text_msg += f"- Lane: {ticket_info['lane']}\n" if ticket_info["lane"] else ""
        text_msg += f"- Images: {image_count}"

        return text_msg

    def _decode_image(self, b64_str):
        import base64

        return base64.b64decode(b64_str)

    def _one_year_ago_str(self):
        from datetime import datetime, timedelta

        one_year_ago = datetime.now() - timedelta(days=365)
        return one_year_ago.strftime("%d/%m/%Y")

    def _today_str(self):
        from datetime import datetime

        return datetime.now().strftime("%d/%m/%Y")
