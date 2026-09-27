import os

from prefect import flow
from prefect.docker import DockerImage
from prefect.runner.storage import GitRepository
from prefect_aws import MinIOCredentials

if __name__ == "__main__":
    creds = MinIOCredentials.load("my-minio-creds")

    flow.from_source(
        source=GitRepository(
            url="https://github.com/rjafarau/mlops-zoomcamp.git",
            branch="04-deployment-2",
        ),
        entrypoint="04-deployment/batch/src/flows/score.py:run",
    ).deploy(
        name="docker-deployment2",
        work_pool_name="docker-pool",
        image=DockerImage(
            name="my_image",
            tag="latest",
            dockerfile="Dockerfile",
            context="04-deployment/batch/",
        ),
        push=False,
        parameters={
            "taxi_type": "green",
            "year": 2021,
            "month": 2,
            "model_id": "m-205aad2b19454838af2cfe5644624f7e",
        },
        job_variables={
            "image_pull_policy": "Never",
            "env": {
                "MLFLOW_TRACKING_URI": os.environ["MLFLOW_TRACKING_URI"],
                "MLFLOW_S3_ENDPOINT_URL": os.environ["MLFLOW_S3_ENDPOINT_URL"],
                "AWS_ACCESS_KEY_ID": creds.minio_root_user,
                "AWS_SECRET_ACCESS_KEY": creds.minio_root_password.get_secret_value(),
            },
            "networks": ["mlops-zoomcamp-network"],
        },
    )
