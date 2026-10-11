import os
import time

from prefect_aws import AwsClientParameters, AwsCredentials, S3Bucket


def create_aws_creds_block():
    my_aws_creds_obj = AwsCredentials(
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_DEFAULT_REGION"],
        aws_client_parameters=AwsClientParameters(
            endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"],
        ),
    )
    my_aws_creds_obj.save(
        name="my-aws-creds",
        overwrite=True,
    )


def create_s3_bucket_block():
    my_s3_bucket_obj = S3Bucket(
        bucket_name="test",
        credentials=AwsCredentials.load("my-aws-creds"),
    )
    my_s3_bucket_obj.save(
        name="s3-bucket-example",
        overwrite=True,
    )


if __name__ == "__main__":
    create_aws_creds_block()
    time.sleep(5)
    create_s3_bucket_block()
