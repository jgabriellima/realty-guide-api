README.md
markdown
Copy code
# MyProject

This project uses FastAPI and TaskIQ with RabbitMQ as the broker to create asynchronous tasks. The project can run either as an API server or a worker, depending on the `MODE` environment variable. Logs are sent to PostHog for analysis.

## Setup

### Requirements

- Docker
- Docker Compose
- RabbitMQ instance
- PostHog instance

### Environment Variables

Environment variables are managed using a `.env` file for local development or directly via the environment for production.

- `MODE`: Set to `api` to run the FastAPI server or `worker` to run the TaskIQ worker.
- `APP_NAME`: Application name.
- `DEFAULT_LARGE_MODEL`: Default large model name.
- `SUPABASE_URL`: Supabase URL.
- `SUPABASE_KEY`: Supabase key.
- `SUPABASE_BUCKET_NAME`: Supabase bucket name.
- `SENTRY_DSN`: Sentry DSN.
- `FIRECRAWL_API_KEY`: Firecrawl API key.
- `BROKER_URL`: RabbitMQ broker URL.
- `POSTHOG_API_KEY`: Your PostHog API key.
- `POSTHOG_HOST`: Your PostHog host URL.

### Build Docker Image

```sh
docker-compose build
Running the API Server and Worker with Live Reload
To run the API server and worker with live reload during development:

sh
Copy code
docker-compose up
Endpoints
Run Task
To run a task, send a POST request to /run-task/ with a parameter:

sh
Copy code
curl -X POST "http://localhost:8000/run-task/" -H "Content-Type: application/json" -d '{"param": "example"}'
Run Task and Wait for Result
To run a task and wait for the result, send a POST request to /run-task-and-wait/ with a parameter:

sh
Copy code
curl -X POST "http://localhost:8000/run-task-and-wait/" -H "Content-Type: application/json" -d '{"param": "example"}'
Logs
Logs are stored in the logs/app.log file and sent to PostHog for analysis.


celery --broker=amqp://8UlPsLtMcWdaewff:stbrP5Uduu8LJa7C1wv9n5Y_naaANfeu@viaduct.proxy.rlwy.net:22121 flower --port=5555


RAILWAY_APP_TOKEN=9697b21b-83e3-4805-8deb-a25a4be8e8a7

RAILWAY_APP_SERVICE_ID_API=5b362d51-b4b3-4665-912f-724a55f209c0
RAILWAY_APP_SERVICE_ID_WORKER=06126a0c-03b0-408e-87bf-175aeb23893a

