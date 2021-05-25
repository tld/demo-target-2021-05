from traceback import print_exc

from flask import Flask, request, jsonify, abort

import psycopg2

from demo_target_2021_05.insecurity import sign, verify

app = Flask(__name__)


@app.route("/api/register", methods=['POST'])
def register():
    username = request.form["username"]
    password = request.form["password"]
    print("registering: %s" % username)

    try:
        conn = psycopg2.connect("postgres://recipes@localhost/recipes")
        curs = conn.cursor()
        curs.execute("INSERT INTO logins (username, role, password) VALUES (%s, %s, %s)", (username, 'user', password))
        conn.commit()
        return "registered: %s" % username
    except:
        return "failed to register: %s" % username


@app.route("/api/login", methods=['POST'])
def login():
    username = request.form["username"]
    password = request.form["password"]
    print("logging in: %s" % username)

    conn = psycopg2.connect("postgres://recipes@localhost/recipes")
    curs = conn.cursor()
    curs.execute("SELECT id, role, username FROM logins WHERE username = %s AND password = %s", (username, password,))
    uid, role, username = curs.fetchone()
    print("uid: %r" % uid)
    print("role: %r" % role)

    token = sign({"id": uid, "role": role, "username": username})
    return jsonify({"message": "Approved, use attached token in Authorization-header.", "token": token})

@app.route("/api/recipes/<rid>")
def recipes(rid):
    print("Looking up recipe: %r" % rid)
    conn = psycopg2.connect("postgres://recipes@localhost/recipes")
    curs = conn.cursor()
    curs.execute("SELECT id, name, recipe FROM recipes WHERE secret = False AND id = %s" % rid)

    recipes = []
    for rid, name, recipe in curs.fetchall():
        recipes.append({"id": rid, "name": name, "recipe": recipe})

    if not recipes:
        abort(404)

    return jsonify(recipes)

@app.route("/api/recipes", methods=['POST'])
def post_recipes():
    name = request.form["name"]
    recipe = request.form["recipe"]
    auth = request.headers["authorization"]

    verified = verify(auth)
    if verified['role'] != 'admin':
        return jsonify({"message": "Not allowed to do that, needs to be admin."})

    try:
        conn = psycopg2.connect("postgres://recipes@localhost/recipes")
        curs = conn.cursor()
        curs.execute("INSERT INTO recipes (name, recipe) VALUES (%s, %s)", (name, recipe,))
        conn.commit()
        return "stored recipe: %s" % recipe
    except:
        print_exc()
        return "failed to store recipe: %s" % recipe

@app.route("/api/recipes")
def recipes_list():
    conn = psycopg2.connect("postgres://recipes@localhost/recipes")
    curs = conn.cursor()
    curs.execute("SELECT id, name, secret FROM recipes")

    recipes = []
    for rid, name, secret in curs.fetchall():
        if secret:
            recipes.append({"id": rid, "name": name, "access": "CONFIDENTIAL"})
        else:
            recipes.append({"id": rid, "name": name, "access": "public"})

    if not recipes:
        abort(404)

    return jsonify(recipes)


app.debug = True
app.run(host="0.0.0.0", port=42999)

