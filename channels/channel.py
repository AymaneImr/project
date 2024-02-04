from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort, current_app, jsonify
from flask_login import login_required, current_user
from admin.models import Post, users, Comments, Like
from admin.extensions import db
import time

fourth = Blueprint('fourth', __name__, static_folder='static', template_folder='templates')


@fourth.route('/<username>')
@login_required
def my_channel(username):
    user = users.query.filter_by(username=username).first()
    quotes = user.posts
    return render_template("my_channel.html", quotes=quotes, user=user)

'''create a quote or a post / pictures'''

@fourth.route('/create_quote', methods=['POST', 'GET'])
@login_required
def create_quote():
    if request.method == 'POST':
        # extract name, content of the quote, 
        quote_name = request.form.get('quote_name')
        content = request.form.get("content")
        if len(quote_name) > 48:
            flash('Too long for just a Title!')
            return redirect(request.url)
        add_content = Post(name=quote_name, content=content, users_id=current_user._id)
        db.session.add(add_content)
        db.session.commit()
        flash("Quote added successfuly!")
        time.sleep(1)
        return redirect(url_for("fourth.my_channel", username=current_user.username))
    return render_template("create_quote.html")

@fourth.route("/delete_post/<id>")
@login_required
def delete_post(id):
    """Delete a specific post"""
    post = Post.query.filter_by(_id=int(id)).first()
    if current_user != post.users and not current_user.is_admin:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post has been deleted!", "danger")
    time.sleep(1)
    return redirect(request.referrer)

@fourth.route("/channels")
@login_required
def channels():
    user = users.query.filter_by(_id=current_user._id).first()
    posts = Post.query.all()
    return render_template("channels.html", quotes=posts)

@fourth.route("/add_comments/<id>", methods=["POST", "GET"])
@login_required
def add_comments(id):
    if request.method == 'POST':
        comment = request.form.get('comment')
        if not comment:
            flash("Your comment can't be empty.", "warning")
            return redirect(request.url)
        cmnt = Comments(comment=comment, users_id=current_user._id, post_id=id)
        db.session.add(cmnt)
        db.session.commit()
        flash("Comment added successfully.", 'seccess')
    return redirect(request.referrer)

@fourth.route('/like/<post_id>', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(_id=post_id).first()
    like = Like(users_id=current_user._id, post_id=post_id)
    liked_post = Like.query.filter_by(users_id=current_user._id, post_id=post_id).first()
    if liked_post:
        db.session.delete(liked_post)
        db.session.commit()
    else:
        db.session.add(like)
        db.session.commit()
    return jsonify({"likes": len(post.likes), "liked": current_user._id in map(lambda x: x.users_id, post.likes)})



@fourth.route('/delete_comment/<id>')
@login_required
def delete_comment(id):
    comment = Comments.query.filter_by(_id=id).first()
    if not comment:
        flash("the comment doesn't exist", 'error')
        return  redirect(request.referrer)
    db.session.delete(comment)
    db.session.commit()
    flash('Seccessfuly deleted comment', 'seccess')
    return redirect(request.referrer)

@fourth.route("/search", methods=['POST'])
def search():
    if request.method == 'POST':
        search = request.form.get("search")
        results = users.query.filter(users.username.like("%" + search + "%")).order_by(users.date_joined).limit(10).all()
        return render_template('search_results.html', results=results, search=search)
    return render_template("my_channel.html")