from django.contrib import admin
from .models import LinkInfo  # Import the LinkInfo model
# Register your models here.
@admin.register(LinkInfo)
class LinkInfoAdmin(admin.ModelAdmin):
    pass