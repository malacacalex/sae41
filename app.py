from flask import Flask, render_template, request, redirect, jsonify
from flask_mysqldb import MySQL

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


def get_user_id(username):
    conn = mysql.connection
    cursor = conn.cursor()

    query = "SELECT id FROM users WHERE login = %s"
    cursor.execute(query, (username,))
    user_id = cursor.fetchone()

    cursor.close()
    return user_id[0] if user_id else None


def get_user_login(user_id):
    conn = mysql.connection
    cursor = conn.cursor()

    query = "SELECT login FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user_login = cursor.fetchone()

    cursor.close()
    return user_login[0] if user_login else None


def get_user_meetings(user_id):
    conn = mysql.connection
    cursor = conn.cursor()

    query = "SELECT m.creation_date, d.date, d.meeting_id, a.response " \
            "FROM meetings AS m " \
            "JOIN dates AS d ON m.id = d.meeting_id " \
            "LEFT JOIN answers AS a ON d.id = a.date_id AND a.user_name = %s " \
            "WHERE m.user_id = %s"
    cursor.execute(query, (get_user_login(user_id), user_id))
    meetings = cursor.fetchall()

    cursor.close()
    return meetings


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

        if is_valid_user(username, password):
            # Mot de passe correct
            return redirect('/reunion.html?user=' + username)
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

        if not user_exists(username):
            cur = mysql.connection.cursor()
            cur.execute("USE sae41")
            query = "INSERT INTO users (login, password) VALUES (%s, %s)"
            values = (username, password)
            cur.execute(query, values)

            mysql.connection.commit()
            cur.close()

            return redirect('/index.html')
        else:
            error = "Nom d'utilisateur déjà utilisé"
            return render_template('inscription.html', error=error)

    return render_template('inscription.html')


@app.route('/reunion.html', methods=['GET', 'POST'])
def reunion():
    user = request.args.get('user')
    if not user:
        return redirect('/index.html')

    if request.method == 'POST':
        user_id = get_user_id(user)
        if not user_id:
            return redirect('/index.html')

        date = request.form.get('meeting-date')
        participants = request.form.getlist('participants')

        conn = mysql.connection
        cursor = conn.cursor()

        # Vérifier si l'utilisateur a déjà une réunion planifiée à la même heure
        query = "SELECT COUNT(*) FROM dates AS d " \
                "JOIN meetings AS m ON d.meeting_id = m.id " \
                "WHERE d.date = %s AND m.user_id = %s"
        cursor.execute(query, (date, user_id))
        count = cursor.fetchone()[0]

        if count > 0:
            error = "Vous avez déjà une réunion planifiée à cette heure"
            meetings = get_user_meetings(user_id)
            return render_template('reunion.html', user=user, error=error, meetings=meetings)

        # Insérer la nouvelle réunion dans la base de données
        query = "INSERT INTO meetings (user_id, creation_date) VALUES (%s, NOW())"
        cursor.execute(query, (user_id,))
        meeting_id = cursor.lastrowid

        query = "INSERT INTO dates (user_id, meeting_id, date) VALUES (%s, %s, %s)"
        for participant in participants:
            cursor.execute(query, (user_id, meeting_id, date))

        conn.commit()
        cursor.close()

    user_id = get_user_id(user)
    if not user_id:
        return redirect('/index.html')

    meetings = get_user_meetings(user_id)
    return render_template('reunion.html', user=user, meetings=meetings)

@app.route('/create-meeting', methods=['POST'])
def create_meeting():
    user = request.args.get('user')
    if not user:
        return jsonify({'message': 'Utilisateur non spécifié'}), 400

    user_id = get_user_id(user)
    if not user_id:
        return jsonify({'message': 'Utilisateur non trouvé'}), 400

    data = request.json
    date = data.get('date')
    participants = data.get('participants')

    conn = mysql.connection
    cursor = conn.cursor()

    # Vérifier si l'utilisateur a déjà une réunion planifiée à la même heure
    query = "SELECT COUNT(*) FROM dates AS d " \
            "JOIN meetings AS m ON d.meeting_id = m.id " \
            "WHERE d.date = %s AND m.user_id = %s"
    cursor.execute(query, (date, user_id))
    count = cursor.fetchone()[0]

    if count > 0:
        return jsonify({'message': 'Vous avez déjà une réunion planifiée à cette heure'}), 400

    # Insérer la nouvelle réunion dans la base de données
    query = "INSERT INTO meetings (user_id, creation_date) VALUES (%s, NOW())"
    cursor.execute(query, (user_id,))
    meeting_id = cursor.lastrowid

    query = "INSERT INTO dates (user_id, meeting_id, date) VALUES (%s, %s, %s)"
    for participant in participants:
        cursor.execute(query, (user_id, meeting_id, date))

    conn.commit()
    cursor.close()

    return jsonify({'message': 'Réunion créée avec succès'}), 200

if __name__ == '__main__':
    app.run()
