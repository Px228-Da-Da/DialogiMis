#!/bin/bash

# Install PostgreSQL
sudo apt-get update
# sudo apt-get install -y postgresql

# Start and enable PostgreSQL service
# sudo systemctl start postgresql
# sudo systemctl enable postgresql

# Create a PostgreSQL user and database
# sudo -u postgres psql -c "CREATE USER raspb WITH PASSWORD '123qweasd';"
# sudo -u postgres psql -c "CREATE DATABASE db WITH OWNER = raspb;"

# Grant necessary privileges to the user
# sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE db TO raspb;"
# sudo -u postgres psql -d db -c "GRANT ALL PRIVILEGES ON TABLE public.db TO raspb;"

# Create the 'db' table
# sudo -u postgres psql -d db -c "CREATE TABLE IF NOT EXISTS public.db (id text, user_id bigint, url_sheet text);"

# Create a systemd service file for TBots
cat <<EOL | sudo tee /etc/systemd/system/DialogiMis.service
[Unit]
Description=DialogiMis Service
After=network.target postgresql.service

[Service]
ExecStart=/usr/bin/python3 /home/raspb/DialogiMis/app.py
WorkingDirectory=/home/raspb/DialogiMis/
Restart=always
User=raspb

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and start TBots service
sudo systemctl daemon-reload
sudo systemctl start DialogiMis
sudo systemctl enable DialogiMis

echo "Installation completed successfully!"
