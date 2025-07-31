import boto3
import mimetypes
from copy import Error

from django.http import FileResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from botocore.client import Config
from botocore.exceptions import ClientError
from django.core.exceptions import ValidationError  # Use Django's ValidationError
from .utils import upload_image_to_b2


# Create your views here.
from .forms import ProductForm, ProductUpdateForm, ProductAttachmentInlineFormSet
from .models import Product, ProductAttachment


def product_create_view(request):
    context = {}
    form = ProductForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        if request.user.is_authenticated:
            obj.user = request.user
            obj.save()
            return redirect(obj.get_manage_url())
        form.add_error(None, "Your must be logged in to create products.")
    context['form'] = form
    return render(request, 'products/create.html', context)

def product_list_view(request):
    object_list = Product.objects.all()
    return render(request, "products/list.html", {"object_list": object_list})



def product_manage_detail_view(request, handle=None):
    obj = get_object_or_404(Product, handle=handle)
    attachments = ProductAttachment.objects.filter(product=obj)
    is_manager = False
    if request.user.is_authenticated:
        is_manager = obj.user == request.user
    context = {"object": obj}
    if not is_manager:
        return HttpResponseBadRequest()
    form = ProductUpdateForm(request.POST or None, request.FILES or None, instance=obj)
    formset = ProductAttachmentInlineFormSet(request.POST or None, 
                                             request.FILES or None,queryset=attachments)
    if form.is_valid() and formset.is_valid():
        instance = form.save(commit=False)
        # Handle main product image upload
        if 'image' in request.FILES:
            try:
                filename, url = upload_image_to_b2(
                    request.FILES['image'],
                    existing_image=instance.image.name if instance.image else None
                )
                instance.image = filename
            except ValidationError as e:
                form.add_error('image', str(e))
                return render(request, 'products/manager.html', context)
        
        instance.save()
        formset.save(commit=False)
        # Handle attachment uploads
        for _form in formset:
            is_delete = _form.cleaned_data.get('DELETE')
            try:
                attachment_obj = _form.save(commit=False)
                if attachment_obj and not is_delete:
                    if 'file' in _form.changed_data:
                        filename, url = upload_image_to_b2(
                            _form.cleaned_data['file'],
                            existing_image=attachment_obj.file.name if attachment_obj.file else None
                        )
                        attachment_obj.file = filename
                    attachment_obj.product = instance
                    attachment_obj.save()
                elif attachment_obj and is_delete and attachment_obj.pk:
                    attachment_obj.delete()
            except ValidationError as e:
                _form.add_error('file', str(e))
                context.update({
                    'form': form,
                    'formset': formset,
                    'error': str(e)
                })
                return render(request, 'products/manager.html', context)
                
        return redirect(obj.get_manage_url())
    context['form'] = form
    context['formset'] = formset
    return render(request, 'products/manager.html', context)

def product_detail_view(request, handle=None):
    obj = get_object_or_404(Product, handle=handle)
    attachments = ProductAttachment.objects.filter(product=obj)
    # attachments = obj.productattachment_set.all()
    is_owner = False
    if request.user.is_authenticated:
        is_owner = request.user.purchase_set.all().filter(product=obj,completed=True).exists() # verify ownership
    context = {"object": obj, "is_owner": is_owner, "attachments": attachments}
    return render(request, 'products/detail.html', context)

# def product_attachment_download_view(request, handle=None, pk=None):
#     attachment = get_object_or_404(ProductAttachment, product__handle=handle, pk=pk)
#     can_download = attachment.is_free or False
#     if request.user.is_authenticated:
#         can_download = True # check ownership
#     if can_download is False:
#         return HttpResponseBadRequest()
#     file = attachment.file.open(mode='rb') # cdn -> S3 object storage
#     filename = attachment.file.name
#     content_type, _ = mimetypes.guess_type(filename)
#     response =  FileResponse(file)
#     response['Content-Type'] = content_type or 'application/octet-stream'
#     response['Content-Disposition'] = f'attachment;filename={filename}'
#     return response

def product_attachment_download_view(request, handle=None, pk=None):
    # Get attachment or 404
    attachment = get_object_or_404(ProductAttachment, product__handle=handle, pk=pk)
    
    # Check download permissions
    can_download = attachment.is_free
    if request.user.is_authenticated:
        can_download = can_download or request.user.purchase_set.filter(
            product=attachment.product,
            completed=True
        ).exists()
    
    if not can_download:
        return HttpResponseBadRequest("Purchase required to download this file")
    
    # Get file from B2
    try:
        # Initialize B2 client
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.B2_ENDPOINT,
            aws_access_key_id=settings.B2_KEY_ID,
            aws_secret_access_key=settings.B2_APP_KEY,
            config=Config(signature_version='s3v4')
        )
        
        # Get file from B2
        file_obj = s3_client.get_object(
            Bucket=settings.B2_BUCKET_NAME,
            Key=attachment.file.name
        )
        
        # Prepare response
        content_type = file_obj.get('ContentType', 'application/octet-stream')
        filename = attachment.file.name.split('/')[-1]
        
        response = FileResponse(
            file_obj['Body'],
            as_attachment=True,
            filename=filename
        )
        response['Content-Type'] = content_type
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except ClientError as e:
        print(f"B2 download error: {str(e)}")  # Log the error
        return HttpResponseBadRequest("File not found or not accessible")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Log other errors
        return HttpResponseBadRequest("Error processing download request")