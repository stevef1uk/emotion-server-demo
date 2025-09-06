# Emotion Service Stack

A complete Docker Compose setup for the Emotion API service, featuring a **Gradio UI** and an **MCP server** for streamlined experimentation and access.

## Architecture

The stack consists of three main services:

* **Emotion API (`emotion-api`)**: The core Go server that runs the emotion analysis model using `llama.cpp` integration. This is the source of truth for emotion predictions. It contains a fine-tuned gemeni3:120 model embedded in a docker container. This componnet is external to this project see: https://hub.docker.com/repository/docker/stevef1uk/emotion-server/general for details.
* **Gradio UI (`emotion-ui`)**: A user-friendly Gradio-based web interface that allows for easy interaction with the service. It can send prediction requests directly to the `emotion-api` or via the `emotion-mcp` server.
* **MCP Server (`emotion-mcp`)**: A Go-based server that acts as a proxy, demonstrating the **Model Context Protocol (MCP)** approach. It routes requests from the UI to the Emotion API.

---

## Prerequisites

* **Docker** and **Docker Compose** installed.
* The required project files and directories (see Project Structure below).

---

## Project Structure

The project structure has been updated to reflect the new Gradio UI setup and the location of the `mcp-go-server`.

```bash
.
├── docker-compose.yml
├── ui/
│   ├── Dockerfile
│   └── ...
├── mcp-go-server/
│   ├── Dockerfile
│   └── ...
├── server/
│   ├── go.mod
│   └── ...
├── gemma3_emotion_model_unsloth/
│   └── ...
└── keys/
    └── public_key.pem
'''
---
## Quick Start
This stack is designed for a fast, hassle-free launch. 🚀

Clone the project or ensure all required files are in place.

Run the following command from the root directory to build and start all services in detached mode:


As the emotion-service docker container has differnet versions for Macs (Apple Silicon) and X86 and RPis a environmnet variable needs to be defined:
```

For a Mac (ARM64):

```bash
IMAGE_TAG=arm64 docker-compose up --build -d
```

For an RPi (ARM):

```bash
IMAGE_TAG=arm docker-compose up --build -d
```

For an Intel machine (AMD64):

```bash
IMAGE_TAG=amd64 docker-compose up --build -d
```

Note: The initial build may take a few minutes as it downloads base images and dependencies.

Access the services:

Gradio UI: http://localhost:7860

Emotion API: http://localhost:8000

MCP Server: http://localhost:9000

Service Details
Gradio UI (emotion-ui)

Port: 7860

Description: The primary user interface for this project. It lets you send text to the Emotion service and see the returned emotion. It's configured to access the services via two different paths:

Direct API: Requests are sent straight to http://emotion-api:8000.

MCP Approach: Requests are routed through the http://emotion-mcp:9000 server.

Environment Variables:

SG_BASE=http://emotion-mcp:9000

DIRECT_API_BASE=http://emotion-api:8000

Emotion API (emotion-api)

Port: 8000

Description: The core Go server with llama.cpp integration. It handles all emotion analysis logic.

Environment Variables:

MODEL_PATH=/app/model

GO_SERVER_PORT=8000

MCP Server (emotion-mcp)

Port: 9000

Description: A Go server that demonstrates the Model Context Protocol. It acts as a middle layer between the UI and the Emotion API.

Environment Variables:

EMOTION_SERVICE_URL=http://emotion-api:8000/predict

MCP_SERVER_PORT=9000

Management Commands
Command	Description
docker-compose up -d	Starts all services in the background.
docker-compose down	Stops and removes all containers, networks, and volumes.
docker-compose logs -f	Follows logs for all services.
docker-compose logs -f <service>	Follows logs for a specific service (e.g., emotion-ui).
docker-compose ps	Lists all services and their current status.
docker-compose restart <service>	Restarts a specific service.
Troubleshooting
Services won't start? Use docker-compose logs -f to see the error messages.

Can't access the UI? Make sure Docker is running and that port 7860 is not being used by another application.

Model decryption fails? Ensure that following expiry of the evaluation license a valid license is requested from the projects author (stevef1uk@gmail.com) if you wish to continue to use the docker emotion-service container.

If you have any further questions or issues, feel free to open an issue on the project's repository.

Disclaimers
For Educational/Experimental Purposes Only: This project is intended for educational and experimental purposes. It is not designed for production use without further security hardening and optimization.

No Guarantees: This software is provided "as-is" without any express or implied warranties. The authors and contributors disclaim all liability for any damage or loss resulting from its use.

Third-Party Components: This project utilizes several third-party libraries and components, each with its own license. Please refer to their respective documentation for licensing information.

Security: While efforts have been made to secure this setup, it is not a complete production-grade solution. The exposed ports and internal network configurations should be reviewed and secured for any public-facing deployment.
