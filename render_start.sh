#!/usr/bin/env bash
# Render.com start script for Nexomate
set -e

echo "=== Nexomate — Render Start Script ==="

# If Render disk is mounted, symlink data directory to persistent storage
RENDER_DISK="/opt/nexomate/data"
LOCAL_DATA="./data"

if [ -d "$RENDER_DISK" ]; then
    echo "Persistent disk detected at $RENDER_DISK"
    # Move existing data to persistent disk if first deploy
    if [ ! -f "$RENDER_DISK/nexomate.db" ] && [ -f "$LOCAL_DATA/nexomate.db" ]; then
        echo "Migrating local database to persistent disk..."
        cp -r "$LOCAL_DATA"/* "$RENDER_DISK"/ 2>/dev/null || true
    fi
    # Replace local data dir with symlink to persistent disk
    rm -rf "$LOCAL_DATA"
    ln -sf "$RENDER_DISK" "$LOCAL_DATA"
    echo "Data directory linked to persistent disk."
else
    echo "No persistent disk — using ephemeral storage."
    mkdir -p "$LOCAL_DATA"
fi

# Initialize database tables
echo "Initializing database..."
python -c "from database.database import engine, Base; from database import models; Base.metadata.create_all(bind=engine); print('Database ready.')"

# Run migrations
python -c "
try:
    from database.migrations import run_migrations
    run_migrations()
    print('Migrations complete.')
except Exception as e:
    print(f'Migrations skipped: {e}')
"

echo "Starting Streamlit..."
exec streamlit run app.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --browser.gatherUsageStats=false
