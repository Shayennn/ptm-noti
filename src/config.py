import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    CITIZEN_ID = os.getenv("CITIZEN_ID")
    USER_PASSWORD = os.getenv("USER_PASSWORD")
    NEAR_EXPIRY_THRESHOLD = int(os.getenv("NEAR_EXPIRY_THRESHOLD", "60"))
    APPRISE_URL = os.getenv("APPRISE_URL")

    STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "s3").lower()  # 'file' or 's3'
    FILE_STORAGE_PATH = os.getenv("FILE_STORAGE_PATH", "./images")

    # Generic S3 configs (works with AWS S3, Minio, R2, GCS S3-compatible endpoints)
    S3_ENDPOINT = os.getenv("S3_ENDPOINT", "")  # If empty, boto3 uses AWS directly.
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

    USERNAME = os.getenv("USERNAME", "fooClientIdPassword")
    PASSWORD = os.getenv("PASSWORD", "secret")

    BASE_URL_AUTH = "https://ptmapi.police.go.th/ETKServiceLogin/api/v1/user/authenticate"
    BASE_URL_ALLTICKETS = "https://ptmapi.police.go.th/ETKServiceTicket/api/v1/user/allTickets"
    BASE_URL_TICKETDETAIL = "https://ptmapi.police.go.th/ETKServiceTicket/api/v1/user/ticketDetail"
    BASE_URL_IMAGEEVIDENCE = (
        "https://ptmapi.police.go.th/ETKServiceTicket/api/v1/user/imageevidence"
    )
    BASE_URL_REFRESH = "https://ptmapi.police.go.th/ETKServiceTicket/api/v1/user/refreshaccesstoken"

    STATE_FILE = os.getenv("STATE_FILE", "state.json")
