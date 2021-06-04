from flask import Flask, render_template
from config import config
from app.blueprints.auth import auth_bp
from app.blueprints.blog import blog_bp
from app.blueprints.admin import admin_bp
from app.extensions import bootstrap, db, mail, moment, ckeditor, login_manager, csrf, migrate
from app.models import Admin, Category, Post, Comment, Link
from flask_login import current_user


import os, click

# 初始化, 将第三方插件与app捆绑
def create_app(config_name=None):
    #如果没有配置config_name模式
    if config_name is None:
        config_name = os.getenv('FLAKS_CONFIG', 'development')
    # print(config_name)
    app = Flask(__name__)
    app.config.from_object(config[config_name])


    register_logging(app)  #注册日志处理器
    register_blueprint(app) #注册蓝本
    register_extensions(app) #注册扩展
    register_shell_context(app) #注册shell 上下文处理器
    register_template_context(app) #注册模板 上下文处理器
    register_errors(app)  #注册错误处理器
    register_commands(app)  #注册自定义shell命令
    return app

def register_blueprint(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(blog_bp)




#日志处理器
def register_logging(app):
       pass

#蓝本
def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    ckeditor.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db=db)






#shell 上下文处理器
def register_shell_context(app):  #这个 shell 上下文处理器函数返回一个字典，包含数据库实例和模型。
    @app.shell_context_processor   #除了默认导入的 app 之外，flask shell 命令将自动把这些对象导入shell。
    def make_shell_context():
        return dict(db=db,Admin=Admin, Post=Post, Category=Category, Comment=Comment)

#模板上下文处理器
def register_template_context(app):
    @app.context_processor
    def make_template_context():  # base.html基模板需要的变量在这里生成
        admin = Admin.query.first()  #查到所有Admin记录, 只返回第一行first, 分栏右边显示
        categories = Category.query.order_by(Category.name).all()  #查询所有的分类按名称排序 右边显示
        links = Link.query.all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(admin=admin, categories=categories, links=links, unread_comments=unread_comments)

#错误处理器
def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

#自定义shell命令
# 调用 工具(生成虚拟数据)
def register_commands(app):
    @app.cli.command()
    @click.option('--category', default=10, help='分类默认10条')
    @click.option('--post', default=50, help='文章默认50条')
    @click.option('--comment', default=500, help='评论默认500条')

    def forge(category, post, comment):
        from app.fakes import fake_admin, fake_posts,fake_comments, fake_categorys, fake_link

        # db.drop_all()
        # db.create_all()
        click.echo('生成管理员admin虚拟数据')
        fake_admin()

        click.echo('#生成分类虚拟数据 %d 条'% category)
        fake_categorys(category)

        click.echo('#生成虚拟文章 %d 条' % post)
        fake_posts(post)

        click.echo('#生成虚拟评论 %d' % comment)
        fake_comments(comment)

        click.echo('生成Link信息')
        fake_link()

        click.echo('生成过程结束')

    @app.cli.command()
    @click.option('--username', prompt=True, help='建立用户名')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='输入密码')

    def init(username, password):

        click.echo('重建数据库')
        db.create_all()

        admin = Admin.query.first()  #查看是否有admin管理员
        if admin:
            click.echo('已经管理员记录')
            admin.username = username
            admin.set_password(password)

        else:
            click.echo('新建管理员')
            admin = Admin(username=username,
                          blog_title='Bluelog',
                          blog_sub_title="No, i`m the real thing.",
                          name='Admin',
                          about='我的地盘我做主'
                          )

        # admin = Admin(username=username,
        #                blog_title='Suisenlog',
        #                blog_sub_title="No car",
        #                name='Admin',
        #                about='Busy these days'
        #               )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first() #在数据库中查看是否存有一个分类名称
        if category is None:
            click.echo('建立分类, 名称为Default')
            category = Category(name="Default")
            db.session.add(category)

        db.session.commit()
        click.echo('结束')

    @app.cli.command()
    @click.option('--drop', help='drop删除表,再新建空表')
    def initdb(drop):
        if drop:
            click.echo('drop删除表,你要继续吗?', abort=True)
            db.drop_all()
            click.echo('数据库表删除结束 ')

        click.echo('开始新建表')
        db.create_all()
        click.echo('新建表完成')

