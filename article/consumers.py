# article/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.db import IntegrityError #捕获数据库完整性错误
from .models import Article,Comment

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from django.contrib.auth.models import AnonymousUser
        self.article_id = self.scope['url_route']['kwargs']['article_id']
        self.group_name = f'article_{self.article_id}'

        # 仅允许认证用户连接
        if self.scope["user"] == AnonymousUser():
            await self.close(code=4001)# 未授权错误代码
            # 加入文章组
        else:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
            # 发送连接成功消息(仅认证用户)
            await self.send(text_data=json.dumps({
                'type': 'connection',
                'message': f'已连接到文章 {self.article_id} 的实时评论'
            }))
        
        
    async def disconnect(self, close_code):
        # 记录关闭原因（示例）
        if close_code == 4001:
            print(f"用户未授权，关闭连接（文章ID: {self.article_id}）")
        elif close_code != 1000:
            print(f"异常关闭，状态码: {close_code}（文章ID: {self.article_id}）")
        # 离开文章组
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"收到消息: {data}")
        event_type = data.get('type')
        
        if event_type == 'new_comment':
            #提取客户端发送的评论数据
            comment_content=data.get('content')
            parent_comment_id=data.get('parent_comment_id')#可能为None，非回复
            
            #验证必要数据
            if not comment_content:
                await self.send_error("评论内容不能为空")
                return
            #保存评论到数据库
            try:
                #调用异步方法保存评论，并转为异步操作
                new_comment=await sync_to_async(self.save_comment_to_db)(
                    content=comment_content,
                    parent_id=parent_comment_id
                )
            except Article.DoesNotExist:
                await self.send_error("关联的文章不存在")
                return
            except IntegrityError:
                await self.send_error("评论保存失败，请重试")
            except Exception as e:
                await self.send_error(f"服务器错误：{str(e)}")
                return
            # 转发新评论到组,保存成功后，转发评论到组内所有用户
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'new_comment',
                    'content': data['content'],
                    'user': data['user'],
                    'comment_id': new_comment.id, #数据库生成的评论id
                    'parent_comment_id': data.get('parent_comment_id')
                }
            )
            
    # 辅助方法：发送错误消息给客户端
    async def send_error(self,message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

    # 同步方法：保存评论到数据库（被sync_to_async包装）
    def save_comment_to_db(self, content, parent_id=None):
        # 获取当前认证用户（已在connect中验证过非匿名）
        current_user = self.scope["user"]

        # 获取关联的文章（如果文章不存在，会抛出Article.DoesNotExist）
        article = Article.objects.get(id=self.article_id)

        # 处理父评论（如果是回复）
        parent_comment = None
        if parent_id:
            parent_comment = Comment.objects.get(id=parent_id)

        # 创建并保存评论（你的模型类是小写的comment）
        new_comment = Comment.objects.create(
            content=content,
            article=article,  # 关联到当前文章
            author=current_user,  # 帖子作者（这里复用为评论的用户关联，根据你的模型设计）
            user=current_user.username,  # 评论用户的用户名（存字符串）
            parent_comment=parent_comment  # 父评论（可为None）
        )
        return new_comment


    async def new_comment(self, event):
        # 发送评论数据到WebSocket
        await self.send(text_data=json.dumps({
            'type': 'comment',
            'content': event['content'],
            'user': event['user'],
            'comment_id': event['comment_id'],
            'parent_comment_id': event.get('parent_comment_id')
        }))