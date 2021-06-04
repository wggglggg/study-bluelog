from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

#管理员
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    blog_title = db.Column(db.String(60))
    blog_sub_title = db.Column(db.String(100))
    name = db.Column(db.String(30))
    about = db.Column(db.Text)

    # 将明文密码 转成 散列值密码类型
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        return self.password_hash
    #将散列值密码与明文密码对比, 一致拿到True, 不一致False
    def validate_password(self,password):
        return check_password_hash(self.password_hash, password)

#文章的分类  ,分类名称不能重复
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    posts = db.relationship('Post', back_populates='category')#, cascade='all')

    def delete(self):
        default_category = Category.query.get_or_404(1)  # default默认分类Id 是 1
        # 假如有一个分类名为movie,删除movie分类, 在这就变参展了posts = movie.posts, 就是先拿到moive下的所有文章

        posts = self.posts[:]
        for post in posts:
            post.category = default_category  # 将default默认分类的id, 赋值给了movie下的所有文章,也就是转移到了默认分类下
        db.session.delete(self)  #把movie分类删除
        db.session.commit()

#文章
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    name = db.Column(db.String(30))
    slug = db.Column(db.String(128))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    can_comment = db.Column(db.Boolean, default=True)  # 开户评论的回复或者关闭评论,通过布尔值来获取状态
    # can_post_comment = db.Column(db.Boolean, default=True) # 开户文章的评论或者关闭评论,通过布尔值来获取状态
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all')
    # cascade = 'all',  在SALAlchemy中，只要将一条数据添加到session中，和他相关联的数据都可以一起存入和删除。
    # 这其实是通过relationship对象创建时传入关键字参数cascade实现的，叫级联接

#评论
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author =db.Column(db.String(30))
    email = db.Column(db.String(254))
    site = db.Column(db.String(255))
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False)  #收集是否是管理评论返回 布尔值
    reviewed = db.Column(db.Boolean, default=False)    #收集是否过审核评论返回 布尔值
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    #一对多都为自己,所以外键建在自己内
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])
    # remote_side=[id] 标识为另一侧
    replies = db.relationship('Comment', back_populates='replied', cascade='all')

# 分享网站
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    url = db.Column(db.String(255))
