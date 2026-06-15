#!/bin/bash
# Script to install RisePyMinder in cron
# Usage: bash install_cron.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${SCRIPT_DIR}/venv/bin/python"
MAIN_PY="${SCRIPT_DIR}/main.py"
LOG_FILE="${SCRIPT_DIR}/logs/cron.log"

# Create logs directory if it doesn't exist
mkdir -p "${SCRIPT_DIR}/logs"

# Add cron entry to run every 5 minutes
# Note: Adjust PYTHON_BIN if you use a different Python path

CRON_ENTRY="*/5 * * * * cd ${SCRIPT_DIR} && ${PYTHON_BIN} ${MAIN_PY} >> ${LOG_FILE} 2>&1"

# Get current crontab
CRONTAB_CONTENT=$(crontab -l 2>/dev/null || echo "")

# Check if entry already exists
if echo "$CRONTAB_CONTENT" | grep -q "${MAIN_PY}"; then
    echo "⚠️  Cron entry already exists for RisePyMinder"
    echo "Current crontab content:"
    crontab -l | grep "${MAIN_PY}" || echo "Not found"
else
    # Add new entry
    (echo "$CRONTAB_CONTENT"; echo "$CRON_ENTRY") | crontab -
    echo "✅ Cron entry installed successfully"
    echo "Will run: python main.py every 5 minutes"
    echo "Logs available at: ${LOG_FILE}"
fi
