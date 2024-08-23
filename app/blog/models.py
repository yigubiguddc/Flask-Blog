from datetime import datetime
from RealProject import db
from sqlalchemy.dialects.mysql import LONGTEXT
from enum import IntEnum


# 基类，有抽象__abstract__ = True，不会自动创建独立的表格
class BaseModel(db.Model):
    __abstract__ = True

    add_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, )    # 创建时间utc比北京时间慢8个小时
    pub_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)    # 更新时间


class PostPublishType(IntEnum):
    draft = 1       # 草稿
    show = 2        # 发布页


class Category(BaseModel):
    id = db.Column(db.Integer, primary_key=True)    # 主键
    name = db.Column(db.String(128), nullable=False)
    icon = db.Column(db.String(128), nullable=True)
    # 文章分类(Category)和文章(Post)是一对多的关系
    # post = db.relationship('Post', backref='category', lazy=True)
    post = db.relationship('Post', back_populates="category", cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return '<Category %r>' % self.name


# 遵守PEP 8代码风格，注意可读性
# 创建多对多关系帮助器,都是主键
tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
                db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True))


# 文章
class Post(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)   # 标题
    desc = db.Column(db.String(200), nullable=True)     # 描述description
    content = db.Column(LONGTEXT, nullable=False)       # LONGTEXT是长文本，要单独引入
    # 指定了一个外键约束，将 Post 模型中的 category_id 列与 Category 模型中的 id 列关联起来
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete="CASCADE"), nullable=False)
    has_type = db.Column(db.Enum(PostPublishType), server_default='show', nullable=False)
    # 多对多关系
    tags = db.relationship('Tag', secondary=tags, lazy='subquery', backref=db.backref('post', lazy=True))
    category = db.relationship("Category", back_populates="post")
    # cascade定义了在父对象被删除时如何处理与之相关的子对象，这里时all, delete表明Post的对象被删时级联删除所有comment
    comment = db.relationship('Comment', back_populates="post", cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return '<Post %r>' % self.title


# 文章标签
class Tag(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return self.name


#  添加评论功能
class Comment(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    user = db.relationship("User", back_populates="comment")
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)
    post = db.relationship("Post", back_populates="comment")
