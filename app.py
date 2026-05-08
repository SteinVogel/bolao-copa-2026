from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from database import db
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_a = db.Column(db.String(100), nullable=False)
    team_b = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    phase = db.Column(db.String(50), nullable=False)

class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    score_a = db.Column(db.Integer, nullable=False)
    score_b = db.Column(db.Integer, nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    score_a = db.Column(db.Integer, nullable=False)
    score_b = db.Column(db.Integer, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_tables():
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', is_admin=True)
            admin.set_password('D/5=b-32/9')
            db.session.add(admin)
            db.session.commit()

create_tables()

@app.route('/')
@login_required
def index():
    games = Game.query.all()
    return render_template('index.html', games=games)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Credenciais inválidas')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if not username or not password:
            flash('Usuário e senha são obrigatórios')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('As senhas não combinam')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Este usuário já existe')
            return render_template('register.html')
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Cadastro realizado! Faça login')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/bet/<int:game_id>', methods=['GET', 'POST'])
@login_required
def bet(game_id):
    game = Game.query.get_or_404(game_id)
    existing_bet = Bet.query.filter_by(user_id=current_user.id, game_id=game_id).first()
    if request.method == 'POST':
        score_a = int(request.form['score_a'])
        score_b = int(request.form['score_b'])
        if existing_bet:
            existing_bet.score_a = score_a
            existing_bet.score_b = score_b
        else:
            new_bet = Bet(user_id=current_user.id, game_id=game_id, score_a=score_a, score_b=score_b)
            db.session.add(new_bet)
        db.session.commit()
        flash('Bet saved')
        return redirect(url_for('index'))
    return render_template('bet.html', game=game, bet=existing_bet)

@app.route('/ranking')
@login_required
def ranking():
    users = User.query.all()
    ranking_data = []
    for user in users:
        total_points = 0
        bets = Bet.query.filter_by(user_id=user.id).all()
        for bet in bets:
            result = Result.query.filter_by(game_id=bet.game_id).first()
            if result:
                if bet.score_a == result.score_a and bet.score_b == result.score_b:
                    total_points += 3
                elif (bet.score_a > bet.score_b and result.score_a > result.score_b) or \
                     (bet.score_a < bet.score_b and result.score_a < result.score_b) or \
                     (bet.score_a == bet.score_b and result.score_a == result.score_b):
                    total_points += 1
        ranking_data.append({'user': user, 'points': total_points})
    ranking_data.sort(key=lambda x: x['points'], reverse=True)
    return render_template('ranking.html', ranking=ranking_data)

# Admin routes
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    games = Game.query.all()
    users = User.query.all()
    return render_template('admin.html', games=games, users=users)

@app.route('/admin/add_game', methods=['POST'])
@login_required
def add_game():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    team_a = request.form['team_a']
    team_b = request.form['team_b']
    date_str = request.form['date']
    phase = request.form['phase']
    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
    game = Game(team_a=team_a, team_b=team_b, date=date, phase=phase)
    db.session.add(game)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/add_result/<int:game_id>', methods=['POST'])
@login_required
def add_result(game_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    score_a = int(request.form['score_a'])
    score_b = int(request.form['score_b'])
    result = Result(game_id=game_id, score_a=score_a, score_b=score_b)
    db.session.add(result)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/add_user', methods=['POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    username = request.form['username']
    password = request.form['password']
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)