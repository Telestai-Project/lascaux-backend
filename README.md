# Lascaux v3 Documentation

## Overview

This application is a social platform API built with FastAPI and backed by a Cassandra database. It allows you to run your own Lascaux community. The application includes several endpoints for authentication, user management, posts, news, and votes.

## Prerequisites

- Python >=3.10
- `pip` for managing Python packages
- `make` utility
- Cassandra database (automatically pulled andstarted by the application)

## Installation

1. **Clone the Repository:**

   Clone the repository to your local machine.

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Dependencies:**

   Use the `make` command to install all necessary Python packages.

   ```bash
   make install
   ```

## Running the Application

To start the application, use the `make` command:

```bash
make run_app
```

This command will execute the `run_app` target in the Makefile, which runs the FastAPI application located at `app/start_application.py`.

## Health Check

Once the application is running, you can perform a health check by accessing the `/healthcheck` endpoint:

```bash
http://<your-server-address>/healthcheck
```

This should return a JSON response indicating the status of the application:

```json
{
  "status": "ok"
}
```

## Development Note

The `run_bot` command is currently in development and not officially supported. It is intended for future features and should not be used in production environments.

## Setting Up a systemd Service

To ensure that your application runs as a service and restarts automatically on failure, you can create a `systemd` service file.

1. **Create a systemd Service File:**

   Create a new file at `/etc/systemd/system/lascaux-node.service` with the following content:

   ```ini
   [Unit]
   Description=Lascaux Node
   After=network.target

   [Service]
   Type=simple
   WorkingDirectory=/path/to/your/repository
   ExecStart=/usr/bin/make run_app
   Restart=on-failure
   User=your-username
   Group=your-groupname

   [Install]
   WantedBy=multi-user.target
   ```

   Replace `/path/to/your/repository`, `your-username`, and `your-groupname` with the appropriate values for your setup.

2. **Enable and Start the Service:**

   Enable the service to start on boot and start it immediately:

   ```bash
   sudo systemctl enable myapp.service
   sudo systemctl start myapp.service
   ```

3. **Check Service Status:**

   You can check the status of your service with:

   ```bash
   sudo systemctl status myapp.service
   ```

This setup will ensure that your application runs continuously and restarts automatically if it crashes.
