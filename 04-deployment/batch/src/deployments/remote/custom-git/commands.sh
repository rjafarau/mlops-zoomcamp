# Create deployment defined in `prefect.yaml`
uv run --env-file 04-deployment/batch/src/deployments/remote/.env \
    prefect deploy -n custom-git-deployment --no-prompt \
    --prefect-file 04-deployment/batch/src/deployments/remote/custom-git/prefect.yaml

# Create deployment using deploy.py
uv run --env-file 04-deployment/batch/src/deployments/remote/.env \
    python 04-deployment/batch/src/deployments/remote/custom-git/deploy.py

# Run the deployment with default parameters
uv run --env-file 04-deployment/batch/src/deployments/remote/.env \
    prefect deployment run 'run/custom-git-deployment'
