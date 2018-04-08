from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog"
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    id = request.args.get('id')

    if not (id):

        posts = Blog.query.order_by("id desc").all()

        return render_template('blog.html',title="Blog Post",posts=posts)

    post_id = int(id)
    post = Blog.query.filter_by(id=post_id).first()

    return render_template('post.html', title=post.title, post=post)

@app.route('/newpost', methods=['GET'])
def newpost():

    return render_template('newpost.html', title="Add a Blog Entry")

@app.route('/newpost', methods=['POST'])
def add_post():
    blog_title = request.form['title']
    blog_body = request.form['blog']

    if not (blog_title):
        if not (blog_body):
            return render_template('newpost.html', title="Add a Blog Entry", error_title=True, error_body=True)
        else:
            return render_template('newpost.html', title="Add a Blog Entry", error_title=True, b_body=blog_body)
    if not (blog_body):
        return render_template('newpost.html', title="Add a Blog Entry", error_body=True, b_title=blog_title)

    new_post = Blog(blog_title, blog_body)
    db.session.add(new_post)
    db.session.commit()

    post_id = Blog.query.all()

    return redirect("/blog?id=" + str(post_id[-1].id))

if __name__ == "__main__":
    app.run()
