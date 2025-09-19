from celery import shared_task
from django_redis import get_redis_connection
from .models import Article
from .utils import view_counter
import logging

logger = logging.getLogger(__name__)

@shared_task
def sync_article_views_to_db():
    """将Redis中的阅读量同步到MySQL数据库"""
    redis_conn = get_redis_connection("default")
    
    try:
        # 获取所有文章的阅读量
        all_views = redis_conn.zrange("article_views", 0, -1, withscores=True)
        
        for article_id_bytes, views in all_views:
            article_id = int(article_id_bytes.decode())
            views_count = int(views)
            
            try:
                # 更新数据库
                Article.objects.filter(id=article_id).update(reads=views_count)
                logger.info(f"已同步文章 {article_id} 的阅读量: {views_count}")
            except Article.DoesNotExist:
                logger.warning(f"文章 {article_id} 不存在，跳过同步")
        
        logger.info(f"阅读量同步完成，共处理 {len(all_views)} 篇文章")
        
    except Exception as e:
        logger.error(f"同步阅读量时发生错误: {e}")

@shared_task
def increment_article_views(article_id, user_id=None):
    logger.info(f"开始增加文章阅读量: article_id={article_id}, user_id={user_id}")
    try:
        view_counter.increment_views(article_id, user_id)
        logger.info(f"阅读量增加成功: article_id={article_id}")
    except Exception as e:
        logger.error(f"增加阅读量失败: {str(e)}")

# from django.db import transaction

# @shared_task
# def sync_views_to_mysql():
#     """
#     将Redis中的阅读量同步到MySQL数据库
#     """
#     try:
#         redis_conn = get_redis_connection("default")
        
#         # 获取所有文章在Redis中的阅读量
#         article_keys = redis_conn.keys("article:*:views")
        
#         with transaction.atomic():
#             for key in article_keys:
#                 # 从键名中提取文章ID
#                 article_id = int(key.decode().split(':')[1])
#                 views = int(redis_conn.get(key) or 0)
                
#                 # 更新数据库中的阅读量
#                 Article.objects.filter(id=article_id).update(reads=views)
                
#         logger.info("成功同步阅读量数据到MySQL")
        
#     except Exception as e:
#         logger.error(f"同步阅读量到MySQL时出错: {e}")