# Create `prefect` namespace
kubectl create namespace prefect

# Add the Prefect Helm repository
# https://docs.prefect.io/v3/how-to-guides/deployment_infra/kubernetes#add-the-prefect-helm-repository
helm repo add prefect https://prefecthq.github.io/prefect-helm
helm repo update

# Generate a default job template for the K8S work pool
uv run --env-file 04-deployment/batch/src/deployments/remote/.env \
    prefect work-pool get-default-base-job-template --type kubernetes >> template.json

# Edit `template.json` manually to add `imagePullSecrets`
# https://docs.prefect.io/v3/advanced/customize-base-job-templates#image-pull-secrets

# Create K8S work pool
# using CLI
uv run --env-file 04-deployment/batch/src/deployments/remote/.env \
    prefect work-pool create \
        --base-job-template 04-deployment/batch/src/deployments/remote/kubernetes/template.json \
        --type kubernetes \
        k8s-pool

# using UI
# https://docs.prefect.io/v3/how-to-guides/deployment_infra/kubernetes#create-a-kubernetes-work-pool

# Create K8S worker using Helm
# https://docs.prefect.io/v3/how-to-guides/deployment_infra/kubernetes#deploy-a-worker-using-helm
helm install prefect-worker prefect/prefect-worker \
    --namespace=prefect \
    -f 04-deployment/batch/src/deployments/remote/kubernetes/values.yaml

# Create K8S secret
# https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-secret-by-providing-credentials-on-the-command-line
export $(cat 04-deployment/batch/src/deployments/remote/.env | xargs) \
&& kubectl create secret docker-registry regcred \
    --docker-server=$DOCKER_SERVER \
    --docker-username=$DOCKER_USERNAME \
    --docker-password=$DOCKER_PASSWORD \
    --docker-email=$DOCKER_EMAIL

# Create deployment defined in `prefect.yaml`
uv run --env-file 04-deployment/batch/src/deployments/remote/.env \
    prefect deploy \
        --prefect-file 04-deployment/batch/src/deployments/remote/kubernetes/prefect.yaml \
        --name k8s-deployment \
        --no-prompt

# Create deployment using `deploy.py`
uv run --env-file 04-deployment/batch/src/deployments/remote/.env \
    python 04-deployment/batch/src/deployments/remote/kubernetes/deploy.py

# Run the deployment with default parameters
uv run --env-file 04-deployment/batch/src/deployments/remote/.env \
    prefect deployment run 'run/k8s-deployment'
