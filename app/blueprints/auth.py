from flask import Blueprint, redirect, url_for, flash, render_template
from app.utils import redirect_back
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm
from app.models import Admin

auth_bp = Blueprint('auth', __name__)





# 登入页面
@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:  # 当前用户是登录状态, 直接跳到Index.
        return redirect(url_for('blog/index'))

    # 如果不是登录状态, 从登录页面获取用户输入的用户名与密码
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.filter_by(username=username).first()  #先去数据库里取管理员信息
        if admin:
            # 验证用户用户名与密码, 如果数据库提取的用户名与网页获取到的用户名一致并且,
            # validate_password验证网页输入的密码为 True
            if admin.username == username and admin.validate_password(password):
                login_user(admin, remember)  # 传入用户对象 与 remeber布尔值 登录用户
                flash("登录成功", "info") # 用info样式提示
                return redirect_back() #返回登录的一个页面

            flash('用户名或者密码错误.', 'warning')  # 警告样式提示

        else:
            flash('用户名不存在', 'warning') # 如果数据库没有取到用户, 显示 不存在
    return render_template('auth/login.html', form=form)


# 登出页面
@auth_bp.route('/logout')
@login_required  # 需要是已登陆状态, 才可以退出
def logout():
    logout_user()
    flash("已退出", 'info')
    return redirect_back()

