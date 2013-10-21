from flask import Flask, render_template, request, redirect, session, url_for, flash
import model

app = Flask(__name__)
app.secret_key = "shhhhthisisasecret"

# / has two routing functions. this one is for GET. the form has no action URL so it will just reload the same page it is on.
@app.route("/")
def index():
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
    return redirect(url_for("index"))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/user/<username>")
def show_wall_posts(username):
    model.connect_to_db()
    display_id = model.get_user_by_name(username)
    posts = model.get_posts_by_user_id(display_id)
    user_id = session.get('user_id')
    if user_id:
        return render_template("wall.html", posts=posts, userid=user_id)

    return render_template("wall.html", posts=posts)
 
if __name__ == "__main__":
    app.run(debug = True)
