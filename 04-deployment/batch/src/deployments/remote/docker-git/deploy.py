import os

from prefect import flow
from prefect.docker import DockerImage
from prefect.runner.storage import GitRepository
from prefect_aws import AwsCredentials

if __name__ == "__main__":
    creds = AwsCredentials.load("my-aws-creds")

    flow.from_source(
        source=GitRepository(
            url="https://github.com/rjafarau/mlops-zoomcamp.git",
            branch="main",
        ),
        entrypoint="04-deployment/batch/src/flows/score.py:run",
    ).deploy(
        name="docker-git-deployment",
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
                "AWS_ACCESS_KEY_ID": creds.aws_access_key_id,
                "AWS_SECRET_ACCESS_KEY": creds.aws_secret_access_key.get_secret_value(),
                "AWS_DEFAULT_REGION": creds.region_name,
            },
            "networks": ["mlops-zoomcamp-network"],
            "auto_remove": True,
        },
    )
