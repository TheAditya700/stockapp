#!/bin/bash

echo "Starting Ticker Service..."

# Loop forever
while true; do
    echo "Ticking..."
    python3 flaskapp/updateprices_catchup.py
    
    # Sleep for 10 seconds
    sleep 10
done
