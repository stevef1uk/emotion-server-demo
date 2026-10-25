# License Keys Directory

This directory is used to mount commercial decryption keys when running the Emotion Service locally via Docker Compose.

- **Public / Demo Mode (Default)**:
  - If no `customer_private.pem` is placed in this directory, the service will run in locked demonstration mode.
  - Calling the Emotion API or MCP Server will cleanly inform the user that a commercial license is required and direct them to [https://emotion-service-api.sjfisher.com](https://emotion-service-api.sjfisher.com).

- **Licensed Mode**:
  - If you have purchased a commercial license from [sales@sjfisher.com](mailto:sales@sjfisher.com), place your assigned `customer_private.pem` and `token.txt` in this directory:
    ```
    keys/
    ├── customer_private.pem
    └── token.txt
    ```
  - Docker Compose will mount your private key to `/app/keys/customer_private.pem`, unlocking the encrypted model on startup.
