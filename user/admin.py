from django.contrib import admin

# Register your models here.
from user.models import MyUser  # Import the MyUser model
from django.contrib.auth.admin import UserAdmin
@admin.register(MyUser)
class MyUserAdmin(UserAdmin):
    pass