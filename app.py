from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend fetch calls

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",    # Use 'db' if using Docker
    user="root",
    password="pass",
    database="portfolio"
)

# Get all comments for a project
@app.route("/api/comments/<int:project_id>", methods=["GET"])
def get_comments(project_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT user_name, comment, timestamp FROM comments WHERE project_id=%s", (project_id,))
    comments = cursor.fetchall()
    return jsonify(comments)

# Add a comment
@app.route("/api/comment", methods=["POST"])
def add_comment():
    data = request.json
    user_name = data.get("user_name")
    comment = data.get("comment")
    project_id = data.get("project_id")

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO comments (project_id, user_name, comment, timestamp) VALUES (%s, %s, %s, %s)",
        (project_id, user_name, comment, datetime.now())
    )
    db.commit()

    # Update project stats (optional)
    cursor.execute("UPDATE project_stats SET comments_count = comments_count + 1, last_touched = %s WHERE project_id = %s",
                   (datetime.now(), project_id))
    db.commit()
    return jsonify({"status": "success"})

# Track project view
@app.route("/api/touch/<int:project_id>", methods=["POST"])
def touch_project(project_id):
    cursor = db.cursor()
    cursor.execute("UPDATE project_stats SET views = views + 1, last_touched = %s WHERE project_id=%s",
                   (datetime.now(), project_id))
    db.commit()
    return jsonify({"status": "touched"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
