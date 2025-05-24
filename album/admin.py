from django.contrib import admin
from .models import Albuminfo

# Register your models here.
@admin.register(Albuminfo)
class AlbumInfoAdmin(admin.ModelAdmin):
    pass