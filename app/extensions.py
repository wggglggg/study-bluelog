from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

bootstrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()
ckeditor = CKEditor()
moment = Moment()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()


# 登录提示, 如果路由函数上面有@login_required,先到按下面设置流程来动作
# 一 直接跳到登录页面
login_manager.login_view = 'auth.login'
# 二 提示为警告类型(可选)
login_manager.login_message_category = 'warning'
# 三 警告提示信息(可选)
login_manager.login_message = '浏览此页面需先登录'


# 登录验证, 当使用current_user时, 会先在loaduser函数验证是否为已注册用户,从数据库里取用户, 能取到返回用户对象
@login_manager.user_loader
def load_user(user_id):
    from app.models import Admin
    user = Admin.query.get(int(user_id))
    return user