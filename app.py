from flask import Flask, url_for, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)
db = SQLAlchemy(app)

# Остальной код вашего Flask-приложения здесь...

# Создайте класс модели Message для хранения сообщений в базе данных
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100))
    receiver = db.Column(db.String(100))
    message = db.Column(db.String(500))

    def __init__(self, sender, receiver, message):
        self.sender = sender
        self.receiver = receiver
        self.message = message

# Обработчик WebSocket-сообщений для отправки сообщений
@socketio.on('sendMessage')
def handle_send_message(data):
    sender = data['sender']
    receiver = data['receiver']
    message = data['message']
    
    # Сохраняем сообщение в базе данных
    new_message = Message(sender=sender, receiver=receiver, message=message)
    db.session.add(new_message)
    db.session.commit()
    
    # Отправляем сообщение всем подключенным клиентам, включая отправителя и получателя
    emit('receiveMessage', {'sender': sender, 'receiver': receiver, 'message': message}, broadcast=True)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password


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
            username = request.form['username']
            password = request.form['password']
            db.session.add(User(username=username, password=password))
            db.session.commit()
            session['username'] = username  # Store the username in the session
            session['logged_in'] = True
            return redirect(url_for('index'))
        except:
            return render_template('index.html', message="User Already Exists")
    else:
        return render_template('register.html')



@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        u = request.form['username']
        p = request.form['password']
        data = User.query.filter_by(username=u, password=p).first()
        if data is not None:
            session['username'] = u  # Store the username in the session
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('index.html', message="Incorrect Details")




@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
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
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='0.0.0.0', port=5500)

