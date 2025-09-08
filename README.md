### Emotion Service Stack

A complete Docker Compose setup for the Emotion API service, featuring a **Gradio UI** and an **MCP server** for streamlined experimentation and access.

***

### Architecture

The stack consists of three main services:

* **Emotion API (emotion-api):** The core Go server that runs the emotion analysis model using **llama.cpp** integration. This is the source of truth for emotion predictions. It contains a fine-tuned gemeni3:120 model embedded in a docker container. This componnet is external to this project see: https://hub.docker.com/repository/docker/stevef1uk/emotion-server/general for details.
* **Gradio UI (emotion-ui):** A user-friendly Gradio-based web interface that allows for easy interaction with the service. It can send prediction requests directly to the **emotion-api** or via the **emotion-mcp** server.
* **MCP Server (emotion-mcp):** A Go-based server that acts as a proxy, demonstrating the **Model Context Protocol (MCP)** approach. It routes requests from the UI to the Emotion API.

***

### Prerequisites

* **Docker** and **Docker Compose** installed.
* The required project files and directories (see Project Structure below).

***

### Project Structure

The project structure has been updated to reflect the new Gradio UI setup, the location of the **mcp-go-server**, and the addition of a **tests** directory.
