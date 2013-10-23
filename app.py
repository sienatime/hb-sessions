from flask import Flask, render_template, request, redirect, session, url_for, flash
import model
import datetime

app = Flask(__name__)
app.secret_key = "shhhhthisisasecret"

# / has two routing functions. this one is for GET. the form has no action URL so it will just reload the same page it is on.
@app.route("/")
def index():
    if logged_in():
        return redirect(url_for("show_newsfeed"))

    return render_template("index.html")

# this routing function gets called after you submit the form on /.
@app.route("/", methods=["POST"])
def process_login():
    username = request.form.get("username")
    password = request.form.get("password")

    # calls the function authenticate() in model.py and returns True if user authentication info matches, and False if it does not.
    model.connect_to_db()
    authenticated = model.authenticate(username, password)
    if authenticated:
        # a flash is just a message that we can show to the user once. you can also pass it a category, and here I'm using the Bootstrap alert types to get some extra fancy styling
        flash("Welcome!","alert-success")
        # saves the username and user ID in the session so we can keep using it
        user_id = model.get_user_by_name(username)
        session['user_id'] = user_id
        session['username'] = username
        return redirect(url_for("show_newsfeed"))
    else:
        flash("Password incorrect, please try again.","alert-danger")

    # go to the index page if we failed to authenticate. url_for allows us to change our URLs later without breaking all of the references to them.
    return redirect(url_for("index"))

@app.route("/register")
def register():
    # if you are logged in and you try to go to /register, go instead to your wall.
    if logged_in():
        username = session['username']
        return redirect(url_for("show_wall_posts", profile=username))

    return render_template("register.html")

@app.route("/register", methods=['POST'])
def create_account():
    # i actually don't think you need this, because you will never be posting from the register page if you are logged in, since the register page just sends you to your profile if you are logged in.
    if logged_in():
        username = session['username']
        return redirect(url_for("show_wall_posts", profile=username))

    new_username = request.form.get("username")
    new_pwd = request.form.get("password")
    verify_pass = request.form.get("password_verify")
    model.connect_to_db()

    existing_user = model.get_user_by_name(new_username)

    if existing_user:
        flash("Username already exists, please choose a new one or log in instead.","alert-danger")
        return redirect(url_for("register"))
        
    if new_pwd == verify_pass:
        model.create_user(new_username, new_pwd)
        flash("User created! You can now log in.","alert-success")
        return redirect(url_for("index"))
    else:
        flash("Passwords did not match.","alert-danger")
        return redirect(url_for("register"))

@app.route("/newsfeed")
def show_newsfeed():
    if logged_in():
        model.connect_to_db()
        feed = model.get_newsfeed()
        pretty_data = make_pretty_data(feed)
        return render_template("feed.html", feed=pretty_data)

    flash("Sign up or log in to view the news feed!", "alert-danger")
    return redirect(url_for("index"))

@app.route("/user/<profile>")
def show_wall_posts(profile):
    model.connect_to_db()
    display_id = model.get_user_by_name(profile)
    posts = model.get_posts_by_user_id(display_id)
    pretty_data = make_pretty_data(posts)
    return render_template("wall.html", posts=pretty_data, profile=profile)

@app.route("/user/<profile>", methods=['POST'])
def post_to_wall(profile):
    content = request.form.get("post_text")
    # the person writing the post is the person logged in
    author_id = session['user_id']
    model.connect_to_db()
    # the owner is the person's wall we are currently looking at, and then we need the ID of that person
    owner_id = model.get_user_by_name(profile)
    # insert a row into the DB that contains the relevant data
    model.write_wall_post(owner_id, author_id, content)
    # then render the page with all of the wall posts on it, including the one we just wrote.
    return redirect(url_for("show_wall_posts", profile=profile))
 
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

def logged_in():
    return session.get('user_id')

def make_pretty_data(posts):
    pretty_data = []
    for story in posts:
        timestamp = datetime.datetime.strptime(str(story[2]),"%Y-%m-%d %H:%M:%S")
        author_name = model.get_name_by_id(story[1])
        owner_name = model.get_name_by_id((story[0]))
        pretty_data.append( (owner_name, author_name, timestamp, story[3]) )

    return pretty_data

if __name__ == "__main__":
    app.run(debug = True)
