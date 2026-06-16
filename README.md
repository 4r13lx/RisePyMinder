[![Scheduled Script Execution](https://github.com/4r13lx/RisePyMinder/actions/workflows/scheduled.yml/badge.svg)](https://github.com/4r13lx/RisePyMinder/actions/workflows/scheduled.yml)

# RisePyMinder

Scheduled notification system for general purposes (originally created for educational institutions). Sends automatic reminders through multiple channels (Email, Telegram, Discord, Slack, WhatsApp, etc.) based on a JSON schedule.

## Features

- ✅ Send notifications through multiple channels (Telegram, Discord, Email, Slack, WhatsApp, etc.)
- ✅ Flexible schedule based on JSON
- ✅ Configurable recipients via environment variables (comma-separated URLs)
- ✅ Automatic hour rounding (every 5 minutes)
- ✅ Configurable timezone (supports IANA timezone identifiers)
- ✅ Professional logging
- ✅ Modular and scalable structure

## Requirements

- Python 3.8+
- pip

## Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd RisePyMinder
```

### 2. Create virtual environment (recommended)

Remember to have `python3-venv` installed. Then run:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

Remember to have `pip` installed. Then run:

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your notification configurations
```

## Configuration

### Environment Variables

Recipients are configured through environment variables. The system supports any notification service compatible with Apprise.

**Basic Configuration:**

```bash
# Timezone (IANA timezone identifier)
# Examples: UTC, America/New_York, America/Argentina/Buenos_Aires, Europe/London, Asia/Tokyo
TIMEZONE=America/Argentina/Buenos_Aires

# Notification recipients (comma-separated URLs)
RECIPIENTS=tgram://bot_token/chat_id,discord://webhook_id/webhook_token
```

**Notification URL Examples:**

```bash
# Single Telegram recipient
RECIPIENTS=tgram://bot_token/chat_id

# Multiple recipients
RECIPIENTS=tgram://bot1/chat1,tgram://bot2/chat2

# Mixed services
RECIPIENTS=tgram://bot_token/chat_id,discord://webhook_id/webhook_token,mailtos://user@gmail.com

# Email
RECIPIENTS=mailtos://teacher@school.edu.ar

# Discord
RECIPIENTS=discord://webhook_id/webhook_token

# Slack
RECIPIENTS=slack://token_a/token_b/token_c

# Combination
RECIPIENTS=tgram://bot_token/chat_id,mailtos://email@example.com,discord://webhook_id/webhook_token
```

For more Apprise options, see: https://github.com/caronc/apprise/wiki

**Available IANA Timezones:** https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

### JSON Schedule

The `data/schedule.json` file defines messages to send:

```json
[
  {
    "date": "14-06-2026",
    "time": "08:00",
    "message": "Message to send"
  },
  {
    "date": "15-06-2026",
    "time": "14:30",
    "message": "Another message"
  }
]
```

**Format:**
- `date`: DD-MM-YYYY format
- `time`: HH:MM format (rounded every 5 minutes)
- `message`: Message text

## Usage

### Manual execution

```bash
python main.py
```

### Scheduled execution (Cron)

Every 5 minutes:

```bash
*/5 * * * * cd /path/to/project && python main.py >> logs/cron.log 2>&1
```

Every hour:

```bash
0 * * * * cd /path/to/project && python main.py >> logs/cron.log 2>&1
```

### With Docker

Using Docker Compose (recommended):

```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f risepyminder

# Stop the service
docker-compose down
```

**Customizing timezone in Docker:**

Edit `docker-compose.yml` and update the `TIMEZONE` environment variable:

```yaml
environment:
  - TIMEZONE=America/Argentina/Buenos_Aires
```

Or override it when running:

```bash
docker-compose run -e TIMEZONE=America/New_York risepyminder
```

Manual Docker execution:

```bash
docker build -t risepyminder:latest .
docker run -d \
  --env-file .env \
  -e TIMEZONE=UTC \
  -v ./logs:/app/logs \
  -v ./data:/app/data \
  risepyminder:latest
```

## Project Structure

```
RisePyMinder/
├── scheduler/
│   ├── __init__.py           # Exports main modules
│   ├── scheduler.py          # Scheduled message orchestrator
│   ├── notification.py       # Notification service with Apprise
│   └── config.py            # Centralized configuration
├── data/
│   └── schedule.json        # Message schedule
├── logs/                     # Execution logs
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Configuration template
├── README.md                 # This file
├── EXAMPLES.md               # Configuration examples
└── Dockerfile                # Docker configuration
```

## Documentation

- **[README.md](README.md)** - Main documentation
- **[EXAMPLES.md](EXAMPLES.md)** - Configuration examples for different scenarios
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

## Development

### Install development dependencies

```bash
pip install -r requirements.txt
```

### Run tests

```bash
pytest tests/ -v
```

### Run linter

```bash
flake8 scheduler/
black --check scheduler/
```

### Type checking

```bash
mypy scheduler/
```

## Logs

Logs are written to:
- **Console**: Real-time output
- **Files**: In `logs/`

Default level: INFO

To change logging level, edit `scheduler/config.py`.

## Troubleshooting

### Error: "RECIPIENTS environment variable not configured"

Check that:
1. `RECIPIENTS` environment variable exists in `.env`
2. URLs are properly formatted and separated by commas
3. You reloaded `.env` after editing

### Error: "Unknown timezone"

Verify that the timezone is valid according to IANA standard. Examples:
- `UTC`
- `America/New_York`
- `America/Argentina/Buenos_Aires`
- `Europe/London`
- `Asia/Tokyo`

See: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

### Error: "Invalid URL format"

Verify that the Apprise URL is valid. See https://github.com/caronc/apprise/wiki

### Messages not being sent

1. Verify schedule is correctly formatted (valid JSON)
2. Check that date and time match exactly
3. Verify timezone is correct
4. Review logs: `tail -f logs/*.log`

## License

**[GNU General Public License v3](https://github.com/4r13lx/RisePyMinder/LICENSE)**

## Contact

To report issues or suggestions, open an issue in the repository.
