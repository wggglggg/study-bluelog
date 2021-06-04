from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, ValidationError, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, Email, Optional, URL
from flask_ckeditor import CKEditorField
from app.models import Category

# Login登陆表
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1,20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8,128)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')

# Post提交文章表
class PostForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1,60)])
    title = StringField('Title', validators=[DataRequired(), Length(1,60)])
    category = SelectField('Category', coerce=int, default=1)
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField()
    # choices 拿到分类列表与 Selectfield配合使用
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]

#分类表
class CategoryForm(FlaskForm):
    name = StringField('CategoryName', validators=(DataRequired(), Length(1,30)))
    submit = SubmitField('提交')

    #去分类数据库里面查找是否存在同名, validate_xxxxxx, xxxx为上面表中字段,  field.xxxx可以拿到用户在网页输入的信息
    def validate_name(self, field):
        if Category.query.filter_by(name=field.name).first():
            raise ValidationError('分类名称已经存在')

# 评论表
class CommentForm(FlaskForm):
    author = StringField('Name', validators=[DataRequired(), Length(1,30)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1,254)])
    site = StringField('Site', validators=[Optional(), URL(), Length(0,255)])
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField()

# 管理员评论表, author, email, site不需要,因为是管理员,所以要隐藏
# 继承了上面CommentForms类,  重写了三个字段为隐藏
class AdminCommentForm(CommentForm):
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()

# settingForm 设置网站about, 网站title标题与副标题
class SettingForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1,70)])
    blog_title = StringField("Blog Title", validators=[DataRequired(), Length(1,70)])
    blog_sub_title = StringField("Blog Sub Title", validators=[DataRequired(), Length(1,100)])
    about = CKEditorField('About Page', validators=[DataRequired()])
    submit = SubmitField()