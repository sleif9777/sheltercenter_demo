import os

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = "sheltercenter-demo"
AWS_S3_ENDPOINT_URL = "https://nyc3.digitaloceanspaces.com/"
AWS_LOCATION = "https://sheltercenter-demo.nyc3.digitaloceanspaces.com/"

DEFAULT_FILE_STORAGE = 'demo.cdn.backends.MediaRootS3Boto3Storage'
STATICFILES_STORAGE = 'demo.cdn.backends.StaticRootS3Boto3Storage'
