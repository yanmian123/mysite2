from django_redis import get_redis_connection
from django.conf import settings
import json
from django.core.cache import caches
import redis
from django.conf import settings
import logging
import redis
from django.conf import settings
import logging,os

# 获取日志器
logger = logging.getLogger(__name__)

class ArticleViewCounter:
    def __init__(self):
        """
        初始化视图计数器
        不立即建立连接，延迟到第一次使用时
        """
        self.redis_conn = None
        self.connection_attempts = 0
        self.max_retries = 5
        self.retry_delay = 2  # 秒


    # def _ensure_connection(self):
    #     try:
    #         self.redis_conn = redis.Redis(
    #             host=settings.REDIS_HOST,  # 从settings获取
    #             port=6379,
    #             db=0
    #         )
    #         logger.info(f"成功连接到Redis: {settings.REDIS_HOST}:6379")
    #         return self.redis_conn.ping()
    #     except Exception as e:
    #         logger.error(f"Redis连接失败: {str(e)}")
    #         return False
    def _ensure_connection(self):
        """确保Redis连接可用"""
        if self.redis_conn is not None:
            try:
                if self.redis_conn.ping():
                    return True
            except (redis.ConnectionError, redis.TimeoutError):
                self.redis_conn = None
        
        if self.redis_conn is None and self.connection_attempts < self.max_retries:
            try:
                self.redis_conn = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=6379,
                    db=0,
                    socket_connect_timeout=3,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )
                
                if self.redis_conn.ping():
                    logger.info("Redis连接成功")
                    self.connection_attempts = 0
                    return True
                
            except (redis.ConnectionError, redis.TimeoutError) as e:
                self.redis_conn = None
                self.connection_attempts += 1
                logger.warning(f"Redis连接失败 (尝试 {self.connection_attempts}/{self.max_retries}): {str(e)}")
                
                if self.connection_attempts >= self.max_retries:
                    logger.error(f"无法连接到Redis: {settings.REDIS_HOST}:6379")
        return False 

    def increment_views(self, article_id, user_id=None, request=None):
        """
        增加文章浏览量（包括唯一浏览量）
        """
        if not self._ensure_connection():
            return False
        
        # try:
        #     # 使用正确的键名格式
        #     self.redis_conn.zincrby("article_views", 1, str(article_id))
            
        #     # 增加唯一浏览量
        #     unique_key = f"article:{article_id}:unique_views"
        #     if user_id is not None:
        #         identifier = user_id
        #     elif request is not None:
        #         identifier = request.META.get('REMOTE_ADDR', 'unknown')
        #     else:
        #         identifier = 'unknown'
            
        #     self.redis_conn.sadd(unique_key, identifier)
        #     return True
            
        # except Exception as e:
        #     logger.error(f"增加阅读量失败: {str(e)}")
        #     return False
        
        
        try:
            # 使用有序集合存储总阅读量
            self.redis_conn.zincrby("article_views", 1, str(article_id))
            
            # 同时使用字符串键存储当前阅读量（为了兼容sync_views_to_mysql任务）
            views_key = f"article:{article_id}:views"
            current_views = self.redis_conn.get(views_key)
            if current_views:
                self.redis_conn.set(views_key, int(current_views) + 1)
            else:
                self.redis_conn.set(views_key, 1)
            
            # 增加唯一浏览量
            unique_key = f"article:{article_id}:unique_views"
            if user_id is not None:
                identifier = user_id
            elif request is not None:
                identifier = request.META.get('REMOTE_ADDR', 'unknown')
            else:
                identifier = 'unknown'
            
            self.redis_conn.sadd(unique_key, identifier)
            return True
            
        except Exception as e:
            logger.error(f"增加阅读量失败: {str(e)}")
            return False
        
        
    # def get_views(self, article_id):
    #     """
    #     获取文章总浏览量
    #     """
    #     if not self._ensure_connection():
    #         return 0
        
    #     try:
    #         # 使用正确的键名格式
    #         result = self.redis_conn.zscore("article_views", str(article_id))
    #         return int(result) if result else 0
    #     except Exception as e:
    #         logger.error(f"获取浏览量失败: {str(e)}")
    #         return 0
    def get_views(self, article_id):
        """获取文章总浏览量"""
        if not self._ensure_connection():
            return 0
        
        try:
            # 优先从有序集合获取
            result = self.redis_conn.zscore("article_views", str(article_id))
            if result:
                return int(result)
            
            # 回退到字符串键
            views_key = f"article:{article_id}:views"
            result = self.redis_conn.get(views_key)
            return int(result) if result else 0
        except Exception as e:
            logger.error(f"获取浏览量失败: {str(e)}")
            return 0

    def get_unique_views(self, article_id):
        """
        获取文章的唯一浏览量（基于IP或用户ID）
        """
        if not self._ensure_connection():
            logger.error("无法获取唯一浏览量 - Redis连接不可用")
            return 0
        
        try:
            key = f"article:{article_id}:unique_views"
            return self.redis_conn.scard(key)  # 返回集合大小
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.error(f"获取唯一浏览量失败: {str(e)}")
            self.redis_conn = None
            return 0

    def get_top_articles(self, count=5):
        """
        获取最受欢迎的文章
        """
        if not self._ensure_connection():
            logger.error("无法获取热门文章 - Redis连接不可用")
            return []
        
        try:
            return self.redis_conn.zrevrange("article_views", 0, count - 1, withscores=True)
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.error(f"获取热门文章失败: {str(e)}")
            self.redis_conn = None
            return []

    def sync_views_to_db(self):
        """
        将Redis中的浏览量同步到数据库
        """
        if not self._ensure_connection():
            logger.error("无法同步浏览量 - Redis连接不可用")
            return False
        
        try:
            # 获取所有文章和浏览量
            articles = self.redis_conn.zrange("article_views", 0, -1, withscores=True)
            
            from .models import Article  # 延迟导入避免循环依赖
            
            for article_key, views in articles:
                # 解析文章ID (格式: "article:{id}:views")
                article_id = int(article_key.decode().split(":")[1])
                
                try:
                    article = Article.objects.get(id=article_id)
                    article.views = int(views)
                    article.save()
                except Article.DoesNotExist:
                    logger.warning(f"文章不存在: ID={article_id}")
            
            logger.info(f"成功同步 {len(articles)} 篇文章的浏览量到数据库")
            return True
            
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.error(f"同步浏览量失败: {str(e)}")
            self.redis_conn = None
            return False
        except Exception as e:
            logger.exception(f"同步浏览量时发生意外错误: {str(e)}")
            return False

# 创建视图计数器实例
view_counter = ArticleViewCounter()