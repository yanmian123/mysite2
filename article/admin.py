from django.contrib import admin
from .models import ArticleType,Article,comment  # Import the ArticleType model

# Register your models here.


def make_published(modeladmin, request, queryset):
    queryset.update(status='published')
make_published.short_description = "将选中的文章标记为已发布"

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'type', 'create_time', 'reads')
    list_filter = ('type', 'create_time')
    search_fields = ('title', 'abstract', 'content')
    actions = [make_published]
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            # 假设你只想显示 is_staff 为 True 的用户
            kwargs["queryset"] = db_field.related_model.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(ArticleType)
class ArticleTypeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user')

@admin.register(comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'author', 'user', 'create_time')