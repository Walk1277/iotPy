#!/bin/bash
# Start Python Backend
# Usage: ./start_backend.sh

cd "$(dirname "$0")"
echo "Starting Python Backend..."
echo "Press Ctrl+C to stop"
python3 main.py start

