from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
from datetime import datetime
import re

import os

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$")

app = Flask(__name__)
app.secret_key = "NOO"
bcrypt = Bcrypt(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register_user():
    is_valid = True

    if len(request.form["fname"]) < 2:
        is_valid = False
        flash("First name must be at least 2 characters long")
    if len(request.form["lname"]) < 2:
        is_valid = False
        flash("Last name must be at least 2 characters long")
    if len(request.form["password"]) < 8:
        is_valid = False
        flash("Password must be at least 8 characters long")
    if request.form["c_password"] != request.form["password"]:
        is_valid = False
        flash("Passwords must match")
    if not EMAIL_REGEX.match(request.form["email"]):
        is_valid = False
        flash("Please use a valid email address")

    mysql = connectToMySQL("quotedash")
    query = "select * from users where email = %(email)s"
    data = {"email": request.form["email"]}
    results = mysql.query_db(query, data)
    (print(results))
    if results:
        is_valid = False
        flash("please use a different email.")

    if is_valid:
        mysql = connectToMySQL("quotedash")
        # build my query
        query = "INSERT into users (fname, lname, password, email, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(pass)s, %(email)s, NOW(), NOW())"
        # pass revlevant to with my query
        data = {
            "fn": request.form["fname"],
            "ln": request.form["lname"],
            "pass": bcrypt.generate_password_hash(request.form["password"]),
            "email": request.form["email"],
        }
        # commit the query
        user_id = mysql.query_db(query, data)
        session["user_id"] = user_id

        return redirect("/quote")
    else:  # otherwise, reidrect and show errors
        return redirect("/")


@app.route("/login", methods=["POST"])
def login_user():
    is_valid = True

    if len(request.form["email"]) < 1:
        is_valid = False
        flash("Please enter your email")
    if len(request.form["password"]) < 1:
        is_valid = False
        flash("Please enter your password")

    if not is_valid:
        return redirect("/")
    else:
        mysql = connectToMySQL("quotedash")
        query = "SELECT * FROM users WHERE users.email = %(email)s"
        data = {"email": request.form["email"]}
        user = mysql.query_db(query, data)
        if user:
            hashed_password = user[0]["password"]
            if bcrypt.check_password_hash(hashed_password, request.form["password"]):
                session["user_id"] = user[0]["id"]
                return redirect("/quote")
            else:
                flash("Password is invalid")
                return redirect("/")
        else:
            flash("Please use a valid email address")
            return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/quote")
def quoting():
    if "user_id" not in session:
        return redirect("/")

    mysql = connectToMySQL("quotedash")
    query = "SELECT * FROM users WHERE users.id = %(uid)s"
    data = {"uid": session["user_id"]}
    
    try:
        user = mysql.query_db(query, data)[0]
    except IndexError:
        # TODO: Show an error and request user to clear session because
        # we couuldn't find the user that is in our database correspondin
        # to the user_id that is retrieved from the session.
        user = {}


    # `Virtually any API can fail`
    # mysql = connectToMySQL("quotedash")
    # query = """SELECT quotes.id,
    #                   users.fname, 
    #                   quotes.quote, 
    #                   quotes.created_at, 
    #                   quotes.quote,
    #                   quotes.posted_by, 
    #                   COUNT(liked_quotes.quotes_id) as times_liked 
    #             FROM quotes 
    #             LEFT JOIN liked_quotes
    #             ON quotes.id = liked_quotes.quotes_id 
    #             JOIN users
    #             ON quotes.id = users.id  
    #             GROUP BY quotes.id 
    #             ORDER BY quotes.created_at DESC"""
    mysql = connectToMySQL("quotedash")
    query = """SELECT quotes.id, 
                    users.fname as posted_by_username, 
                    author, 
                    quotes.created_at, 
                    quotes.quote, 
                    posted_by, 
                    count(liked_quotes.quotes_id) as times_liked 
                from quotes left join liked_quotes 
                ON quotes.id = liked_quotes.quotes_id 
                left join users
                ON quotes.posted_by = users.id;
                """
    # import ipdb; ipdb.set_trace()
    
              
    quotes = mysql.query_db(query)
    print(quotes)
    #import ipdb; ipdb.set_trace()

    query = """
    SELECT  liked_quotes.quotes_id
    From liked_quotes
    WHERE users_id=%(uid)s;
    """
    data = {"uid": session["user_id"]}
    current_user_liked_quotes = mysql.query_db(query, data)

    return render_template("quote.html", quotes=quotes, user=user, current_user_liked_quotes=current_user_liked_quotes)


@app.route("/create", methods = ["POST"])
def createQuotes():
    if "user_id" not in session:
        return redirect("/")

    is_valid = True
    if len(request.form["quote"]) < 1:
        is_valid = False
        flash("Quote cannot be blank")
    if len(request.form["quote"]) >= 256:
        is_valid = False
        flash("Quote cannot be more than 255 characters")

    if is_valid:
        mysql = connectToMySQL("quotedash")
        query = "INSERT INTO quotes (quote, author, created_at, updated_at, posted_by) VALUES (%(quote)s, %(author)s, NOW(), NOW(), %(posted_by)s)"
        data = {"author": request.form["author"], "quote": request.form["quote"], "posted_by": session["user_id"]}
        tweet = mysql.query_db(query, data)

    return redirect("/quote")


#TODO: change to `quote_id` instead of `quotes_id`
# Remember that table name is plural because it contains a lot or rows of your resource
# Each column refers to a single instance's attribute, so it should be singular.
@app.route("/quotes/<quotes_id>/add_like")
def like_quote(quotes_id):
    query = "INSERT INTO liked_quotes (users_id, quotes_id) VALUES (%(user_id)s, %(quotes_id)s)"
    data = {"user_id": session["user_id"], "quotes_id": quotes_id}
    mysql = connectToMySQL("quotedash")
    mysql.query_db(query, data)
    flash("You just liked this quote")
    return redirect("/quote")


@app.route("/quotes/<quotes_id>/unlike")
def unlike_quote(quotes_id):
    query = "DELETE FROM liked_quotes WHERE users_id = %(user_id)s AND quotes_id = %(quotes_id)s"
    data = {"user_id": session["user_id"], "quotes_id": quotes_id}
    mysql = connectToMySQL("quotedash")
    mysql.query_db(query, data)
    flash("You just unliked the quote")
    return redirect("/quote")


@app.route("/quotes/<quote_id>/delete", methods=["GET"])
def delete_quote(quote_id):

    query = "DELETE FROM liked_quotes WHERE quotes_id = %(quote_id)s"
    data = {
        'quote_id': quote_id}
    mysql = connectToMySQL('quotedash')
    mysql.query_db(query, data)

    query = "DELETE FROM quotes WHERE id = %(quote_id)s"
    data = {"user_id": session["user_id"], "quote_id": quote_id}
    mysql = connectToMySQL("quotedash")
    mysql.query_db(query, data)
    return redirect("/quote")


@app.route("/editAccount", methods=["GET", "POST"])
def edit_account():
    if "user_id" not in session:
        flash("You cannot edit account that are not yours.")
        return redirect("/")

    user_id = session["user_id"]
    # TODO: Handle case when user_id not present
    # TODO: Remove these query to fetch code and try to create form of user information
    # and edit it using SQL query
    if request.method == "GET":
        return render_template("myaccount.html")
    data = {
        "first_name": request.form["fname"],
        "last_name": request.form["lname"],
        #"pass": bcrypt.generate_password_hash(request.form["password"]),
        "email": request.form["email"],
        "user_id": user_id,
    }   
    for k, v in data.items():
        if not v:
            data[k] = None
    #import ipdb; ipdb.set_trace()
    #query = """UPDATE users SET fname=%(first_name)s, lname=%(last_name)s, email=%(email)s WHERE id=%(user_id)s"""

    query = "UPDATE users SET "
    if data["first_name"]:
        query += " fname=%(first_name)s"
    if data["last_name"]:
        if data["first_name"]:
            query += ","
        query += " lname=%(last_name)s"
    if data["email"]:
        if data["last_name"]:
            query += ","
        query += " email=%(email)s"
    query += " WHERE id=%(user_id)s "
    
    #SET fname=%()
    #WHERE id=%()s"""
    # data = {"user_id": user_id}

    #editAccount
    mysql = connectToMySQL("quotedash")
    result = mysql.query_db(query, data)
    # import ipdb; ipdb.set_trace()
    flash("Your profile information has been updated successfuly")
    return render_template("myaccount.html")


@app.route("/users")
def show_users():
    query = """SELECT quote, author, posted_by
    FROM quotes"""
    mysql = connectToMySQL("quotedash")
    # data = {"uid": session["user_id"]}
#    import ipdb; ipdb.set_trace()
    quotes = mysql.query_db(query)

    # mysql = connectToMySQL('quotedash')
    # query = "SELECT followed FROM user_followers WHERE following = %(id)s"
    # data = {'id': session['user_id']}

    return render_template("user.html", quotes=quotes)


if __name__ == "__main__":
    app.run(debug=True)
