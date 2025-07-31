import stripe 
# import uuid
# import boto3
from cfehome.env import config
from django.conf import settings
# from django.core.exceptions import ValidationError
# from botocore.exceptions import ClientError
# from botocore.client import Config
# import b2sdk.v2 as b2


STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default=None)
stripe.api_key=STRIPE_SECRET_KEY

def product_sales_pipeline(product_name="Test product",product_price=1000):
  stripe_product_obj=stripe.Product.create(name=product_name)
  stripe_product_id=stripe_product_obj.id
  stripe_price_obj=stripe.Price.create(
    product=stripe_product_id,
    unit_amount=product_price,
    currency="usd"
  )
  stripe_price_id=stripe_price_obj.id
  base_endpoint="http://127.0.0.1:8000"
  success_url=f"{base_endpoint}/purchases/success/"
  cancel_url=f"{base_endpoint}/purchases/stopped/"
  checkout_session=stripe.checkout.Session.create(
    line_items=[
      {
        "price":stripe_price_id,
        "quantity":1,
      }
    ],
    mode="payment",
    success_url=success_url,
    cancel_url=cancel_url
  )
  print(checkout_session.url)
  #return checkout_session.url



# def upload_image_to_b2(file, existing_image=None, bucket_name=settings.B2_BUCKET_NAME):
#     # validate the file
#     if not file.content_type.startswith('image/'):
#         raise ValidationError("File is not an image.")
    
#     try:
#         # Initialize B2 API
#         info = b2.InMemoryAccountInfo()
#         b2_api = b2.B2Api(info)
#         b2_api.authorize_account("production", settings.B2_KEY_ID, settings.B2_APP_KEY)
        
#         # Get bucket
#         bucket = b2_api.get_bucket_by_name(bucket_name)
        
#         # Generate unique filename
#         file_extension = file.name.split('.')[-1]
#         unique_filename = f"{uuid.uuid4()}.{file_extension}"

#         # Delete existing image if present
#         if existing_image:
#             try:
#                 file_version = bucket.get_file_info_by_name(existing_image)
#                 bucket.delete_file_version(file_version.id_, file_version.file_name)
#             except Exception as e:
#                 print(f"Error deleting existing image: {e}")

#         # Upload new file
#         uploaded_file = bucket.upload_bytes(
#             file.read(),
#             unique_filename,
#             content_type=file.content_type
#         )

#         # Generate URL
#         download_url = b2_api.get_download_url_for_file_name(bucket_name, unique_filename)
#         return unique_filename, download_url

#     except Exception as e:
#         print(f"Error in B2 operation: {e}")
#         raise ValidationError(f"Failed to handle image in B2: {str(e)}")
    
# def test_b2_connection():
#     """Test B2 credentials using native B2 API"""
#     import b2sdk.v2 as b2
#     from django.conf import settings
    
#     try:
#         info = b2.InMemoryAccountInfo()
#         b2_api = b2.B2Api(info)
#         b2_api.authorize_account("production", settings.B2_KEY_ID, settings.B2_APP_KEY)
        
#         # List buckets to test connection
#         for bucket in b2_api.list_buckets():
#             print(f'Bucket: {bucket.name}')
            
#         return True, "Connection successful"
#     except Exception as e:
#         return False, f"Connection failed: {str(e)}"