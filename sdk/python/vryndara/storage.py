import boto3
import os
from botocore.exceptions import NoCredentialsError

class StorageManager:
    def __init__(self, bucket_name="vryndara-assets"):
        self.bucket = bucket_name
        # Connect to local MinIO
        self.s3 = boto3.client('s3',
            endpoint_url='http://localhost:9000',
            aws_access_key_id='admin',
            aws_secret_access_key='password123',
            config=boto3.session.Config(signature_version='s3v4')
        )

    def upload_file(self, file_path, object_name=None):
        """Uploads ANY file type (mp4, blend, fbx) to storage."""
        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            print(f"    [Storage] Uploading {object_name}...")
            self.s3.upload_file(file_path, self.bucket, object_name)
            
            # Generate a link (accessible by other agents)
            url = f"http://localhost:9000/{self.bucket}/{object_name}"
            print(f"    [Storage] Success: {url}")
            return url
        except Exception as e:
            print(f"    [Storage] Upload Failed: {e}")
            return None

    def download_file(self, object_name, dest_path):
        """Downloads a file from storage to local disk."""
        try:
            self.s3.download_file(self.bucket, object_name, dest_path)
            return True
        except Exception as e:
            print(f"    [Storage] Download Failed: {e}")
            return False