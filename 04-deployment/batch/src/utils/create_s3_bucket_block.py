import os
import time

from prefect_aws import AwsClientParameters, MinIOCredentials, S3Bucket


def create_minio_creds_block():
    my_minio_creds_obj = MinIOCredentials(
        minio_root_user=os.environ["AWS_ACCESS_KEY_ID"],
        minio_root_password=os.environ["AWS_SECRET_ACCESS_KEY"],
        aws_client_parameters=AwsClientParameters(
            endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"],
        ),
    )
    my_minio_creds_obj.save(
        name="my-minio-creds",
        overwrite=True,
    )


def create_s3_bucket_block():
    my_s3_bucket_obj = S3Bucket(
        bucket_name="test",
        credentials=MinIOCredentials.load("my-minio-creds"),
    )
    my_s3_bucket_obj.save(
        name="s3-bucket-example",
        overwrite=True,
    )


if __name__ == "__main__":
    create_minio_creds_block()
    time.sleep(5)
    create_s3_bucket_block()
