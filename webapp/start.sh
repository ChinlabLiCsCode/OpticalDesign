#!/bin/bash
# Start backend and frontend dev servers
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting FastAPI backend on http://localhost:8000..."
cd "$SCRIPT_DIR/backend"
conda run -n base python -m uvicorn main:app --port 8000 --reload &
BACKEND_PID=$!

echo "Starting Vite frontend on http://localhost:5173..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "  Backend  → http://localhost:8000"
echo "  Frontend → http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
