from flask import *
from models import *
from migrate import *
import secrets
import time

app = Flask(__name__)
app.config.from_pyfile('settings.py')
db.init_app(app)
migrate.init_app(app, db)


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/wifi-list')
def wifi_list():
    return render_template('wifi-list.html')

@app.route('/add_confirm')
def add_confirm():
    return render_template('add_confirm.html')


@app.route('/pump/<int:id>')
def pump_view(id):
    pump = Pump.query.filter_by(id=id)[0]
    return render_template('pump.html', pump=pump)


@app.route('/api/register')
def register_user():
    data = request.args
    name = data.get('name')
    email = data.get('email')
    token = secrets.token_hex(nbytes=8)
    password = data.get('password')

    new_user = User(name=name, email=email, token=token,
                    password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'token': token})


@app.route('/api/login')
def login_user():
    data = request.args
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email, password=password).first()
    if user:
        return jsonify({'token': user.token})
    else:
        return jsonify({'message': 'Invalid email or password'}), 403


@app.route('/api/pumps')
def get_user_pumps():
    token = request.args['token']
    try:
        user = User.query.filter_by(token=token)[0]
        pumps = [{'id': pump.id, 
                  'name': pump.name, 
                  'level': pump.level, 
                  'current': pump.current, 
                  'volt': pump.volt,
                  'state_one': pump.state_one, 
                  'state_two': pump.state_two, 
                  'latest_modified': pump.latest_modified,
                  'now': str(int(time.time()))} for pump in user.pumps]
        return jsonify(pumps)
    except:
        return jsonify({'message': 'User not found'}), 404


@app.route('/api/pumps/get')
def get_user_pump():
    data = request.args
    token = data['token']
    user = User.query.filter_by(token=token)[0]
    pump = Pump.query.filter_by(user_id=user.id, name=data['name'])[0]
    if pump:
        pump_data = {
            'id': pump.id,
            'name': pump.name,
            'level': pump.level,
            'current': pump.current,
            'volt': pump.volt,
            'state_one': pump.state_one,
            'state_two': pump.state_two,
            'latest_modified': pump.latest_modified, 
            'now': str(int(time.time()))
        }
        return jsonify(pump_data)
    else:
        return jsonify({'message': 'Pump not found'}), 404


@app.route('/api/pumps/update')
def update_user_pump():
    data = request.args
    token = data['token']
    user = User.query.filter_by(token=token)[0]
    pump = Pump.query.filter_by(user_id=user.id, name=data['name'])[0]
    if pump:
        pump.name = data.get('name', pump.name)
        pump.level = data.get('level', pump.level)
        pump.current = data.get('current', pump.current)
        pump.volt = data.get('volt', pump.volt)
        pump.state_one = data.get('state_one', pump.state_one)
        pump.state_two = data.get('state_two', pump.state_two)

        if not data.get('state_one'):
            pump.latest_modified = int(time.time())

        db.session.commit()
        return jsonify({'message': 'Pump updated successfully'})
    else:
        return jsonify({'message': 'Pump not found'}), 404


@app.route('/api/pumps/add')
def add_user_pump():
    data = request.args
    token = request.args['token']
    user = User.query.filter_by(token=token)[0]
    if not user.token == token:
        return jsonify({'message': 'Not authorized'}), 401

    try:
        Pump.query.filter_by(name=data.get('name'), user_id=user.id)[0]
    except:
        pump = Pump(name=data.get('name'), level=0, current=0,
                    volt=0, state_one=0, state_two=0,
                    user=user)
        db.session.add(pump)
        db.session.commit()
    return jsonify({'message': 'Pump added successfully'})


@app.route('/api/pumps/<int:pump_id>/remove')
def remove_user_pump(pump_id):
    pump = Pump.query.get(pump_id)
    token = request.args['token']
    user = User.query.filter_by(token=token)[0]
    if not user.id == pump.user_id:
        return jsonify({'message': 'Not authorized'}), 401
    if pump:
        db.session.delete(pump)
        db.session.commit()
        return jsonify({'message': 'Pump removed successfully'})
    else:
        return jsonify({'message': 'Pump not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
