# Create deployment defined in `prefect.yaml`
uv run --env-file 04-deployment/batch/src/deployments/remote/.env \
    prefect deploy -n docker-git-deployment --no-prompt \
    --prefect-file 04-deployment/batch/src/deployments/remote/docker-git/prefect.yaml

# Create deployment using deploy.py
uv run --env-file 04-deployment/batch/src/deployments/remote/.env \
    python 04-deployment/batch/src/deployments/remote/docker-git/deploy.py

# Run the deployment with default parameters
uv run --env-file 04-deployment/batch/src/deployments/remote/.env \
    prefect deployment run 'run/docker-git-deployment'
