# Simulate remote environment
uv sync

# Start a worker that polls your work pool
uv run --env-file 04-deployment/batch/src/deployments/remote/.env \
    prefect worker start --pool docker-pool --type docker

# Create `.prefectignore` and `prefect.yaml` files
uv run --env-file 04-deployment/batch/src/deployments/remote/.env \
    prefect init
