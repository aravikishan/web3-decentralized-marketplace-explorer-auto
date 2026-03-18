#!/bin/bash
set -e
echo "Starting Web3 Decentralized Marketplace Explorer..."
uvicorn app:app --host 0.0.0.0 --port 9068 --workers 1
