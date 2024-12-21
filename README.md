# Ticket Processing and Notification System

This application processes traffic tickets, retrieves detailed ticket information, fetches associated evidence images, and notifies users through various Apprise-supported channels. It supports storing evidence locally or in S3-compatible storage systems like AWS S3, Minio, or Cloudflare R2.

## Features

- **Authentication and Token Management**: Automatically handles token retrieval, refresh, and storage.
- **Ticket Processing**: Fetches new tickets, retrieves ticket details, and downloads evidence images.
- **Image Storage**: Supports both local storage (`file`) and S3-compatible storage (`s3`).
- **Notifications**: Sends ticket details and image attachments (or links) via Apprise-supported services (e.g., Telegram, Discord, Email).
- **JSON Logging**: Logs all operations, including ticket details, in a structured JSON format.

## Installation

### Prerequisites

- **Python**: Make sure you have Python 3.7 or later installed.
- **Dependencies**: Install required Python libraries.

### Clone the Repository

```bash
git clone https://github.com/Shayennn/ptm-noti
cd ptm-noti
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root with the following variables:

```dotenv
# API Credentials
CITIZEN_ID=1111111111119
USER_PASSWORD=SuperSecretP@ssw0rd

# Token expiration handling (in seconds)
NEAR_EXPIRY_THRESHOLD=60

# Notification system
APPRISE_URL=https://apprise.example.com/notify

# Storage configuration
STORAGE_BACKEND=file # Options: 'file' or 's3'
FILE_STORAGE_PATH=/app/data/images # Used if STORAGE_BACKEND is 'file'

# Don't set S3_ENDPOINT for AWS S3. Use the default endpoint.
S3_ENDPOINT=localhost:9000

# S3/S3-like configuration (used if STORAGE_BACKEND is 's3')
S3_ACCESS_KEY=admin
S3_SECRET_KEY=password
S3_BUCKET_NAME=mybucket

STATE_FILE=/app/data/state.json
```

## Usage

### Run the Application

```bash
python main.py
```

### How It Works

1. **Authentication**: The app authenticates with the API and retrieves an access token. If the token is about to expire, it attempts a refresh.
2. **Ticket Retrieval**: The app fetches all unprocessed tickets within the last year.
3. **Ticket Details and Evidence**: For each ticket, it retrieves detailed information and downloads associated evidence images.
4. **Image Storage**:
   - **Local**: Stores images in the directory specified by `FILE_STORAGE_PATH`.
   - **S3**: Uploads images to the configured S3-compatible storage.
5. **Notifications**:
   - Sends ticket details and image attachments (for `file` mode) or image links (for `s3` mode) via the Apprise URL.
6. **Logging**: Logs ticket details, notifications, and operational data in a JSON format.

## Configuration

### Storage Backend

- **File Storage**: Set `STORAGE_BACKEND=file` and specify a local directory with `FILE_STORAGE_PATH`.
- **S3-Compatible Storage**: Set `STORAGE_BACKEND=s3` and configure:
  - `S3_ENDPOINT` (leave empty for AWS S3)
  - `S3_ACCESS_KEY`, `S3_SECRET_KEY`
  - `S3_BUCKET_NAME`

### Notification Channels

- Use the `APPRISE_URL` environment variable to configure notification services. For example:
  - **Telegram**: `tgram://{bot_token}/{chat_id}`
  - **Discord**: `discord://{webhook_id}/{webhook_token}`
  - **Email**: `mailto://{email_address}`
- Refer to the [Apprise Documentation](https://github.com/caronc/apprise#supported-notifications) for a full list of supported services.

## Logs

Logs are generated in JSON format and printed to the console. Example log:

```json
{
  "timestamp": "2024-12-20T20:16:00",
  "level": "INFO",
  "message": "Processing ticket",
  "ticketInfo": {
    "ticketNo": "0000000000000",
    "dateHappen": "01/12/2024 09:09:00",
    "fineAmount": "500.0",
    "licensePlate": "ก-1 กรุงเทพมหานคร",
    "location": "ทล.1 0+100",
    "offense": "ฝ่าฝืนเครื่องหมายจราจร",
    "paidStatus": "PENDING"
  }
}
```

## Dependencies

This project uses the following Python libraries:

- **[requests](https://pypi.org/project/requests/)**: HTTP requests.
- **[boto3](https://pypi.org/project/boto3/)**: S3-compatible storage.
- **[apprise](https://pypi.org/project/apprise/)**: Notifications.
- **[python-dotenv](https://pypi.org/project/python-dotenv/)**: Environment variable management.

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Examples

### Local Storage and Telegram Notification

1. Configure `.env`:
2. Run the app:

   ```bash
   python main.py
   ```

### S3 Storage and Discord Notification

1. Configure `.env`:

   ```dotenv
   ...
   STORAGE_BACKEND=s3
   S3_ENDPOINT=http://localhost:9000
   S3_ACCESS_KEY=admin
   S3_SECRET_KEY=password
   S3_BUCKET_NAME=mybucket
   ...
   ```

2. Run the app:

   ```bash
   python main.py
   ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository, make changes, and submit a pull request. For major changes, please open an issue first to discuss what you’d like to change.

## Troubleshooting

### Common Issues

- **Token Expiry**: If the app fails due to token expiry, ensure the `.env` file is correctly configured with `CITIZEN_ID` and `USER_PASSWORD`.
- **S3 Configuration**: If using S3, ensure the bucket exists and the credentials in `.env` are correct.
- **Apprise Errors**: Test the `APPRISE_URL` with a simple `apprise` command to verify it works:

  ```bash
  apprise -t "Test Title" -b "Test Message" "tgram://{bot_token}/{chat_id}"
  ```

### Debugging

- Review logs for detailed information about the processing workflow and errors.
