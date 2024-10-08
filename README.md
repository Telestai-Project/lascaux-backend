# Lascaux Backend

Lascaux is a decentralized, text-based social media platform designed to empower users through distributed moderation and open-source development. Using Telestai's wallet-based authentication system, Lascaux ensures secure and decentralized user identity, content creation, and moderation. Users will be able to run their own instances of Lascaux, interact with other nodes, and contribute to the platform through open-source collaboration.

## Features:
- **Wallet-Based Authentication**: Users authenticate using a signature from their Telestai wallet.
- **Hybrid-Decentralized Architecture**: Content is stored locally on each node's SQLite database with long-term storage on IPFS for redundancy.
- **Voting-Based Moderation**: Community voting drives content approval and moderation, with potential AI assistance.
- **Open Source**: Lascaux is open-source, allowing users to fork, run their own instances, and contribute to the platform.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Telestai-Project/lascaux-backend.git
   cd lascaux-backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python -c "from app.database import init_db; init_db()"
   ```

4. Run the FastAPI application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Routes

### Authentication
- **`POST /auth/login`**: Authenticates a user via their Telestai wallet.
- **`POST /auth/register`**: Registers a new user with their Telestai wallet.
- **`POST /auth/verify`**: Verifies a signed message for sensitive actions.
- **`POST /auth/refresh`**: Refreshes the session token.

### Profile Management
- **`GET /profile/{wallet_address}`**: Fetches a user's profile details.
- **`PUT /profile/{wallet_address}`**: Updates the profile details of the user.
- **`POST /profile/complete`**: Completes a user's profile after initial registration.

### Content Management
- **`POST /content/create`**: Submits new content to the platform.
- **`GET /content/{content_id}`**: Retrieves content by its unique content ID.
- **`POST /content/edit/{content_id}`**: Allows a user to edit their own content.
- **`DELETE /content/{content_id}`**: Deletes a user’s content.

### Voting & Moderation
- **`POST /content/{content_id}/vote`**: Submits a vote for or against a piece of content.
- **`GET /content/{content_id}/votes`**: Retrieves the current vote count.
- **`POST /content/{content_id}/moderate`**: Flags content for moderation.

### Node Synchronization
- **`GET /node/sync`**: Requests synchronization data from another node.
- **`POST /node/push`**: Pushes data from one node to another.

### IPFS Integration
- **`POST /ipfs/push`**: Uploads content to IPFS.
- **`GET /ipfs/{ipfs_hash}`**: Retrieves content from IPFS.

### Miscellaneous
- **`GET /healthcheck`**: Checks if the node is running.
- **`GET /nodes/available`**: Lists all currently available nodes.

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- SQLAlchemy
- Pytest
- HTTPX

## Contributing
Lascaux is open-source, and we welcome contributions. Fork the repository, create a branch, and submit a pull request with your changes. For large changes, please open an issue first to discuss what you’d like to modify. **Contributions will be rewarded**.
