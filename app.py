from flask import Flask, render_template, request, redirect, session, url_for, flash
import model

app = Flask(__name__)
app.secret_key = "shhhhthisisasecret"

# / has two routing functions. this one is for GET. the form has no action URL so it will just reload the same page it is on.
@app.route("/")
def index():
    username = logged_in()
    if username:
        return redirect(url_for("show_wall_posts", username=username))

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
        # a flash is just a message that we can show to the user once
        flash("User authenticated!")
        # saves the username in the session so we can keep using it
        user_id = model.get_user_by_name(username)
        session['user_id'] = user_id
    else:
        flash("Password incorrect, please try again.")

    # go to the index page once we are done trying to authenticate. url_for allows us to change our URLs later without breaking all of the references to them.
    return redirect(url_for("show_wall_posts", username=username))

@app.route("/register")
def register():
    username = logged_in()
    if username:
        return redirect(url_for("show_wall_posts", username=username))
        
    return render_template("register.html")

@app.route("/register", methods=['POST'])
def create_account():
    username = logged_in()
    if username:
        return redirect(url_for("show_wall_posts", username=username))

    new_username = request.form.get("username")
    new_pwd = request.form.get("password")
    verify_pass = request.form.get("password_verify")
    model.connect_to_db()

    existing_user = model.get_user_by_name(new_username)

    if existing_user:
        flash("Username already exists, please try again.")
        return redirect(url_for("register"))

    if new_pwd == verify_pass:
        model.create_user(new_username, new_pwd)
        flash("User created! You can now log in.")
        return redirect(url_for("index"))
    else:
        flash("Passwords did not match.")
        return redirect(url_for("register"))

@app.route("/user/<username>")
def show_wall_posts(username):
    model.connect_to_db()
    display_id = model.get_user_by_name(username)
    posts = model.get_posts_by_user_id(display_id)
    pretty_data = []

    # post: 0: owner ID, 1: author ID, 2: date, 3: text
    for post in posts:
        pretty_data.append( (post[0], model.get_name_by_id(post[1]), post[2], post[3]) )

    user_id = session.get('user_id')
    profile = username
    if user_id:
        return render_template("wall.html", posts=pretty_data, userid=user_id, username=profile)

    return render_template("wall.html", posts=pretty_data, profile=username)

@app.route("/user/<username>", methods=['POST'])
def post_to_wall(username):
    content = request.form.get("post_text")
    # the person writing the post is the person logged in
    author_id = session['user_id']
    model.connect_to_db()
    # the owner is the person's wall we are currently looking at, and then we need the ID of that person
    print "username is", username
    owner_id = model.get_user_by_name(username)
    # insert a row into the DB that contains the relevant data
    model.write_wall_post(owner_id, author_id, content)
    # then render the page with all of the wall posts on it, including the one we just wrote.
    return redirect(url_for("show_wall_posts", username=username))
 
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

def logged_in():
    user_id = session.get('user_id')
    if user_id:
        model.connect_to_db()
        return model.get_name_by_id(user_id)

if __name__ == "__main__":
    app.run(debug = True)
