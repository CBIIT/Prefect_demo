from prefect import task, flow
from src.utils import copy_object_parameter, copy_file_flow, set_s3_session_client

@flow(
    name="Copy an object in S3",
    log_prints=True,
)
def copy_object_s3(
    source_s3_uri: str,
    dst_s3_bucket_folder: str,
) -> str:
    """Copies an object in S3 from source to destination

    Args:
        source_s3_uri (str): Source S3 URI, e.g. s3://my-bucket/obj-to-copy
        dst_s3_bucket_folder (str): Destiantion S3 bucket folder path, e.g. s3://my-bucket/dest-folder/
    """
    copy_parameter = copy_object_parameter(
        url_in_cds=source_s3_uri, dest_bucket_path=dst_s3_bucket_folder
    )
    s3_client = set_s3_session_client()
    transfer_status = copy_file_flow(copy_parameter=copy_parameter, s3_client=s3_client)
    print(f"transfer_status: {transfer_status}")
    return transfer_status
