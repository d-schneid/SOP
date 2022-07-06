from django.contrib import admin

from experiments.models import Algorithm, Dataset

admin.site.register(Algorithm)
admin.site.register(Dataset)
