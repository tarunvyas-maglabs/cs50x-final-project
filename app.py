import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import requests

from helpers import login_required, apology

app = Flask(__name__)

# Use filesystem instead of cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///project.db")

# Global variable - Google Books API
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password:
            return "Please enter a username"
        if not confirmation or confirmation != password:
            return "Passwords do not match"
        
        hashed_password = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users(username,hash) VALUES (?, ?)", username, hashed_password)
            return redirect("/")
        except ValueError:
            return "Username already exists"
        
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


@app.route("/search")
def search():
    query = request.args.get("search")
    page = int(request.args.get("page", 0))
    if not query:
        return apology("Could not find")
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{query}&startIndex={page * 40}&maxResults=40&key={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        raw_books = response.json().get('items', [])  # Extract items
        if not raw_books:
            return render_template("Error")
        books = []

        for item in raw_books:
            volume_info = item.get('volumeInfo', {})
            books.append({
                'title': volume_info.get('title', 'Unknown Title'),
                'authors': ', '.join(volume_info.get('authors', [])),
                'description': volume_info.get('description', 'No description available'),
                'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                'id': item.get('id', '')  # Include book ID for potential interactions
            })

        # Pass the processed books to the template
        return render_template('search.html', books=books, query=query, page=page, total_pages = 40)
    else:
        # Handle API errors gracefully
        return render_template('search.html', error="Failed to fetch results. Try again.")
    
@app.route("/rate-book", methods=["POST"])
@login_required
def rate_book():
    try:
        # Parse JSON from the request body
        data = request.get_json()
        if not data:
            app.logger.error("No data received in the request.")
            return jsonify(success=False, error="No data received"), 400

        # Log the received payload
        app.logger.debug(f"Received payload: {data}")

        # Extract data
        book_id = data.get('book_id')
        rating = float(data.get('rating'))  # Ensure rating is a float
        book_title = data.get('book_title')
        author_name = data.get('author_name')
        publication_year = data.get('publication_year')
        image_url = data.get('image_url')
        user_id = session.get('user_id')

        # Validate data
        if not user_id:
            app.logger.error("Unauthorized access: no user_id in session.")
            return jsonify(success=False, error="Unauthorized"), 401
        if not all([book_id, rating, book_title, author_name, image_url]):
            app.logger.error("Missing required fields. Payload: %s", data)
            return jsonify(success=False, error="Invalid data"), 400

        # Handle author_name normalization
        if isinstance(author_name, str):
            author_name = ''.join(author_name.split(', '))  # Normalize format

        # Handle missing publication_year
        if not publication_year:
            publication_year = "Unknown"

        # Insert or update the author
        existing_author = db.execute("SELECT id FROM authors WHERE name = ?", author_name)
        if not existing_author:
            author_id = db.execute("INSERT INTO authors (name) VALUES (?)", author_name)
        else:
            author_id = existing_author[0]["id"]

        # Insert or update the book
        existing_book = db.execute("SELECT id FROM books WHERE id = ?", book_id)
        if not existing_book:
            db.execute("""
                INSERT INTO books (id, title, author_id, publication_year, image_url, total_ratings, ratings_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, book_id, book_title, author_id, publication_year, image_url, 0, 0)

        # Insert or update the rating
        existing_rating = db.execute("SELECT rating FROM ratings WHERE user_id = ? AND book_id = ?", user_id, book_id)
        if existing_rating:
            # Update the existing rating
            old_rating = existing_rating[0]["rating"]
            db.execute("UPDATE ratings SET rating = ? WHERE user_id = ? AND book_id = ?", rating, user_id, book_id)
            db.execute("""
                UPDATE books
                SET total_ratings = total_ratings - ? + ?
                WHERE id = ?
            """, old_rating, rating, book_id)
        else:
            # Insert a new rating
            db.execute("INSERT INTO ratings (user_id, book_id, rating) VALUES (?, ?, ?)", user_id, book_id, rating)
            db.execute("""
                UPDATE books
                SET total_ratings = total_ratings + ?, ratings_count = ratings_count + 1
                WHERE id = ?
            """, rating, book_id)

        # Log the updated book and rating data
        updated_book = db.execute("SELECT total_ratings, ratings_count FROM books WHERE id = ?", book_id)
        app.logger.debug(f"Updated book record: {updated_book}")

        updated_rating = db.execute("SELECT * FROM ratings WHERE user_id = ? AND book_id = ?", user_id, book_id)
        app.logger.debug(f"Updated rating record: {updated_rating}")

        return jsonify(success=True, message="Rating saved successfully")

    except Exception as e:
        app.logger.error(f"Error in rate_book: {str(e)}")
        return jsonify(success=False, error=str(e)), 500

@app.route("/mylist")
@login_required
def mylist():
    user_books = db.execute("""
        SELECT books.id, books.title, books.image_url, books.total_ratings, books.ratings_count, ratings.rating
        FROM ratings
        JOIN books ON books.id = ratings.book_id
        WHERE ratings.user_id = ?
        ORDER BY ratings.rating DESC, books.title
    """, session["user_id"])

    # Render template even if no books are rated
    return render_template("mylist.html", books=user_books)

@app.route("/leaderboard")
def leaderboard():
    books = db.execute("""
        SELECT books.id, books.title, books.image_url, books.total_ratings, books.ratings_count, 
               authors.name AS author_name
        FROM books
        JOIN authors ON authors.id = books.author_id
        WHERE books.ratings_count > 0
        ORDER BY (books.total_ratings / books.ratings_count) DESC, books.title
    """)

    # Render template with books or an empty list
    return render_template("leaderboard.html", books=books)
