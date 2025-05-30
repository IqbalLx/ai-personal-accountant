# Project Quickstart Guide

This guide will walk you through setting up and running the project.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **[UV](https://astral.sh/uv)**: A fast Python package installer and resolver.
2.  **Docker & Docker Compose**: For running the PostgreSQL database instance. (If not already installed, get them from [Docker's official website](https://www.docker.com/get-started)).

## Setup Instructions

Follow these steps to prepare your environment and install dependencies.

### 1. Clone the Repository (if you haven't already)

```bash
git clone git@github.com:IqbalLx/ai-personal-accountant.git
cd ai-personal-accountant
```

### 2\. Set Up Virtual Environment & Install Dependencies

This project uses `uv` for environment and package management.

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
# On macOS and Linux:
source .venv/bin/activate
# On Windows (PowerShell):
# .venv\Scripts\Activate.ps1
# On Windows (CMD):
# .venv\Scripts\activate.bat

# Install all project dependencies
uv sync
```

### 3\. Configure Google AI Services

You'll need a Google AI Studio API key to interact with Google's AI models.

1.  **Obtain your API Key**:

    - Go to [Google AI Studio](https://aistudio.google.com) and get your API key.
    - You will likely need to set this key as an environment variable or in a configuration file as per the project's requirements (e.g., `GOOGLE_API_KEY="YOUR_API_KEY"`).

2.  **(Optional) Enable Gemini Pro Model Usage**:

    - To use the Gemini Pro model, ensure your Google Cloud project associated with the API key has billing enabled. You can configure this in the [Google Cloud Console](https://console.cloud.google.com/).

## Running the Application

Once the setup and configuration are complete, you can run the application.

### 1\. Start the PostgreSQL Database

The project uses a PostgreSQL database managed via Docker Compose.

```bash
# Start the PostgreSQL service in detached mode
docker compose up -d
```

This command will download the PostgreSQL image (if not already present) and start a containerized instance.

### 2\. Prepare the Database

Navigate to the source directory and run the database migrations.

```bash
cd src
python3 tools/database.py
```

This script will set up the necessary tables in your PostgreSQL database.

### 3\. Launch the Web Application

Start the web server using the `adk` command-line tool.

```bash
# (Ensure you are still in the src directory or that adk is in your PATH)
adk web
```

### 4\. Access the Application

Once the web server is running (it will typically indicate the address and port it's listening on), open your web browser and navigate to: http://localhost:8000
