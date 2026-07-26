# Start a worker that polls your work pool
prefect worker start --pool local-pool --type process

# Create `.prefectignore` and `prefect.yaml` files
prefect init

# Deploy the flow to the Prefect server
prefect deploy duration-prediction.py:run --name duration-prediction --pool local-pool

# Or using saved deployment config from `prefect.yaml`
prefect deploy -n duration-prediction

# To deploy all deployments defined in `prefect.yaml`
prefect deploy --all

# Run the deployment with parameters
prefect deployment run run/duration-prediction --param year=2021 --param month=1
