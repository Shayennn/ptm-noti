from logger import log_json
from storage import get_storage
from ticket_processor import TicketProcessor
from token_manager import TokenManager


def main():
    try:
        token_manager = TokenManager()
        accessToken, refreshToken, expiresAt = token_manager.get_valid_token()

        storage = get_storage()
        processor = TicketProcessor(accessToken, storage)
        processor.process_tickets()
    except Exception as e:
        log_json(40, "Unhandled error", error=str(e))


if __name__ == "__main__":
    main()
