# SmartHub DevOps

## How to run
1. Clone this repo
2. Copy .env.example to .env
3. Run `docker compose up --build -d`
4. Open http://localhost:3000

## Services
| Service | Port |
|---------|------|
| Frontend | 3000 |
| Backend API | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| RabbitMQ | 5672 |
| ChromaDB | 8002 |

## Tech Stack
- Docker + Docker Compose
- FastAPI Python backend
- Nginx reverse proxy
- PostgreSQL, Redis, RabbitMQ, ChromaDB
