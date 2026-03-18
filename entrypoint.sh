#!/bin/bash
set -e

echo "========================================="
echo "  Brewly - Starting deployment..."
echo "========================================="

# Wait for MySQL to be ready
echo "[1/3] Waiting for MySQL database..."
MAX_RETRIES=30
RETRY_COUNT=0

while ! nc -z ${DB_HOST:-db} ${DB_PORT:-3306} 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "ERROR: MySQL is not available after ${MAX_RETRIES} retries. Exiting."
        exit 1
    fi
    echo "  Waiting for MySQL... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

echo "  MySQL is ready!"

# Initialize database tables and seed data
echo "[2/3] Initializing database..."
flask init-db || echo "  Database already initialized or init skipped."

# Start the application
echo "[3/3] Starting application server..."
echo "========================================="
echo "  Brewly is running!"
echo "  URL: http://0.0.0.0:5000"
echo "  Admin: admin / admin123"
echo "========================================="

exec "$@"
