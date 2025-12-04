#!/bin/bash

# Run the initialization script
python3 initialize.py

# Start the Flask application
flask run --host=0.0.0.0 --port=5000
