from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from flask import jsonify

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'sqlflask'
app.config['MYSQL_PASSWORD'] = 'sqlflask'
app.config['MYSQL_DB'] = 'sae41'

mysql = MySQL(app)

def user_exists(username):
    conn = mysql.connection
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE login = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    cursor.close()
    return user is not None

def is_valid_user(username, password):
    conn = mysql.connection
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE login = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    cursor.close()
    return user is not None


@app.route('/get-users', methods=['GET'])
def get_users():
    cursor = mysql.connection.cursor()
    query = "SELECT login FROM users"
    cursor.execute(query)
    users = [user[0] for user in cursor.fetchall()]
    cursor.close()
    return jsonify(users)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = mysql.connection
        cursor = conn.cursor()

        query = "SELECT * FROM users WHERE login = %s"
        cursor.execute(query, (username,))
        login = cursor.fetchall()

        if is_valid_user(username, password):
            # Mot de passe correct
            return redirect('/reunion.html')
        else:
            # Mot de passe incorrect
            error = "Nom d'utilisateur ou mot de passe incorrect"
            return render_template('index.html', error=error)

    return render_template('index.html')


@app.route('/inscription.html', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        cur = mysql.connection.cursor()
        cur.execute("USE sae41")
        query = "INSERT INTO users (login, password) VALUES (%s, %s)"
        values = (username, password)
        cur.execute(query, values)

        mysql.connection.commit()
        cur.close()

        return redirect('/index.html')

    return render_template('inscription.html')


@app.route('/reunion.html', methods=['GET', 'POST'])
def reunion():
    return render_template('reunion.html')


if __name__ == '__main__':
    app.run()
