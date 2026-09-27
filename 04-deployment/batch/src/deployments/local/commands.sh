# Start a worker that polls your work pool
prefect worker start --pool local-pool --type process

# Create `.prefectignore` and `prefect.yaml` files
prefect init

# Create deployment defined in `prefect.yaml`
prefect deploy -n local-deployment --no-prompt \
    --prefect-file 04-deployment/batch/src/deployments/local/prefect.yaml

# Create deployment using deploy.py
python 04-deployment/batch/src/deployments/local/deploy.py

# Run the deployment with default parameters
prefect deployment run 'run/local-deployment'
