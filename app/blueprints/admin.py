from flask import Blueprint, flash, redirect, url_for, render_template,request, current_app
from flask_login import login_required, current_user
from app.forms import SettingForm, PostForm, CategoryForm
from app.models import db, Admin, Post, Category, Comment
from app.utils import redirect_back



admin_bp = Blueprint('admin', __name__)


# 小技巧一次性为所有路由上方加上登录需求  login_required
# 随便写函数, 函数内容为空即可.
@admin_bp.before_request
@login_required
def login_protect():
    pass

@admin_bp.route('/admin')
def admin():
    pass

# 博客管理settings页面
@admin_bp.route('/settings', methods=["GET", "POST"])
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        name = form.name.data
        blog_title = form.blog_title.data
        blog_sub_title = form.blog_sub_title.data
        about = form.about.data
        db.session.commit()
        flash('设置成功')
        return redirect(url_for('blog.index'))
    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.blog_sub_title.data = current_user.blog_sub_title
    form.about.data = current_user.about
    return render_template('admin/settings.html', form=form)

# 发表文章Post
@admin_bp.route('/new_post', methods=['GET','POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        username = current_user.name
        # print('name----', username)
        body = form.body.data
        category = Category.query.get_or_404(form.category.data)

        post = Post(title=title, name=username, body=body, category=category)
        db.session.add(post)
        db.session.commit()
        flash('新文章创建成功', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)

# 添加新分类
@admin_bp.route('/new_category', methods=['GET', 'POST'])
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash("添加新分类成功", 'success')
        return redirect(url_for('blog.index'))
    return render_template('admin/new_category.html', form=form)

# 文章删除功能
@admin_bp.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('删除成功')
    return redirect_back()

# 删除评论
@admin_bp.route('/delete_comment/<int:comment_id>', methods=["POST"])
def delete_comment(comment_id):

    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash("此条评论(包含回复)已经删除", 'success')
    print(current_user.username, admin.username)
    return redirect_back()

# 开户或者关闭评论
@admin_bp.route('/set_comment/<int:post_id>', methods=['POST'])
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if  post.can_comment:  # 默认是True开启
        post.can_comment = False
        flash('评论已关闭.','info')

    else:
        post.can_comment = True
        flash('评论已开启.', 'info')

    db.session.commit()
    return redirect(url_for('blog.show_post', post_id=post.id))



# 文章再次编辑发布
@admin_bp.route('/edit_post/<int:post_id>', methods=['GET','POST'])
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.name = form.username.data
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get_or_404(form.category.data)
        db.session.commit()
        flash('修改成功')
        return redirect(url_for('blog.show_post', post_id=post_id))
    form.username.data = post.name
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('admin/edit_post.html', form=form)




@admin_bp.route('/new_link')
def new_link():
    pass

# 文章管理页面
@admin_bp.route('/manage_post')
def manage_post():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_MANAGE_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('admin/manage_post.html', pagination=pagination, posts=posts)

@admin_bp.route('/manage_category')
def manage_category():
    return render_template('admin/manage_category.html')

# 审核评论
@admin_bp.route('/approve_comment/<int:comment_id>', methods=['GET','POST'])
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    flash('评论已经审核完毕')
    return redirect_back()

# 管理评论--后台
@admin_bp.route('/manage_comment/<filter>')
def manage_comment(filter):
    # filter_rule = request.args.get('filter','all') # 在网址里拿filter, 如果值为空默认是all,
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_MANAGE_COMMENT_PER_PAGE']
    if filter== 'unread':
        # 如果过滤器filter_rule为未审核过,也可称为未读的评论
        filter_comments = Comment.query.filter_by(reviewed=False)
    elif filter == 'admin':
        # 如果过滤器filter_rule为 查看管理员评论
        filter_comments = Comment.query.filter_by(from_admin=True)
    else:
        # 查看所有评论
        filter_comments = Comment.query

    pagination = filter_comments.order_by(Comment.timestamp.desc()).paginate(page, per_page)
    comments = pagination.items
    print('filter是' ,filter)
    return render_template('admin/manage_comment.html', filter=filter, comments=comments, pagination=pagination)

@admin_bp.route('/edit_category/<int:category_id>')
def edit_category(category_id):
    pass

@admin_bp.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('无法删除默认分类category')
        return redirect_back()
    name = category.name
    category.delete()
    flash('%s 分类已经被删除' % name)
    return redirect(url_for('admin.manage_category', filter='all'))
