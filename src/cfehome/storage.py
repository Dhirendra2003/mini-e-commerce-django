# from django.core.files.storage import Storage
# import boto3
# from botocore.client import Config
# from django.conf import settings

# class B2Storage(Storage):
#     def __init__(self):
#         super().__init__()
#         self.client = None
#         self.bucket = settings.B2_BUCKET_NAME
        
#     def _get_client(self):
#         if self.client is None:
#             self.client = boto3.client(
#                 's3',
#                 endpoint_url=settings.B2_ENDPOINT,
#                 aws_access_key_id=settings.B2_KEY_ID,
#                 aws_secret_access_key=settings.B2_APP_KEY,
#                 config=Config(signature_version='s3v4')
#             )
#         return self.client

#     def deconstruct(self):
#         """Make storage serializable for migrations"""
#         return ('cfehome.storage.B2Storage', [], {})

#     def _save(self, name, content):
#         self._get_client().upload_fileobj(
#             content,
#             self.bucket,
#             name,
#             ExtraArgs={'ContentType': content.content_type}
#         )
#         return name

#     def url(self, name):
#         return f"https://f004.backblazeb2.com/file/{self.bucket}/{name}"

#     def exists(self, name):
#         try:
#             self._get_client().head_object(Bucket=self.bucket, Key=name)
#             return True
#         except:
#             return False

#     def delete(self, name):
#         self._get_client().delete_object(Bucket=self.bucket, Key=name)