# Lascaux v3 Documentation

## Overview

This application is a social platform API built with FastAPI and backed by a Cassandra database. It allows you to run your own Lascaux community. The application includes several endpoints for authentication, user management, posts, news, and votes.

The deployment of the Lascaux backend is streamlined using Docker containers, which simplifies the production setup. The application runs in two main containers: one for the FastAPI application (`lasko_app`) and another for the Cassandra database (`lasko_cassandra`). This containerized approach ensures consistent environments across different stages of development and production, enhancing scalability and reliability.

Security considerations are thoroughly addressed to protect the database, including:

- **TLS/SSL Encryption**: Ensures secure client and inter-node communication.
- **Client Authentication**: Verifies the identity of clients connecting to the database.
- **Authorization**: Controls access to resources within the database.

Additionally, the database is isolated within a private network, further enhancing its security by preventing unauthorized external access.

## Prerequisites

- Python >=3.10
- Docker & Docker Compose installed on your machine.
- Java Development Kit (JDK) 11 or later installed on your machine.
- OpenSSL installed on your machine: Required for generating and managing SSL certificates.

## Installation

1. **Clone the Repository:**

   Clone the repository to your local machine.

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Generate SSL Certificate:**

   This section will guide you through the process of generating a self-signed SSL certificate for your Cassandra cluster.
   
   2.1 Create a directory for the certificates and navigate to it. Must be in the root of the project.

   ```bash
   mkdir -p ssl
   cd ssl
   ```

   2.2 Generate Server Certificate (Keystore)

   To enhance the security of Cassandra with SSL/TLS, you need to create a keystore and truststore. For simplicity, self-signed certificates can be generated.
   
   ```bash
   keytool -genkeypair \
      -keyalg RSA \
      -alias cassandra \
      -keystore cassandra.keystore \
      -storepass cassandra \
      -validity 365 \
      -keysize 2048 \
      -dname "CN=cassandra"
   ```
   This command will generate a self-signed certificate and save it as `cassandra.keystore`. The password for the keystore is `cassandra`.

   2.3 Generate Client Certificate (Truststore)

   Export the certificates and create a truststore to allow Cassandra nodes and clients to trust each other.

   ```bash
   # Export server certificate
   keytool -export -alias cassandra -keystore cassandra.keystore -file cassandra.crt -storepass cassandra

   # Create a truststore
   keytool -import -file cassandra.crt -alias cassandra -keystore cassandra.truststore -storepass cassandra -noprompt
   ```
   These commands will create a truststore named `cassandra.truststore` and export the server certificate as `cassandra.crt`.

   2.4 Convert JKS to PKCS12

   To convert the Java KeyStore (JKS) to PKCS12 format, use the following command:

   ```bash
   keytool -importkeystore -srckeystore cassandra.keystore -destkeystore cassandra.p12 -deststoretype PKCS12 -srcstorepass cassandra -deststorepass cassandra
   ```

   This step is necessary because the PKCS12 format is more widely supported across different platforms and applications, including FastAPI. It allows for easier integration and management of SSL certificates within the FastAPI environment. Thise command will create a PKCS12 file named `cassandra.p12`.

   2.5 Extract Certificates in PEM Format

   To extract the certificates in PEM format, execute the following commands:

   ```bash
   openssl pkcs12 -in cassandra.p12 -out client-cert.pem -clcerts -nokeys -passin pass:cassandra
   openssl pkcs12 -in cassandra.p12 -out client-key.pem -nocerts -nodes -passin pass:cassandra
   ```

   Extracting the certificates in PEM format is crucial because FastAPI, like many other web frameworks, often requires SSL certificates in PEM format for secure communication. The PEM format is a standard for encoding certificates and keys, making it compatible with FastAPI's SSL/TLS configuration. This command will create a client-cert.pem file and a client-key.pem file.

   Before proceeding to the next step, the user should have the following 6 files in the `ssl` directory, using the exact names as listed:
   - `cassandra.keystore`
   - `cassandra.crt`
   - `cassandra.truststore`
   - `cassandra.p12`
   - `client-cert.pem`
   - `client-key.pem`

   **Note 1**: It is crucial to use these exact file names to ensure the application can correctly locate and use the SSL certificates and keys during setup and operation.

   **Note 2**: The password used for generating the SSL certificates can be changed to any other value, but it must be consistent across all certificate generation steps. In our example, the common password used was 'cassandra'.

3. **Configure Environment Variables:**

   Copy the `.env.example` file to `.env` and configure the environment variables.

   ```bash
   cp .env.example .env
   ```

   The `.env` file should have at least the following variables:
   - `CASSANDRA_USER`: The user of the Cassandra database.
   - `CASSANDRA_PASSWORD`: The password of the Cassandra database.

4. **Customize Cassandra Configuration:**

   Any specific or additional configuration you wish to incorporate into Cassandra can be managed through the `cassandra.yaml` file. This file has been pre-configured for our backend, but each user can modify it to change its behavior according to their needs.

## Running the Application

To start the application, execute the script with Python:

```bash
python3 manage_docker.py
```

This script will present the user with a menu of options to manage the backend:

1. **Start Lasko Backend**: This option will initiate the FastAPI application and the Cassandra database, setting up the necessary Docker containers to run the backend services.

2. **Show Container Status (including Cassandra)**: Select this to view the current status of all running containers, including the Cassandra database, providing insights into their operational state.

3. **Exit and Leave Running**: Use this option to exit the script while keeping the Lasko backend and Cassandra containers running, allowing the services to continue operating without interruption.

4. **Stop and Exit Without Removing Containers and Images**: This option stops the running containers and exits the script, but retains the containers and images for future use, facilitating quick restarts.

5. **Stop, Exit and Remove All Containers and Images**: Choose this to completely stop and remove all containers and images, effectively cleaning up the environment and freeing up resources.

## Health Check

Once the application is running, you can perform a health check by accessing the `/healthcheck` endpoint:

```bash
http://<your-server-address>:8000/healthcheck
```

This should return a JSON response indicating the status of the application:

```json
{
  "status": "ok"
}
```

## Automatic Restart

To ensure that the Docker containers for the Lasko backend automatically restart after a system reboot, a restart policy has been configured in the `docker-compose.yml` file. The `unless-stopped` policy is used, which means:

- Containers will always restart unless they are explicitly stopped.
- This ensures that the application remains available after a system reboot or unexpected shutdown.