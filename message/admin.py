from django.contrib import admin
from .models import message  # Import the message model
# Register your models here.
@admin.register(message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user','name', 'content', 'email', 'created_time')
    list_filter = ('name', 'email')
    search_fields = ('name', 'email','content')
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            # 假设你只想显示年龄大于 18 岁的用户
            kwargs["queryset"] = db_field.related_model.objects.filter(age__gt=18)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)