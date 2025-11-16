from django.contrib import admin
from . import models

for model_name, model in models.__dict__.items():
    try:
        if isinstance(model, type) and issubclass(model, models.models.Model):
            admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

