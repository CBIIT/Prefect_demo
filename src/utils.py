import boto3
from botocore.exceptions import ClientError
import os
from botocore.config import Config
from prefect import task, flow
from urllib.parse import urlparse
import json
from prefect import get_run_logger

def set_s3_session_client():
    """This method sets the s3 session client object
    to either use localstack for local development if the
    LOCALSTACK_ENDPOINT_URL variable is defined
    """
    localstack_endpoint = os.environ.get("LOCALSTACK_ENDPOINT_URL")
    if localstack_endpoint != None:
        AWS_REGION = "us-east-1"
        AWS_PROFILE = "localstack"
        ENDPOINT_URL = localstack_endpoint
        boto3.setup_default_session(profile_name=AWS_PROFILE)
        s3_client = boto3.client(
            "s3", region_name=AWS_REGION, endpoint_url=ENDPOINT_URL
        )
    else:
        # Create a custom retry configuration
        custom_retry_config = Config(
            connect_timeout=300,
            read_timeout=300,
            retries={
                "max_attempts": 5,  # Maximum number of retry attempts
                "mode": "standard",  # Retry on HTTP status codes considered retryable
            },
        )
        s3_client = boto3.client("s3", config=custom_retry_config)
    return s3_client


def parse_file_url(url: str) -> tuple:
    """Parse an s3 uri into bucket name and key"""
    # add s3:// if missing
    if not url.startswith("s3://"):
        url = "s3://" + url
    else:
        pass
    parsed_url = urlparse(url)
    bucket_name = parsed_url.netloc
    object_key = parsed_url.path
    # this is in case url is only bucket name, such as s3://my-bucket
    if object_key == "":
        object_key = "/"
    else:
        pass
    if object_key[0] == "/":
        object_key = object_key[1:]
    else:
        pass
    return bucket_name, object_key


def copy_object_parameter(url_in_cds: str, dest_bucket_path: str) -> dict:
    """Returns a dict that can be used as parameter for copy object using s3 client

    Example
    mydict=copy_object_parameter(url_in_cds="s3://ccdi-validation/QL/file2.txt",
        dest_bucket_path="my-source-bucket/new_release")
    Expected Return
    {
        'Bucket': 'my-source-bucket',
        'CopySource': 'ccdi-validation/QL/file2.txt',
        'Key': 'new_release/QL/file2.txt'
    }
    """
    origin_bucket, object_key = parse_file_url(url=url_in_cds)
    if "/" not in dest_bucket_path:
        dest_bucket_path = dest_bucket_path + "/"
    else:
        pass
    if dest_bucket_path.startswith("s3://"):
        dest_bucket_path = dest_bucket_path[5:]
    else:
        pass
    dest_bucket, dest_prefix = dest_bucket_path.split("/", 1)
    copysource = os.path.join(origin_bucket, object_key)
    dest_key = os.path.join(dest_prefix, object_key)
    param_dict = {"Bucket": dest_bucket, "CopySource": copysource, "Key": dest_key}
    return param_dict

@task(
    name="Copy an object file in S3",
    log_prints=True,
)
def copy_file_in_s3(
    copy_parameter: dict, file_size: int, s3_client
):
    """Copy objects between two locations defined by copy_parameter

    This function only works with object less than 5GB
    """
    runner_logger = get_run_logger()
    copy_source = copy_parameter["CopySource"]
    if file_size < 5 * 1024 * 1024 * 1024:
        try:
            s3_client.copy_object(**copy_parameter)
            transfer_status = "Success"
        except ClientError as ex:
            transfer_status = "Fail"
            ex_code = ex.response["Error"]["Code"]
            ex_message = ex.response["Error"]["Message"]
            if ex_code == "NoSuchKey":
                object_name = ex.response["Error"]["Key"]
                runner_logger.error(ex_code + ":" + ex_message + " " + object_name)
            elif ex_code == "NoSuchBucket":
                bucket_name = ex.response["Error"]["Code"]["BucketName"]
                runner_logger.error(
                    ex_code + ":" + ex_message + " Bucket name: " + bucket_name
                )
            else:
                runner_logger.error(
                    "Error info:\n" + json.dumps(ex.response["Error"], indent=4)
                )        
    else:
        runner_logger.error(f"This copy function only works with object less than 5GB. File size {file_size} of {copy_source} exceeds the size limit.")
        transfer_status = "Fail"
    return transfer_status


@flow(
    name="Copy an object file",
    retries=3,
    retry_delay_seconds=0.5,
    log_prints=True,
)
def copy_file_flow(copy_parameter: dict, s3_client) -> str:
    """Copy objects between two locations defined by copy_parameter

    It checks if the file has been transferred (Key and object Content length/size) before trasnfer process
    Function copy_file_in_s3 is executed only if
        - The file hasn't been transferred
        - the destination object size less than 5GB
    """
    copy_source = copy_parameter["CopySource"]
    source_bucket, source_key = copy_source.split("/", 1)
    object_response = s3_client.head_object(Bucket=source_bucket, Key=source_key)
    file_size = object_response["ContentLength"]

    # check if the destination object has been copied or no
    try:
        dest_object = s3_client.head_object(
            Bucket=copy_parameter["Bucket"], Key=copy_parameter["Key"]
        )
        if dest_object["ContentLength"] == file_size:
            print(
                f"File {copy_source} had already been copied to destination bucket path. Skip"
            )
            # runner_logger.info(
            #    f"File {copy_source} had already been copied to destination bucket path. Skip"
            # )
            transfer_status = "Success"
        else:
            # if the destin object size is different from source, copy the object
            transfer_status = copy_file_in_s3(
                copy_parameter=copy_parameter,
                file_size=file_size,
                s3_client=s3_client
            )

    except Exception as ex:
        # if the destin object does not exist, repeat the copy task
        transfer_status = copy_file_in_s3(
            copy_parameter=copy_parameter,
            file_size=file_size,
            s3_client=s3_client,
        )
    return transfer_status
