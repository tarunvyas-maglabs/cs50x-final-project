# Immerse — Book Discovery & Rating Web App

Immerse is a Flask-based web application that allows users to search for books using the **Google Books API** and rate them on a 5-star scale. Logged-in users can maintain a personal list of rated books and view a global leaderboard ranking books by aggregated ratings across all users.

<img width="2560" height="1319" alt="Screenshot 2026-02-10 at 10 32 26 AM" src="https://github.com/user-attachments/assets/37914086-cbde-485f-af7b-34c5aa61a520" />

When a user visits the site, they can browse articles, search for books, view recommendations, and (if signed in) access their personal list.

<img width="2560" height="1318" alt="Screenshot 2026-02-10 at 10 34 37 AM" src="https://github.com/user-attachments/assets/ef339395-d4d6-4051-ba23-af0c8fccab42" />

The user can search for a book which calls the Google Books API and returns a list of books that match the contents entered by the user. If the user is signed in they can rate the books.

<img width="2559" height="1314" alt="Screenshot 2026-02-10 at 10 32 17 AM" src="https://github.com/user-attachments/assets/ff791ac0-6ee9-4ac8-ba8f-cd6db3dbbad7" />

When a user rates a book it will be added to their list of books ordered by highest rated to lowest rated.

<img width="2560" height="1351" alt="Screenshot 2026-02-10 at 10 27 58 AM" src="https://github.com/user-attachments/assets/2eccb3dd-7e0f-4f3d-b466-ca8326e3e410" />

The Recommended tab displays the highest-rated books across all users.

---

## Features
- User authentication (register/login/logout)
- Book search via Google Books API
- Book rating system (1–5 stars)
- Personal rated list (“My List”), ordered by rating
- Global leaderboard aggregating ratings across all users

---

## Tech Stack
- **Backend:** Python, Flask  
- **Frontend:** HTML, CSS, Bootstrap  
- **Database:** SQLite  
- **API:** Google Books API  

---

## Project Structure
Key templates include:
- `index.html` — homepage  
- `search.html` — book search interface  
- `leaderboard.html` — global ranked list  
- `mylist.html` — user-specific rated list  
- `login.html`, `register.html` — authentication  
- `layout.html`, `sign.html` — shared layout templates  
- `project.js` — rating logic and front-end behavior  
- `style.css` — additional styling  

---

## Database Design
The SQLite database contains:
- `users` — user account information  
- `books` — stored book details and aggregated rating values  
- `ratings` — individual user ratings per book  
- `authors` — author information  

Books are stored in the database only after being rated by at least one user.

---

## Notes
This project was developed as the final project for **Harvard CS50x**.