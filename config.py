import os


basedir = os.path.abspath(os.path.dirname(__file__)) #拿到了config.py的完整路径

class BaseConfig(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 邮件配置
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Bluelog Admin', MAIL_USERNAME)

    # 分页配置
    BLUELOG_POST_PER_PAGE = 5
    BLUELOG_COMMENT_PER_PAGE = 10
    BLUELOG_EMAIL = 'wggglggg@hotmail.com'
    BLUELOG_MANAGE_POST_PER_PAGE = 10
    BLUELOG_MANAGE_COMMENT_PER_PAGE = 10


    # 页面主题{'主题名称' : '显示名称'}
    BLUELOG_THEMES = {'perfect_blue': 'Perfect Blue', 'black_swan': 'Black Swan', 'my_black': 'My Black'}




class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.environ.get('DATABASE_URL'), 'bluelog-dev.db')

class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  #测试数据库在内存中

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.environ.get('DATABASE_URL'), 'bluelog.db')

config = {
    'development' : DevelopmentConfig,
    'testing' : TestingConfig,
    'production' : ProductionConfig
}