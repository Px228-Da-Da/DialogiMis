from flask import Flask, render_template, request, redirect, session, jsonify, url_for, flash
from flask_socketio import SocketIO, emit
import pyrebase
import pyrebase
import asyncio
from requests.exceptions import HTTPError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Конфигурационные данные для Firebase
config = {
    'apiKey': "AIzaSyBJVECLZ5_7BOrBRjl8yVk1lz7AP1Q3Ot4",
    'authDomain': "dialogimis.firebaseapp.com",
    'projectId': "dialogimis",
    'storageBucket': "dialogimis.appspot.com",
    'messagingSenderId': "561942559385",
    'appId': "1:561942559385:web:a44b7192b9deb8ab899608",
    'measurementId': "G-P26HK6H3WP",
    'databaseURL': 'https://dialogimis-default-rtdb.firebaseio.com/'
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

# Создайте класс модели Message для хранения сообщений в базе данных
class Message:
    def __init__(self, sender, receiver, message):
        self.sender = sender
        self.receiver = receiver
        self.message = message

# Создайте класс модели User для хранения пользователей в базе данных
class User:
    def __init__(self, username, email, email_verified):
        self.username = username
        self.email = email
        self.email_verified = email_verified


# Обработчик WebSocket-сообщений для отправки сообщений
@socketio.on('sendMessage')
def handle_send_message(data):
    sender = data['sender']
    receiver = data['receiver']
    message = data['message']
    
    # Сохраняем сообщение в базе данных Firebase
    message_data = {
        'sender': sender,
        'receiver': receiver,
        'message': message
    }
    db.child('messages').push(message_data)

    # Отправляем сообщение всем подключенным клиентам, включая отправителя и получателя
    emit('receiveMessage', {'sender': sender, 'receiver': receiver, 'message': message}, broadcast=True)



@socketio.on('signup')
def handle_signup(data):
    email = data['email']
    password = data['password']
    username = data['username']

    try:
        user = auth.create_user_with_email_and_password(email, password)
        auth.send_email_verification(user['idToken'])
        flash('Регистрация успешна! Подтвердите свой email.')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(wait_for_email_verification(request.sid, email, password, username))

    except Exception as e:
        socketio.emit('email_verification_error', str(e), room=request.sid)


@app.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
        return render_template('home.html')
    else:
        return render_template('index.html', message="lalala")


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            username = request.form['username']

            user = auth.create_user_with_email_and_password(email, password)
            auth.send_email_verification(user['idToken'])

            # Сохраняем информацию о пользователе в базе данных Firebase
            user_info = {
                'email': email,
                'username': username,
                'password': password
            }
            db.child('users').child(user['localId']).set(user_info)

            # Запускаем функцию ожидания подтверждения по электронной почте с передачей всех необходимых параметров
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(wait_for_email_verification(request.sid, email, password, username))

            # Возвращаем пользователя на главную страницу после успешной регистрации
            return redirect(url_for('index'))
        except Exception as e:
            # Если произошла ошибка, возвращаем пользователя на страницу регистрации с сообщением об ошибке
            return render_template('register.html', message="Ошибка регистрации: {}".format(e))
    else:
        return render_template('register.html')


async def wait_for_email_verification(sid, email, password, username):
    while True:
        try:
            user = auth.sign_in_with_email_and_password(email, password)

            user_info = auth.get_account_info(user['idToken'])
            email_verified = user_info['users'][0]['emailVerified']
            
            if email_verified:
                socketio.emit('email_verified', room=sid)
                # Добавление информации о пользователе в базу данных Firebase
                db.child("users").child(user['localId']).set({
                    "email": email,
                    "password": password,
                    "username": username
                })
                session['logged_in'] = True
                return redirect(url_for('index'))
            else:
                socketio.emit('email_not_verified', room=sid)
        except Exception as e:
            socketio.emit('email_verification_error', str(e), room=sid)
            break
        await asyncio.sleep(0.5)  # Указываете время задержки в секундах


@app.route('/email_verified')
def email_verified():
    if session.get('logged_in'):
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))  # Или любую другую страницу, если пользователь не вошел в систему


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            user = auth.sign_in_with_email_and_password(email, password)
            session['email'] = email  # Store the email in the session
            session['logged_in'] = True
            session['idToken'] = user['idToken']  # Store the ID token in the session
            return redirect(url_for('index'))
        except Exception as e:
            error_message = e.args[1]
            return render_template('index.html', message=error_message)
    else:
        return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    session.pop('email', None)
    session.pop('idToken', None)  # Remove the ID token from the session
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        users = User.query.filter(User.username.ilike(f'%{search_query}%')).all()
        user_list = [{'username': user.username} for user in users]
        return jsonify({'users': user_list})
    return jsonify({'message': 'Method not allowed'})

if __name__ == '__main__':
    app.secret_key = "ThisIsNotASecret:p"
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)



# from flask import Flask, render_template, request


# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'  # Замените 'your_secret_key' на ваш секретный ключ Flask
# socketio = SocketIO(app)

# firebase = pyrebase.initialize_app(config)
# auth = firebase.auth()

# async def wait_for_email_verification(sid, user):
#     while True:
#         try:
#             user_info = auth.get_account_info(user['idToken'])
#             email_verified = user_info['users'][0]['emailVerified']
#             if email_verified:
#                 socketio.emit('email_verified', room=sid)
#                 break
#             else:
#                 socketio.emit('email_not_verified', room=sid)
#         except Exception as e:
#             socketio.emit('email_verification_error', str(e), room=sid)
#             break
#         await asyncio.sleep(5)  # Проверяем каждые 5 секунд

# @app.route('/')
# def index():
#     return render_template('signup.html')

# @socketio.on('signup')
# def handle_signup(data):
#     email = data['email']
#     password = data['password']

#     try:
#         user = auth.create_user_with_email_and_password(email, password)
#         auth.send_email_verification(user['idToken'])
#         flash('Регистрация успешна! Подтвердите свой email.')

#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         loop.run_until_complete(wait_for_email_verification(request.sid, user))

#     except Exception as e:
#         socketio.emit('registration_error', str(e), room=request.sid)

# if __name__ == '__main__':
#     socketio.run(app, debug=True)
