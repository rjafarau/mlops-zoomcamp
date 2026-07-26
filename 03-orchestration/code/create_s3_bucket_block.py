import os
import time

from prefect_aws import AwsClientParameters, MinIOCredentials, S3Bucket


def create_minio_creds_block():
    my_minio_creds_obj = MinIOCredentials(
        minio_root_user=os.environ["MINIO_ROOT_USER"],
        minio_root_password=os.environ["MINIO_ROOT_PASSWORD"],
        aws_client_parameters=AwsClientParameters(
            endpoint_url=os.environ["MINIO_ENDPOINT_URL"],
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
