from flask import url_for, current_app
from flask_mail import Message

from app.extensions import mail

def send_email(email_title, to, html):
    message = Message(subject=email_title, recipients=[to], html=html)
    mail.send(message)  #需要用mail对象调用send方法


# 有文章的新评论时, 发邮件送给管理员;
def send_new_comment_email(post):
    post_url = url_for('blog.show_post', post_id=post.id, _external=True) + '#comments'
    print('send new comment email---', post_url)
    send_email(email_title='New Comment', to=current_app.config['BLUELOG_EMAIL'],
               html='<p> New comment in post <i>%s</i>, click the link below to check:</p>'
                    '<p><a href="%s">%s</p>'
                    '<p><small style="color: #868e96">Do Not reply this email.</small></p>'
                    % (post.title, post_url, post_url)
               )
# 评论有回复时, 发邮件送给评论人
def send_new_reply_email(comment):
    post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True) + '#comments'
    print('send_new_reply_email---', post_url)
    send_email(email_title='New reply', to=comment.email,
               html='<p>New reply for the comment you left in the post<i>%s</i></p>'
                    '<p><a href="%s">%s</p>'
                    '<p><small sytle="color: #868e96">Do not reply this email</small></p>'
                    % (comment.post.title, post_url, post_url)
               )
