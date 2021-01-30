import sqlite3
import psycopg2
import psycopg2.extras

from flask import Flask, g, request, jsonify
app = Flask(__name__)
from model import comment, User
from counter import counter
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_cors import CORS, cross_origin
#from env import password
import os

password = os.environ.get("DBPASS")


app.secret_key = b'\x0e\xe2k:\xc0\xaa&%\x1c\xecrn\x11N\xaf\xe8'

app.debug = True

login_manager = LoginManager()

login_manager.init_app(app)

CORS(app, supports_credentials=True)

#db connection setup
host = "localhost"
port = "5432"
dbname = "postgres"
user = "postgres"
conn = psycopg2.connect(host = host, port = port, dbname = dbname, user = user, password = password)


#CORS(app)

DATABASE = './database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def to_dicts(rows):
    dicts = []
    for row in rows:
        dic = {}
        for key in row.keys():
            dic[key] = row[key]
        dicts.append(dic)
    return(dicts)

def counter_up():
    new = counter
    new += 1
    file = open("counter.py","w")
    file.write("counter = " + str(new))
    file.close()

@login_manager.user_loader
def load_user(id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    db = get_db()
    cur = db.cursor()
    cursor.execute("Select * FROM Users WHERE userName = %s", (id,))
    u = cursor.fetchone()
    user = User(u["username"], u["password"])

    return(user)
    

@app.route('/')
def hello_world():
    cur = get_db().cursor()
    print(cursor.execute("SELECT * FROM COMMENTS").fetchall())
    print(current_user)
    return {
            "username":"test",
            }



@app.route('/comments', methods=['POST', 'GET'])
def all_comments():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if request.method == 'POST':
        data = eval(request.data)
        parent = data["parent"]
        content = data["content"]
        user = current_user.userName
        score = 0
        cursor.execute("INSERT INTO comments (id, parent, content, username, score) VALUES (nextval('count'),%s,%s,%s,%s)", (parent, content, user, score))
        conn.commit()
        counter_up()
    cursor.execute("SELECT * FROM comments")
    ret = cursor.fetchall()
    return jsonify(to_dicts(ret))

@app.route('/posts', methods=['POST', 'GET'])
def posts():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if request.method == 'POST':
        data = eval(request.data)
        title = data["title"]
        content = data["content"]
        user = data["user"]
        score = data["score"]
        subreddit = data["subreddit"]
        cursor.execute("INSERT INTO posts (id, title, content, username, score, subreddit) VALUES (%s,%s,%s,%s,%s,%s)", (counter, title, content, user, score, subreddit))
        conn.commit()
        counter_up()
    print(current_user)
    cursor.execute("SELECT * FROM posts")
    ret = cursor.fetchall()
    return jsonify(ret)

@app.route('/posts/<post>')
def post(post):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM posts WHERE id = %s", (post,))
    ret = cursor.fetchone()
    return jsonify(ret)

@app.route('/posts/<post>/upvote', methods=['POST'])
def upvote(post):
    data = eval(request.data)
    user = data["userName"]
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT upvoters, downvoters, score FROM posts WHERE id = %s", (post,))
    voters = cursor.fetchone()
    upvoters = voters['upvoters']
    downvoters = voters['downvoters']
    score = voters['score']
    if upvoters is None:
        upvoters = []
    if downvoters is None:
        downvoters = []
    if user in upvoters:
        upvoters.remove(user)
        score -= 1
        cursor.execute("UPDATE posts SET (upvoters, score) = (%s, %s) WHERE id = %s", (upvoters, score, post))
    else:
        if user in downvoters:
            downvoters.remove(user)
            upvoters.append(user)
            score += 2
            cursor.execute("UPDATE posts SET (upvoters, downvoters, score) = (%s, %s, %s) WHERE id = %s", (upvoters, downvoters, score, post))
        else:
            upvoters.append(user)
            score += 1
            cursor.execute("UPDATE posts SET (upvoters, downvoters, score) = (%s, %s, %s) WHERE id = %s", (upvoters, downvoters, score, post))
    if user in upvoters:
        vote = 1
    else:
        vote = 0
    ret = {"score":score,"vote":vote}
    print(ret)
    conn.commit()
    return jsonify(ret)


@app.route('/posts/<post>/downvote', methods=['POST'])
def downvote(post):
    data = eval(request.data)
    user = data["userName"]
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT upvoters, downvoters, score FROM posts WHERE id = %s", (post,))
    voters = cursor.fetchone()
    upvoters = voters['upvoters']
    downvoters = voters['downvoters']
    score = voters['score']
    if upvoters is None:
        upvoters = []
    if downvoters is None:
        downvoters = []
    if user in downvoters:
        downvoters.remove(user)
        score += 1
        cursor.execute("UPDATE posts SET (downvoters, score) = (%s, %s) WHERE id = %s", (downvoters, score, post))
    else:
        if user in upvoters:
            upvoters.remove(user)
            downvoters.append(user)
            score -= 2
            cursor.execute("UPDATE posts SET (upvoters, downvoters, score) = (%s, %s, %s) WHERE id = %s", (upvoters, downvoters, score, post))
        else:
            downvoters.append(user)
            score -= 1
            cursor.execute("UPDATE posts SET (upvoters, downvoters, score) = (%s, %s, %s) WHERE id = %s", (upvoters, downvoters, score, post))
    if user in downvoters:
        vote = -1
    else:
        vote = 0
    ret = {"score":score,"vote":vote}
    print(ret)
    conn.commit()
    return jsonify(ret)


@app.route('/comments/<post>')
def comments(post):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM COMMENTS WHERE parent = %s", (post,))
    ret2 = cursor.fetchall()
    print(post)
    print(ret2)
    return jsonify(ret2)

@app.route('/subreddits', methods=['POST', 'GET'])
def subreddits():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return(login_manager.unauthorized())
        data = eval(request.data)
        title = data["title"]
        user = current_user.userName
        cursor.execute("INSERT INTO subreddits (id, title, username) VALUES (%s,%s,%s)", (counter, title, user))
        conn.commit()
        counter_up()
    cursor.execute("SELECT * FROM subreddits")
    ret = cursor.fetchall()
    return jsonify(ret)

@app.route('/r/<subreddit>')
def subreddit(subreddit):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM posts WHERE subreddit = %s", (subreddit,))
    ret = cursor.fetchall()
    return jsonify(ret)


@app.route('/users', methods=['POST', 'GET'])
def users():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        data = eval(request.data)
        userName = data["userName"]
        password = data["password"]
        cursor.execute("INSERT INTO users (id, userName, password) VALUES (%s,%s,%s)", (counter,userName, password))
        conn.commit()
        counter_up()
    cursor.execute("SELECT * FROM users")
    ret = cursor.fetchall()
    return jsonify(ret)

@app.route('/login', methods=["POST"])
def login():
    db = get_db()
    cur = db.cursor()
    data = eval(request.data)
    user = load_user(data["userName"])
    if user.password == data["password"]:
        login_user(user, remember=True)
        return {"":""}

@app.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    print("test")
    return {"":""}





