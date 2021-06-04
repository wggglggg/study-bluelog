from flask import Blueprint, render_template, request, current_app, url_for, flash, redirect, abort, make_response
from app.utils import redirect_back
from app.models import Post, Comment, Category, Admin
from flask_login import current_user
from app.forms import AdminCommentForm, CommentForm
from app.extensions import db
from app.emails import send_new_comment_email, send_new_reply_email


blog_bp = Blueprint('blog', __name__)

# class current_user:
#     is_authenticated = False

@blog_bp.route('/blog')
def blog():
    pass

@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)  # page是获取当前在哪一页
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']  # per_page是每一页有多少个文章
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    #分页要用到.paginage(page, per_page=per-page)
    posts = pagination.items
    # .items拿到所有的文章
    return render_template('blog/index.html', posts=posts, pagination=pagination)


@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')

@blog_bp.route('/show_category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items

    return render_template('blog/show_category.html', category=category, pagination=pagination, posts=posts)

# 渲染某一文章的页面, 从Index.html点击某一文章Post, 会得到post_id, 拿到某一文章的信息, 渲染出来
@blog_bp.route('/show_post/<int:post_id>', methods=['GET','POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    # print('post_id--------------',post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).filter_by().order_by(Comment.timestamp.desc()).paginate(page, per_page)
    comments = pagination.items

    if current_user.is_authenticated:  #如果登录状态, 就使用管理员表单

        form = AdminCommentForm()
        form.author.data = current_user.username
        form.email.data =current_app.config['BLUELOG_EMAIL']
        form.site.data = url_for('blog.index')  #直接用的自己的bluelog网站
        from_admin = True  #表单没有from_admin, 直接写死如果是登录认证了, 就显示 有一些权限
        reviewed = True   # 登录过的用户,不用管理员审核

    else:    #如果未登录, 使用一般用户表单, 评论是未审核 状态
        form = CommentForm()
        from_admin = False
        reviewed = False


    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(author=author, email=email, site=site, post=post, body=body, from_admin=from_admin, reviewed=reviewed)
        if request.args.get('reply'):
            repled_comment = Comment.query.get_or_404(request.args.get('reply'))
            print('repled_comment----', repled_comment)
            comment.replied = repled_comment
            send_new_reply_email(comment.replied)

        db.session.add(comment)
        db.session.commit()
        if current_user.is_authenticated:
            flash('评论提交成功')
        else:
            flash("评论正等待审核!")
            send_new_comment_email(post)  #post拿到, 发邮件时会发送Post.id 为文章的id
        return redirect(url_for('blog.show_post', post_id=post_id) + '#comments')
    return render_template('blog/show_post.html', post=post, pagination=pagination, comments=comments, form=form)

# 回复评价页面
@blog_bp.route('/reply_comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    print('post_id 3---', comment.post_id)
    return redirect(url_for('blog.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')

# 将theme主题名存到cookie中,传给客户端
@blog_bp.route('/change_theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BLUELOG_THEMES'].keys():
        abort(404)  # 如果题名不在BLUELOG_THEMES字典中, 报错

    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)
    return response
