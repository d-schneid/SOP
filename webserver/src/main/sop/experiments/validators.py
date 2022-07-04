import os
from django.core.exceptions import ValidationError

valid_extensions = ['.py']

def validate_file_extension(value):
    extension = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if not extension.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Only .py files are supported.')