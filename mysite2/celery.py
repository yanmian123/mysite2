import os
from celery.schedules import crontab
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite2.settings')

app = Celery('mysite2')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# 设置定时任务
app.conf.beat_schedule = {
    'sync-views-every-30-seconds': {
        'task': 'article.tasks.sync_article_views_to_db',
        'schedule': 30.0, # 每30秒执行一次
    },
}