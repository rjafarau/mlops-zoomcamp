# Simulate remote environment
uv sync

# Start a worker that polls your work pool
uv run --env-file 04-deployment/batch/src/deployments/docker-git/.env \
    prefect worker start --pool docker-pool --type docker

# Create `.prefectignore` and `prefect.yaml` files
uv run --env-file 04-deployment/batch/src/deployments/docker-git/.env \
    prefect init

# Create deployment defined in `prefect.yaml`
uv run --env-file 04-deployment/batch/src/deployments/docker-git/.env \
    prefect deploy -n docker-deployment2 --no-prompt \
    --prefect-file 04-deployment/batch/src/deployments/docker-git/prefect.yaml

# Create deployment using deploy.py
uv run --env-file 04-deployment/batch/src/deployments/docker-git/.env \
    python 04-deployment/batch/src/deployments/docker-git/deploy.py

# Run the deployment with default parameters
uv run --env-file 04-deployment/batch/src/deployments/docker-git/.env \
    prefect deployment run 'run/docker-deployment2'
