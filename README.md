# Lascaux Backend

Lascaux is a decentralized, text-based social media platform designed to empower users through distributed moderation and open-source development. Using Telestai's wallet-based authentication system, Lascaux ensures secure and decentralized user identity, content creation, and moderation. Users will be able to run their own instances of Lascaux, interact with other nodes, and contribute to the platform through open-source collaboration.

## Features:
- **Wallet-Based Authentication**: Users authenticate using a signature from their Telestai wallet.
- **Hybrid-Decentralized Architecture**: Content is stored locally on each node's SQLite database with long-term storage on IPFS for redundancy.
- **Voting-Based Moderation**: Community voting drives content approval and moderation, with potential AI assistance.
- **Open Source**: Lascaux is open-source, allowing users to fork, run their own instances, and contribute to the platform.

## Routes

### Authentication
1. **`POST /auth/login`**
   - **Description**: Authenticates a user via their Telestai wallet by verifying the signature using [this npm package](https://www.npmjs.com/package/@telestai-project/telestai-message).
   - **Input**: Signed message from the user's wallet.
   - **Output**: Session token or identifier for continued interaction with the platform.
   - **Purpose**: Enables users to securely log in without traditional credentials.

2. **`POST /auth/register`**
   - **Description**: Registers a new user with their Telestai wallet and additional profile details.
   - **Input**: Wallet signature, profile info (e.g., username, bio).
   - **Output**: Confirmation of successful registration.
   - **Purpose**: Completes the user profile beyond wallet signature.

3. **`POST /auth/verify`**
   - **Description**: Verifies a signed message for sensitive actions (e.g., content edit, delete).
   - **Input**: Signed message and action request.
   - **Output**: Success or failure of signature verification.
   - **Purpose**: Verifies the legitimacy of user actions on critical routes.

4. **`POST /auth/refresh`**
   - **Description**: Refreshes the session token for users who are still authenticated via their wallet.
   - **Input**: Current session token and wallet signature.
   - **Output**: New session token.
   - **Purpose**: Extends session without requiring full re-authentication.

### Profile Management
1. **`GET /profile/{wallet_address}`**
   - **Description**: Fetches a user's profile details based on their wallet address.
   - **Input**: Wallet address.
   - **Output**: User profile (username, bio, etc.).
   - **Purpose**: Displays user profile information.

2. **`PUT /profile/{wallet_address}`**
   - **Description**: Updates the profile details of the user.
   - **Input**: Wallet signature and updated profile data (e.g., bio, username).
   - **Output**: Confirmation of successful update.
   - **Purpose**: Allows users to modify their profile details securely.

3. **`POST /profile/complete`**
   - **Description**: Completes a user's profile after initial wallet-based registration.
   - **Input**: Profile details (e.g., username, bio).
   - **Output**: Confirmation of successful profile completion.
   - **Purpose**: Ensures that new users have full profiles after wallet registration.

### Content Management
1. **`POST /content/create`**
   - **Description**: Submits new content to the platform.
   - **Input**: Wallet signature, content details (e.g., text).
   - **Output**: Content ID or confirmation of successful creation.
   - **Purpose**: Allows users to create new posts on Lascaux.

2. **`GET /content/{content_id}`**
   - **Description**: Retrieves content by its unique content ID.
   - **Input**: Content ID.
   - **Output**: Content details (text, creator, votes).
   - **Purpose**: Displays a specific piece of content.

3. **`POST /content/edit/{content_id}`**
   - **Description**: Allows a user to edit their own content.
   - **Input**: Wallet signature and updated content.
   - **Output**: Confirmation of successful edit.
   - **Purpose**: Enables users to modify their previously submitted content.

4. **`DELETE /content/{content_id}`**
   - **Description**: Deletes a user’s content if it hasn’t been finalized or voted into the master branch.
   - **Input**: Wallet signature and content ID.
   - **Output**: Confirmation of deletion.
   - **Purpose**: Allows users to delete content they no longer wish to be public.

### Voting & Moderation
1. **`POST /content/{content_id}/vote`**
   - **Description**: Submits a vote for or against a piece of content.
   - **Input**: Wallet signature and vote (upvote/downvote).
   - **Output**: Confirmation of vote.
   - **Purpose**: Enables community voting on content moderation.

2. **`GET /content/{content_id}/votes`**
   - **Description**: Retrieves the current vote count and breakdown for a specific piece of content.
   - **Input**: Content ID.
   - **Output**: Vote totals (upvotes/downvotes).
   - **Purpose**: Shows voting results to users.

3. **`POST /content/{content_id}/moderate`**
   - **Description**: Flags content for moderation, either by AI or human moderators.
   - **Input**: Content ID and flagging reason.
   - **Output**: Confirmation of moderation request.
   - **Purpose**: Allows users or the system to flag inappropriate content.

### Node Synchronization
1. **`GET /node/sync`**
   - **Description**: Requests synchronization data from another node.
   - **Input**: Node ID or URL.
   - **Output**: Data for syncing local SQLite database.
   - **Purpose**: Keeps distributed instances in sync by fetching updates from other nodes.

2. **`POST /node/push`**
   - **Description**: Pushes data from one node to another to help with synchronization.
   - **Input**: Data for syncing (e.g., content updates).
   - **Output**: Confirmation of successful push.
   - **Purpose**: Allows a node to push its data to another node for syncing.

### IPFS Integration
1. **`POST /ipfs/push`**
   - **Description**: Uploads content to IPFS for long-term storage.
   - **Input**: Content data (e.g., text, media).
   - **Output**: IPFS hash.
   - **Purpose**: Ensures content persistence by uploading to IPFS.

2. **`GET /ipfs/{ipfs_hash}`**
   - **Description**: Retrieves content from IPFS using the provided hash.
   - **Input**: IPFS hash.
   - **Output**: Content data.
   - **Purpose**: Displays content stored on IPFS.

### Miscellaneous
1. **`GET /healthcheck`**
   - **Description**: Simple route to check if the node is running.
   - **Output**: "OK" if the server is running properly.
   - **Purpose**: Useful for automated monitoring systems.

2. **`GET /nodes/available`**
   - **Description**: Lists all currently available nodes that are online and can be interacted with.
   - **Output**: List of nodes (e.g., URLs, IPs).
   - **Purpose**: Allows users to select from available nodes.

## Contributing
Lascaux is open-source, and we welcome contributions. Fork the repository, create a branch, and submit a pull request with your changes. For large changes, please open an issue first to discuss what you’d like to modify. **Contributions will be rewarded**.
