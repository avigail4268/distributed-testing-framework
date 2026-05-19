# Distributed Automation Testing System 🚀

A highly scalable, distributed testing framework using a microservices' architecture. This system manages and executes concurrent web automation tests across multiple isolated Docker containers, centrally controlled by a FastAPI backend.

**Author:** Avigail Musai (B.Sc. Software Engineering, Year 4, Semester B)

## 🏗️ Architecture Overview

This project implements a complete 3-Tier Architecture:
1. **Management API Server (FastAPI):** Acts as the orchestrator, managing the queue of tasks and listening for results.
2. **Worker Nodes (Docker + Selenium):** Independent worker containers that dynamically fetch tasks from the server, run headless browser automation, and post results back.
3. **Database (SQLite + SQLAlchemy):** A relational database storing task queues, execution statuses (`PENDING`, `IN_PROGRESS`, `COMPLETED`), and historical run metrics.

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Uvicorn
* **Database:** SQLite, SQLAlchemy (ORM), Pandas (for data analytics)
* **Automation:** Selenium WebDriver, ChromeDriverManager
* **DevOps & Containerization:** Docker, Docker Compose

## ⚙️ How It Works

1. The central server initializes a database (`tasks.db`) and populates the task queue.
2. Multiple Dockerized workers are spun up concurrently using Docker Compose.
3. Workers query the `/get-task` endpoint to receive dynamic instructions.
4. Each worker executes a headless UI test based on the task parameters.
5. Upon completion, workers send test metadata (duration, status) to the `/submit-result` endpoint.
6. The analytics script queries the database via SQL to generate system-wide performance reports.

## 🚀 Running the Project Locally

### 1. Start the Central Server
```bash
python manager_server.py