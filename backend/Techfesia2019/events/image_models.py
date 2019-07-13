import os

from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
from .models import Event


class BaseUploadModel(models.Model):
    """
    Contains info to be inherited by children. Abstract model
    """
    purpose = models.CharField(max_length=100)
    event = models.ForeignKey(to=Event, on_delete=models.CASCADE, null=True, blank=True)
    upload_picture_path = models.CharField(max_length=250)
    upload_logo_path = models.CharField(max_length=250)
    forced_filename = models.CharField(max_length=80, null=True, blank=True)
    additional_info = models.TextField(null=True, blank=True)
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.upload_picture_path[0] == '/':
            raise ValidationError({
                'upload_path': "Absolute paths are not allowed. "
                               "If you are passing relative paths, remove the preceding '/'"
            })

        if self.upload_logo_path[0] == '/':
            raise ValidationError({
                'upload_path': "Absolute paths are not allowed. "
                               "If you are passing relative paths, remove the preceding '/'"
            })

    class Meta:
        abstract = True


def set_file_upload_picture_path(instance, filename):
    if instance.forced_filename:
        ext = os.path.splitext(filename)[1]
        return os.path.join(instance.upload_picture_path, instance.forced_filename + ext)
    else:
        return os.path.join(instance.upload_picture_path, filename)


def set_file_upload_logo_path(instance, filename):
    if instance.forced_filename:
        ext = os.path.splitext(filename)[1]
        return os.path.join(instance.upload_logo_path, instance.forced_filename + ext)
    else:
        return os.path.join(instance.upload_logo_path, filename)


class FileUploadModel(BaseUploadModel):
    """
    A common model to keep track of all uploads
    """
    uploaded_file = models.FileField(upload_to=set_file_upload_picture_path)


class ImageUploadModel(BaseUploadModel):
    """
    Specialized to upload images
    """
    uploaded_picture = models.ImageField(upload_to=set_file_upload_picture_path)
    uploaded_logo = models.ImageField(upload_to=set_file_upload_logo_path)
