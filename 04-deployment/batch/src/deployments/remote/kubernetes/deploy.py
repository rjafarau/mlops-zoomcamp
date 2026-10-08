import os
import subprocess

from prefect import flow
from prefect.docker import DockerImage
from prefect.runner.storage import GitRepository
from prefect_aws import MinIOCredentials


def get_commit_hash() -> str:
    return (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .decode()
        .strip()
    )


if __name__ == "__main__":
    creds = MinIOCredentials.load("my-minio-creds")
    commit_hash = get_commit_hash()

    flow.from_source(
        source=GitRepository(
            url="https://github.com/rjafarau/mlops-zoomcamp.git",
            branch="main",
        ),
        entrypoint="04-deployment/batch/src/flows/score.py:run",
    ).deploy(
        name="k8s-deployment",
        tags=["k8s", commit_hash],
        work_pool_name="k8s-pool",
        image=DockerImage(
            name=os.environ["DOCKER_IMAGE_NAME"],
            tag=commit_hash,
            dockerfile="Dockerfile",
            context="04-deployment/batch/",
        ),
        parameters={
            "taxi_type": "green",
            "year": 2021,
            "month": 2,
            "model_id": "m-205aad2b19454838af2cfe5644624f7e",
        },
        job_variables={
            "image_pull_policy": "IfNotPresent",
            "image_pull_secrets": [{"name": "regcred"}],
            "env": {
                "MLFLOW_TRACKING_URI": os.environ["MLFLOW_TRACKING_URI"],
                "MLFLOW_S3_ENDPOINT_URL": os.environ["MLFLOW_S3_ENDPOINT_URL"],
                "AWS_ACCESS_KEY_ID": creds.minio_root_user,
                "AWS_SECRET_ACCESS_KEY": creds.minio_root_password.get_secret_value(),
            },
        },
    )
