import random
from sqlite3 import IntegrityError

from app.extensions import db
from app.models import Admin, Category, Post, Comment, Link
from faker import Faker


fake = Faker()

#生成admin虚拟数据
def fake_admin():
    admin = Admin(
        username='wggglggg',
        blog_title='Bluelog',
        blog_sub_title='No, I`m the real thing',
        name='admin',
        about='Um, I`m Wggglggg_admin, had a fun time as a member of CHAM..'
        )
    admin.password_hash = "pbkdf2:sha256:260000$DLhY2Dzx6YMFthlR$dfcdb2a6d95f5dc5788ce5f8ef2eba8ffcb2403a0f50a02ede86a3464fb38752"
    db.session.add(admin)
    db.session.commit()

#生成分类 虚拟数据
def fake_categorys(count=10):
    #默认是 统一默认的分类
    category = Category(name='Default')
    db.session.add(category)

    #生成10条分类
    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        #如果有同名的分类会报错,所以用try来忽略,在db里有设置unique来预防同名
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()  #出现同名回滚session,不然后面都会报错


#生成虚拟文章
def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),  #虚拟标题
            name=fake.name(),      # 生成文章作者
            body=fake.text(2000),   #虚拟文章内容
            can_comment=True,
            # 使第一篇文章都有一个随机的分类
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)

    db.session.commit()

#生成虚拟评论
def fake_comments(count=500):
    # 过审的评论500条随机与文章Post的id挂钩
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    # 生成未过审50条
    apple = int(count*0.1) #  未审核数量
    for i in range(apple):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    #生成管理发表的评论50条
    for i in range(apple):
        comment = Comment(
            author='Wggglggg_admin',
            email='wggglggg@hotmail.com',
            site='op.wggglgggdns.top',
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            from_admin=True,
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    #生成随机回复50条
    for i in range(apple):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count())),
            replied=Comment.query.get(random.randint(1, Comment.query.count()))
        )
        db.session.add(comment)



    db.session.commit()

def fake_link():
    facebook = Link(name='Facebook', url='#')
    google = Link(name='Google', url='#')
    twitter = Link(name='Twitter', url='#')
    baidu = Link(name='Baidu', url='#')
    db.session.add_all([facebook, google, twitter, baidu])
    db.session.commit()