
from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, Blueprint
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post, Books
from flaskblog.posts.forms import PostForm
import requests

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('new_post.html', title="New Post", legend="New Post", form=form)


@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('new_post.html', title=post.title, legend="Update Post", form=form)


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'danger')
    return redirect(url_for('main.home'))


@posts.route("/search")
@login_required
def search():
    return render_template('search.html', title='Search')


@posts.route("/results", methods=['POST', 'GET'])
@login_required
def results():
    category = request.form.get('category')
    search = request.form.get('search')
    search = "'%" + search + "%'"
    results = db.session.execute("SELECT * FROM Books WHERE " + category + " LIKE " + search).fetchall()
    if db.session.execute("SELECT * FROM Books WHERE " + category + " LIKE " + search).rowcount == 0:
        message = 'We are sorry. There were no results for your search.'
        return render_template("results.html", message=message, results=results, title='Search Results')

    return render_template("results.html", results=results, title='Search Results')


@posts.route("/<string:book_num>", methods=['POST', 'GET'])
@login_required
def book(book_num):
    if db.session.execute("SELECT * FROM books WHERE book_num = :book_num", {"book_num": book_num}).rowcount == 0:
        return render_template("errors/404.html"), 404
    else:
        book = db.session.execute("SELECT * FROM books WHERE book_num = :book_num", {"book_num": book_num}).fetchone()

    posts = Post.query.filter_by(book_num=book_num).all()

    # Get APIs from Goodreads.
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "9p5DL4xMYjGwUyWDLfgDw", "isbns": book_num})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful for.")
    data = res.json()
    num_ratings = data["books"][0]["work_ratings_count"]
    avg_rating = data["books"][0]["average_rating"]
    our_avg_rate = db.session.execute("SELECT AVG(Cast(rating as Float)) FROM post WHERE book_num = :book_num",
                                      {"book_num": book_num}).fetchone()[0]
    # Post a User's Review.
    form = PostForm()
    if form.validate_on_submit():
        rating = int(request.form.get("rating"))
        post1 = Post(title=form.title.data, content=form.content.data, author=current_user, book_num=book_num, rating=rating)
        db.session.add(post1)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template("book.html", title=book.name, book=book, posts=posts, form=form,
                           legend="Write a Review", num_ratings=num_ratings, avg_rating=avg_rating,
                           our_avg_rate=our_avg_rate)


@posts.route("/api/books/<string:book_num>")
def book_api(book_num):
    book = db.session.execute("SELECT * FROM books WHERE book_num = :book_num",
                              {"book_num": book_num}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid isbn number"}), 422

    review_counts = db.session.execute("SELECT COUNT(rating) FROM post WHERE book_num = :book_num",
                                       {"book_num": book_num}).fetchone()[0]
    our_avg_rate = db.session.execute("SELECT AVG(Cast(rating as Float)) FROM post WHERE book_num = :book_num",
                                      {"book_num": book_num}).fetchone()[0]
    return jsonify({
        "title": book.name,
        "author": book.author,
        "year": book.year,
        "isbn": book.book_num,
        "review_count": review_counts,
        "average_score": our_avg_rate
    })
