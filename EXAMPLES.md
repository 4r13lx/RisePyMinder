# RisePyMinder - Configuration Examples

This file contains complete `.env` configuration examples for different scenarios.

## Example 1: Single Telegram Recipient

```bash
# .env
TIMEZONE=America/Argentina/Buenos_Aires
RECIPIENTS=tgram://YOUR_BOT_TOKEN/YOUR_CHAT_ID
```

**schedule.json:**
```json
[
  {
    "date": "14-06-2026",
    "time": "08:00",
    "message": "Good morning! Time for the daily standup."
  }
]
```

## Example 2: Multiple Telegram Recipients

```bash
# .env
TIMEZONE=America/Argentina/Buenos_Aires
RECIPIENTS=tgram://BOT_TOKEN_1/CHAT_ID_1,tgram://BOT_TOKEN_2/CHAT_ID_2,tgram://BOT_TOKEN_3/CHAT_ID_3
```

## Example 3: Mixed Services (Telegram + Discord + Email)

```bash
# .env
TIMEZONE=UTC
RECIPIENTS=tgram://BOT_TOKEN/CHAT_ID,discord://WEBHOOK_ID/WEBHOOK_TOKEN,mailtos://your.email@gmail.com
```

**schedule.json:**
```json
[
  {
    "date": "14-06-2026",
    "time": "09:00",
    "message": "Meeting starts in 1 hour"
  },
  {
    "date": "14-06-2026",
    "time": "17:00",
    "message": "End of day report due"
  }
]
```

## Example 4: Different messages for independent recipients

```bash
# .env
TIME_ZONE=America/Argentina/Buenos_Aires
# Named destinations can represent any channel/group, not predefined roles.
RECIPIENT_MATH=discord://MATH_CHANNEL_WEBHOOK_ID/MATH_CHANNEL_WEBHOOK_TOKEN
RECIPIENT_HISTORY=discord://HISTORY_CHANNEL_WEBHOOK_ID/HISTORY_CHANNEL_WEBHOOK_TOKEN
RECIPIENT_STAFF=discord://STAFF_CHANNEL_WEBHOOK_ID/STAFF_CHANNEL_WEBHOOK_TOKEN
```

**schedule.json:**
```json
[
  {
    "date": "17-06-2026",
    "time": "08:00",
    "message": "Math class starts in 1 hour",
    "recipient": "math"
  },
  {
    "date": "17-06-2026",
    "time": "08:00",
    "message": "History materials are ready",
    "recipient": "history"
  },
  {
    "date": "17-06-2026",
    "time": "17:00",
    "message": "Staff meeting reminder",
    "recipient": "staff"
  },
  {
    "date": "18-06-2026",
    "time": "09:00",
    "message": "Shared announcement",
    "recipients": ["math", "history"]
  }
]
```

Each `recipient` name resolves to `RECIPIENT_<NAME>` (case-insensitive). `recipients` can select multiple names. Each Discord webhook routes to its own channel. Unnamed schedule entries continue to use the legacy `RECIPIENTS` list.

## Example 5: Different Timezones

### US Eastern Time
```bash
TIMEZONE=America/New_York
RECIPIENTS=discord://WEBHOOK_ID/WEBHOOK_TOKEN
```

### UK Time
```bash
TIMEZONE=Europe/London
RECIPIENTS=slack://TOKEN_A/TOKEN_B/TOKEN_C
```

### India Time
```bash
TIMEZONE=Asia/Kolkata
RECIPIENTS=tgram://BOT_TOKEN/CHAT_ID
```

### Japan Time
```bash
TIMEZONE=Asia/Tokyo
RECIPIENTS=mailtos://user@company.jp
```

## Example 6: Docker Compose Setup

**docker-compose.yml override:**
```yaml
version: '3.8'

services:
  risepyminder:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: risepyminder
    environment:
      - PYTHONUNBUFFERED=1
      - TIME_ZONE=America/Argentina/Buenos_Aires
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    networks:
      - risepyminder-network

networks:
  risepyminder-network:
    driver: bridge
```

## Apprise URL Format Reference

### Telegram
```
tgram://BOT_TOKEN/CHAT_ID
```

### Discord
```
discord://WEBHOOK_ID/WEBHOOK_TOKEN
```

### Email (Gmail with App Password)
```
mailtos://your_email@gmail.com:app_password@gmail.com
```

### Slack
```
slack://TOKEN_A/TOKEN_B/TOKEN_C
```

### WhatsApp (via Twilio)
```
twilio://ACCOUNT_SID:AUTH_TOKEN@FROM_NUMBER:TO_NUMBER
```

### MS Teams
```
msteams://TOKEN_A/TOKEN_B/TOKEN_C
```

For more formats, see: https://github.com/caronc/apprise/wiki

## Full .env Template

```bash
# Timezone - IANA identifier
# See: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE=UTC

# Legacy destinations used only for schedule entries without recipient/recipients
RECIPIENTS=

# Named destinations used as recipient values in schedule.json
RECIPIENT_MATH=discord://WEBHOOK_ID/WEBHOOK_TOKEN
RECIPIENT_STAFF=tgram://BOT_TOKEN/CHAT_ID

# Optional: Custom log level
# Supported: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

## Testing Your Configuration

1. **Verify the `.env` file:**
   ```bash
   cat .env
   ```

2. **Check that recipients are valid:**
   ```bash
   python -c "import apprise; a = apprise.Apprise(); print(a.add('YOUR_URL_HERE'))"
   ```

3. **Create a test schedule:**
   ```json
   [
     {
       "date": "14-06-2026",
       "time": "21:23",
       "message": "Test message from RisePyMinder"
     }
   ]
   ```

4. **Run the scheduler:**
   ```bash
   python main.py
   ```

5. **Check logs:**
   ```bash
   tail -f logs/*.log
   ```
