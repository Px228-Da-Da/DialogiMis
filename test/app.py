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
    # message_data = {
    #     'sender': sender,
    #     'receiver': receiver,
    #     'message': message
    # }
    # db.child('messages').push(message_data)

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
            session['logged_in'] = True
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
                print("email_verified")
                session['email'] = email  # Store the email in the session
                session['username'] = username
                session['logged_in'] = True
                session['idToken'] = user['idToken']  # Store the ID token in the session
                return redirect(url_for('index'))
            else:
                socketio.emit('email_not_verified', room=sid)
        except Exception as e:
            socketio.emit('email_verification_error', str(e), room=sid)
            break
        await asyncio.sleep(0.05)  # Указываете время задержки в секундах

@app.route('/update_session', methods=['POST'])
def update_session():
    if request.method == 'POST':
        data = request.json
        logged_in = data.get('logged_in')
        if logged_in:
            session['logged_in'] = True
            return jsonify({'message': 'Session updated successfully'}), 200
        else:
            return jsonify({'message': 'Failed to update session'}), 400
    else:
        return jsonify({'message': 'Method not allowed'}), 405





def process_login_error(error_data):
    try:
        if 'code' in error_data and 'message' in error_data:
            if error_data['code'] == 400:
                if error_data['message'] == 'INVALID_LOGIN_CREDENTIALS':
                    return "Неправильний email або пароль."
                # Добавьте другие условия для обработки разных ошибок при входе в систему
            return "Під час входу в систему виникла помилка: {}".format(error_data['message'])
    except Exception:
        pass
    return "Виникла помилка при вході в систему."





@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            
            # Проверяем, существует ли пользователь с указанным email и паролем
            user = auth.sign_in_with_email_and_password(email, password)
            
            # Получаем информацию о пользователе, включая его имя (username)
            user_info = db.child('users').child(user['localId']).get().val()
            username = user_info.get('username')
            
            # Если пользователь существует, сохраняем информацию о сессии и перенаправляем на главную страницу
            session['email'] = email  # Сохраняем email в сессии
            session['username'] = username  # Сохраняем имя пользователя в сессии
            session['logged_in'] = True
            session['idToken'] = user['idToken']  # Сохраняем ID токен в сессии
            return redirect(url_for('index'))
        except HTTPError as e:
            if e.response is not None:
                try:
                    error_message = e.response.json().get('error', {}).get('message', '')
                    if error_message == 'EMAIL_NOT_FOUND':
                        error = "Пользователь с таким email не найден"
                    elif error_message == 'INVALID_PASSWORD':
                        error = "Неверный пароль"
                    elif error_message == 'TOO_MANY_ATTEMPTS_TRY_LATER ':
                        error = "Учетная запись пользователя отключена"
                    else:
                        error = "Ошибка при входе в систему"
                except Exception as e:
                    error = "Ошибка при входе в систему"
            else:
                error = "Пользователь с таким email не найден ИЛИ Неверный пароль Учетная запись временно отключена из-за множества неудачных попыток входа"
    return render_template('login.html', error=error)





@app.route('/email_verified')
def email_verified():
    if session.get('logged_in'):
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))  # Или любую другую страницу, если пользователь не вошел в систему


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
        
        # Выполняем поиск пользователей в базе данных Firebase
        users = []
        try:
            # Получаем данные пользователей из Firebase
            firebase_users = db.child("users").get().val()
            
            # Перебираем пользователей и добавляем их в список, если их имя соответствует запросу
            if firebase_users:
                for user_id, user_data in firebase_users.items():
                    if 'username' in user_data and search_query.lower() in user_data['username'].lower():
                        users.append({'username': user_data['username']})
        except Exception as e:
            # Обработка ошибок при запросе к базе данных Firebase
            return jsonify({'message': 'Error occurred while searching users'}), 500
        
        return jsonify({'users': users})
    return jsonify({'message': 'Method not allowed'})


if __name__ == '__main__':
    app.secret_key = "ThisIsNotASecret:p"
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

