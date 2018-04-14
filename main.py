from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://blogz:password@localhost:8889/blogz"
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "dfkj4230fjFLJFRjle9"
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    date = db.Column(db.DateTime, default=datetime.now())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ["index", "login", "signup", "blog"]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect("/login")

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    id = request.args.get('id')

    if not (id):

        posts = Blog.query.order_by("date desc").all()
        blog_range = 100

        return render_template('blog.html',title="My Blog",posts=posts)

    post_id = int(id)
    post = Blog.query.filter_by(id=post_id).first()

    return render_template('post.html', title="Blog Post", post=post)

@app.route('/newpost', methods=['GET'])
def newpost():

    return render_template('newpost.html', title="New Post")

@app.route('/newpost', methods=['POST'])
def add_post():
    blog_title = request.form['title']
    blog_body = request.form['blog']

    if not (blog_title):
        if not (blog_body):
            return render_template('newpost.html', title="New Post", error_title=True, error_body=True)
        else:
            return render_template('newpost.html', title="New Post", error_title=True, b_body=blog_body)
    if not (blog_body):
        return render_template('newpost.html', title="New Post", error_body=True, b_title=blog_title)

    new_post = Blog(blog_title, blog_body)
    db.session.add(new_post)
    db.session.commit()

    post_id = Blog.query.all()

    return redirect("/blog?id=" + str(post_id[-1].id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if User.query.filter_by(username=username).first():
            flash("User already exist.")
            return redirect("/login")

        if not username:
            flash("You must enter a username.")
            return render_template("signup.html")
        elif len(username) < 3:
            flash("Username must be 3 or more characters.")
            return render_template("signup.html", b_username=username)

        if not password:
            flash("You must enter a password.")
            return render_template("signup.html", b_username=username)
        elif len(password) < 3:
            flash("Password must be 3 or more characters.")
            return render_template("signup.html", b_username=username)

        if password != verify:
            flash("Your passwords do not match.")
            return render_template("signup.html", b_username=username)

        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        flash(username + " is signed up")
        return redirect("/newpost")

    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User.query.filter_by(username = username).first():
            flash("That user does not exist.")
            return redirect("/signup")

        user = User.query.filter_by(username = username).first()
        if not password == user.password:
            flash("The password you entered is incorrect.")
            return render_template("login.html", b_username=username)

        session['username'] = user.username
        flash("Logged in")
        return redirect("/newpost")

    return render_template("login.html")

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/logout')
def logout():
    del session['username']
    return redirect("/blog")

if __name__ == "__main__":
    app.run()
