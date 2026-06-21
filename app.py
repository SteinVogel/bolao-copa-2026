from datetime import datetime, timedelta, timezone
import os
from collections import Counter, OrderedDict
import unicodedata
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from sqlalchemy import inspect, text

from database import db

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

database_url = os.environ.get('DATABASE_URL')
running_on_railway = any(
    os.environ.get(key)
    for key in ('RAILWAY_ENVIRONMENT', 'RAILWAY_ENVIRONMENT_NAME', 'RAILWAY_PROJECT_ID', 'RAILWAY_SERVICE_ID')
)

if database_url and database_url.strip().startswith('${{'):
    raise RuntimeError('DATABASE_URL do Railway nao foi resolvida. Configure DATABASE_URL=${{Postgres.DATABASE_URL}} no servico do app.')

if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

if not database_url:
    railway_volume_path = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH')
    if railway_volume_path:
        os.makedirs(railway_volume_path, exist_ok=True)
        database_url = f"sqlite:///{os.path.join(railway_volume_path, 'database.db')}"
    else:
        if running_on_railway:
            raise RuntimeError('DATABASE_URL ausente no Railway. Configure o app para usar o Postgres antes do deploy.')
        database_url = 'sqlite:///database.db'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

try:
    APP_TIMEZONE = ZoneInfo(os.environ.get('APP_TIMEZONE', 'America/Sao_Paulo'))
except ZoneInfoNotFoundError:
    APP_TIMEZONE = timezone(timedelta(hours=-3), 'America/Sao_Paulo')

WORLD_CUP_2026_TEAMS = [
    'África do Sul',
    'Alemanha',
    'Argélia',
    'Argentina',
    'Arábia Saudita',
    'Austrália',
    'Áustria',
    'Bélgica',
    'Bósnia e Herzegovina',
    'Brasil',
    'Cabo Verde',
    'Canadá',
    'Colômbia',
    'Coreia do Sul',
    'Costa do Marfim',
    'Croácia',
    'Curaçao',
    'Egito',
    'Equador',
    'Escócia',
    'Espanha',
    'Estados Unidos',
    'França',
    'Gana',
    'Haiti',
    'Inglaterra',
    'Irã',
    'Iraque',
    'Japão',
    'Jordânia',
    'Marrocos',
    'México',
    'Noruega',
    'Nova Zelândia',
    'Países Baixos',
    'Panamá',
    'Paraguai',
    'Portugal',
    'Qatar',
    'RD Congo',
    'República Tcheca',
    'Senegal',
    'Suécia',
    'Suíça',
    'Tunísia',
    'Turquia',
    'Uruguai',
    'Uzbequistão',
]

WORLD_CUP_2026_GROUP_STAGE_MATCHES = [
    ('2026-06-11T16:00', 'Grupo A', 'México', 'África do Sul'),
    ('2026-06-11T19:00', 'Grupo A', 'Coreia do Sul', 'República Tcheca'),
    ('2026-06-18T16:00', 'Grupo A', 'República Tcheca', 'África do Sul'),
    ('2026-06-18T19:00', 'Grupo A', 'México', 'Coreia do Sul'),
    ('2026-06-24T16:00', 'Grupo A', 'República Tcheca', 'México'),
    ('2026-06-24T16:00', 'Grupo A', 'África do Sul', 'Coreia do Sul'),
    ('2026-06-12T16:00', 'Grupo B', 'Canadá', 'Suíça'),
    ('2026-06-13T16:00', 'Grupo B', 'Qatar', 'Bósnia e Herzegovina'),
    ('2026-06-18T22:00', 'Grupo B', 'Bósnia e Herzegovina', 'Suíça'),
    ('2026-06-18T23:00', 'Grupo B', 'Canadá', 'Qatar'),
    ('2026-06-24T19:00', 'Grupo B', 'Bósnia e Herzegovina', 'Canadá'),
    ('2026-06-24T19:00', 'Grupo B', 'Suíça', 'Qatar'),
    ('2026-06-13T18:00', 'Grupo C', 'Haiti', 'Escócia'),
    ('2026-06-13T19:00', 'Grupo C', 'Brasil', 'Marrocos'),
    ('2026-06-19T19:00', 'Grupo C', 'Escócia', 'Marrocos'),
    ('2026-06-20T21:00', 'Grupo C', 'Brasil', 'Haiti'),
    ('2026-06-24T18:00', 'Grupo C', 'Escócia', 'Brasil'),
    ('2026-06-24T18:00', 'Grupo C', 'Marrocos', 'Haiti'),
    ('2026-06-12T19:00', 'Grupo D', 'Estados Unidos', 'Paraguai'),
    ('2026-06-13T19:00', 'Grupo D', 'Austrália', 'Turquia'),
    ('2026-06-19T22:00', 'Grupo D', 'Turquia', 'Paraguai'),
    ('2026-06-21T19:00', 'Grupo D', 'Estados Unidos', 'Austrália'),
    ('2026-06-26T18:00', 'Grupo D', 'Turquia', 'Estados Unidos'),
    ('2026-06-26T18:00', 'Grupo D', 'Paraguai', 'Austrália'),
    ('2026-06-14T16:00', 'Grupo E', 'Costa do Marfim', 'Equador'),
    ('2026-06-14T19:00', 'Grupo E', 'Alemanha', 'Curaçao'),
    ('2026-06-20T16:00', 'Grupo E', 'Alemanha', 'Costa do Marfim'),
    ('2026-06-20T19:00', 'Grupo E', 'Equador', 'Curaçao'),
    ('2026-06-25T18:00', 'Grupo E', 'Equador', 'Alemanha'),
    ('2026-06-25T18:00', 'Grupo E', 'Curaçao', 'Costa do Marfim'),
    ('2026-06-14T22:00', 'Grupo F', 'Países Baixos', 'Japão'),
    ('2026-06-14T23:00', 'Grupo F', 'Suécia', 'Tunísia'),
    ('2026-06-20T22:00', 'Grupo F', 'Países Baixos', 'Suécia'),
    ('2026-06-20T23:00', 'Grupo F', 'Tunísia', 'Japão'),
    ('2026-06-25T21:00', 'Grupo F', 'Tunísia', 'Países Baixos'),
    ('2026-06-25T21:00', 'Grupo F', 'Japão', 'Suécia'),
    ('2026-06-15T16:00', 'Grupo G', 'Irã', 'Nova Zelândia'),
    ('2026-06-15T19:00', 'Grupo G', 'Bélgica', 'Egito'),
    ('2026-06-21T16:00', 'Grupo G', 'Bélgica', 'Irã'),
    ('2026-06-21T19:00', 'Grupo G', 'Nova Zelândia', 'Egito'),
    ('2026-06-25T22:00', 'Grupo G', 'Nova Zelândia', 'Bélgica'),
    ('2026-06-25T22:00', 'Grupo G', 'Egito', 'Irã'),
    ('2026-06-15T22:00', 'Grupo H', 'Arábia Saudita', 'Uruguai'),
    ('2026-06-15T23:00', 'Grupo H', 'Espanha', 'Cabo Verde'),
    ('2026-06-21T22:00', 'Grupo H', 'Espanha', 'Arábia Saudita'),
    ('2026-06-21T23:00', 'Grupo H', 'Uruguai', 'Cabo Verde'),
    ('2026-06-26T16:00', 'Grupo H', 'Uruguai', 'Espanha'),
    ('2026-06-26T16:00', 'Grupo H', 'Cabo Verde', 'Arábia Saudita'),
    ('2026-06-16T16:00', 'Grupo I', 'França', 'Senegal'),
    ('2026-06-16T19:00', 'Grupo I', 'Iraque', 'Noruega'),
    ('2026-06-22T16:00', 'Grupo I', 'França', 'Iraque'),
    ('2026-06-22T19:00', 'Grupo I', 'Noruega', 'Senegal'),
    ('2026-06-26T19:00', 'Grupo I', 'Noruega', 'França'),
    ('2026-06-26T19:00', 'Grupo I', 'Senegal', 'Iraque'),
    ('2026-06-16T22:00', 'Grupo J', 'Argentina', 'Argélia'),
    ('2026-06-16T23:00', 'Grupo J', 'Áustria', 'Jordânia'),
    ('2026-06-22T22:00', 'Grupo J', 'Argentina', 'Áustria'),
    ('2026-06-22T23:00', 'Grupo J', 'Jordânia', 'Argélia'),
    ('2026-06-27T16:00', 'Grupo J', 'Jordânia', 'Argentina'),
    ('2026-06-27T16:00', 'Grupo J', 'Argélia', 'Áustria'),
    ('2026-06-17T16:00', 'Grupo K', 'Portugal', 'RD Congo'),
    ('2026-06-17T19:00', 'Grupo K', 'Uzbequistão', 'Colômbia'),
    ('2026-06-23T16:00', 'Grupo K', 'Portugal', 'Uzbequistão'),
    ('2026-06-23T19:00', 'Grupo K', 'Colômbia', 'RD Congo'),
    ('2026-06-27T19:00', 'Grupo K', 'Colômbia', 'Portugal'),
    ('2026-06-27T19:00', 'Grupo K', 'RD Congo', 'Uzbequistão'),
    ('2026-06-17T22:00', 'Grupo L', 'Gana', 'Panamá'),
    ('2026-06-17T23:00', 'Grupo L', 'Inglaterra', 'Croácia'),
    ('2026-06-23T22:00', 'Grupo L', 'Inglaterra', 'Gana'),
    ('2026-06-23T23:00', 'Grupo L', 'Panamá', 'Croácia'),
    ('2026-06-27T22:00', 'Grupo L', 'Panamá', 'Inglaterra'),
    ('2026-06-27T22:00', 'Grupo L', 'Croácia', 'Gana'),
]

PHASE_POINT_WEIGHTS = {
    'grupos': 1,
    '1/16 de final': 2,
    '1/16 final': 2,
    '1/8 de final': 3,
    '1/8 final': 3,
    '1/4 de final': 4,
    '1/4 final': 4,
    'semifinal': 5,
    'disputa do 3o lugar': 6,
    'final': 7,
}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    champion_pick = db.Column(db.String(100), nullable=True)
    runner_up_pick = db.Column(db.String(100), nullable=True)
    third_place_pick = db.Column(db.String(100), nullable=True)
    terms_accepted_at = db.Column(db.DateTime, nullable=True)
    hide_terms_notice = db.Column(db.Boolean, default=False)

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
    results = db.relationship('Result', backref='game', lazy=True)


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


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=True)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def create_tables():
    with app.app_context():
        db.create_all()
        migrate_schema()
        if not User.query.filter_by(username='admin').first():
            admin = User(username=os.environ.get('ADMIN_USERNAME', 'admin'), is_admin=True)
            admin.set_password(os.environ.get('ADMIN_PASSWORD', 'D/5=b-32/9'))
            db.session.add(admin)
            db.session.commit()


def migrate_schema():
    inspector = inspect(db.engine)
    if 'user' not in inspector.get_table_names():
        return

    columns = inspector.get_columns('user')
    column_names = {column['name'] for column in columns}
    password_hash_column = next((column for column in columns if column['name'] == 'password_hash'), None)
    if password_hash_column and getattr(password_hash_column['type'], 'length', None) and password_hash_column['type'].length < 255:
        if db.engine.dialect.name == 'postgresql':
            db.session.execute(text('ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(255)'))
            db.session.commit()
    if 'champion_pick' not in column_names:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN champion_pick VARCHAR(100)'))
    if 'runner_up_pick' not in column_names:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN runner_up_pick VARCHAR(100)'))
    if 'third_place_pick' not in column_names:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN third_place_pick VARCHAR(100)'))
    if 'terms_accepted_at' not in column_names:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN terms_accepted_at TIMESTAMP'))
    if 'hide_terms_notice' not in column_names:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN hide_terms_notice BOOLEAN DEFAULT FALSE'))
    if {'champion_pick', 'runner_up_pick', 'third_place_pick', 'terms_accepted_at', 'hide_terms_notice'} - column_names:
        db.session.commit()


create_tables()


def normalize_phase_text(phase):
    without_accents = unicodedata.normalize('NFKD', phase).encode('ascii', 'ignore').decode('ascii')
    return ' '.join(without_accents.lower().split())


def get_phase_point_weight(phase):
    normalized_phase = normalize_phase_text(phase)
    if normalized_phase.startswith('grupo '):
        return PHASE_POINT_WEIGHTS['grupos']
    return PHASE_POINT_WEIGHTS[normalized_phase]


def calculate_base_points(bet, result):
    if bet.score_a == result.score_a and bet.score_b == result.score_b:
        return 5

    bet_outcome = (bet.score_a > bet.score_b) - (bet.score_a < bet.score_b)
    result_outcome = (result.score_a > result.score_b) - (result.score_a < result.score_b)
    if bet_outcome == result_outcome:
        return 3

    if bet.score_a == result.score_a or bet.score_b == result.score_b:
        return 1

    return 0


def calculate_points(bet, result, game=None):
    base_points = calculate_base_points(bet, result)
    point_weight = get_phase_point_weight(game.phase if game else result.game.phase)
    return base_points * point_weight


def calculate_bet_stats(bet, result, game=None):
    base_points = calculate_base_points(bet, result)
    points = calculate_points(bet, result, game)
    return {
        'points': points,
        'max_points': 5 * get_phase_point_weight(game.phase if game else result.game.phase),
        'exact_scores': 1 if base_points == 5 else 0,
        'correct_outcomes': 1 if base_points == 3 else 0,
        'partial_scores': 1 if base_points == 1 else 0,
        'errors': 1 if base_points == 0 else 0,
    }


def get_team_names():
    teams = set(WORLD_CUP_2026_TEAMS)
    for game in Game.query.all():
        teams.add(game.team_a)
        teams.add(game.team_b)
    return sorted(teams, key=normalize_sort_text)


def normalize_sort_text(value):
    without_accents = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    return without_accents.lower()


def get_setting(key):
    setting = Setting.query.filter_by(key=key).first()
    return setting.value if setting else None


def set_setting(key, value):
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.session.add(setting)
    db.session.commit()


def get_official_champion():
    return get_setting('official_champion')


def get_official_runner_up():
    return get_setting('official_runner_up')


def get_official_third_place():
    return get_setting('official_third_place')


def has_final_standings_pick(user):
    return bool(user.champion_pick and user.runner_up_pick and user.third_place_pick)


def calculate_final_standings_bonus(user, official_champion, official_runner_up, official_third_place):
    champion_bonus = 150 if official_champion and user.champion_pick == official_champion else 0
    runner_up_bonus = 100 if official_runner_up and user.runner_up_pick == official_runner_up else 0
    third_place_bonus = 50 if official_third_place and user.third_place_pick == official_third_place else 0
    return {
        'champion_bonus': champion_bonus,
        'runner_up_bonus': runner_up_bonus,
        'third_place_bonus': third_place_bonus,
        'total': champion_bonus + runner_up_bonus + third_place_bonus,
    }


def calculate_user_performance(user):
    official_champion = get_official_champion()
    official_runner_up = get_official_runner_up()
    official_third_place = get_official_third_place()
    bets = Bet.query.filter_by(user_id=user.id).all()

    bet_points = 0
    exact_scores = 0
    correct_outcomes = 0
    partial_scores = 0
    errors = 0
    evaluated_bets = 0
    max_bet_points = 0

    for bet_item in bets:
        result = Result.query.filter_by(game_id=bet_item.game_id).first()
        if not result:
            continue

        stats = calculate_bet_stats(bet_item, result)
        evaluated_bets += 1
        bet_points += stats['points']
        max_bet_points += stats['max_points']
        exact_scores += stats['exact_scores']
        correct_outcomes += stats['correct_outcomes']
        partial_scores += stats['partial_scores']
        errors += stats['errors']

    final_bonus = calculate_final_standings_bonus(
        user,
        official_champion,
        official_runner_up,
        official_third_place,
    )
    total_points = bet_points + final_bonus['total']
    max_final_bonus = 0
    if official_champion:
        max_final_bonus += 150
    if official_runner_up:
        max_final_bonus += 100
    if official_third_place:
        max_final_bonus += 50
    max_points = max_bet_points + max_final_bonus
    success_rate = round((total_points / max_points) * 100, 1) if max_points else 0

    return {
        'points': total_points,
        'bet_points': bet_points,
        'champion_bonus': final_bonus['champion_bonus'],
        'runner_up_bonus': final_bonus['runner_up_bonus'],
        'third_place_bonus': final_bonus['third_place_bonus'],
        'final_bonus': final_bonus['total'],
        'exact_scores': exact_scores,
        'correct_outcomes': correct_outcomes,
        'partial_scores': partial_scores,
        'errors': errors,
        'evaluated_bets': evaluated_bets,
        'total_bets': len(bets),
        'success_rate': success_rate,
        'max_points': max_points,
    }


def format_game_label(game):
    return f'{game.team_a} vs {game.team_b}'


def get_admin_statistics():
    users = User.query.filter_by(is_admin=False).all()
    games = Game.query.order_by(Game.date).all()
    bets = Bet.query.all()
    results = Result.query.all()

    user_count = len(users)
    user_ids = {user.id for user in users}
    evaluated_game_ids = {result.game_id for result in results}
    evaluated_games = [game for game in games if game.id in evaluated_game_ids]

    bets_by_user = {user.id: [] for user in users}
    bets_by_game = {game.id: [] for game in games}
    for bet_item in bets:
        if bet_item.user_id in user_ids:
            bets_by_user.setdefault(bet_item.user_id, []).append(bet_item)
            bets_by_game.setdefault(bet_item.game_id, []).append(bet_item)

    result_by_game = {result.game_id: result for result in results}
    active_participants = sum(1 for user_bets in bets_by_user.values() if user_bets)
    all_evaluated_participants = 0
    if evaluated_game_ids:
        all_evaluated_participants = sum(
            1
            for user_bets in bets_by_user.values()
            if evaluated_game_ids.issubset({bet_item.game_id for bet_item in user_bets})
        )

    average_bets = round(sum(len(user_bets) for user_bets in bets_by_user.values()) / user_count, 1) if user_count else 0

    totals = {
        'exact_scores': 0,
        'correct_outcomes': 0,
        'partial_scores': 0,
        'errors': 0,
    }
    game_stats = []
    for game in evaluated_games:
        result = result_by_game[game.id]
        game_bets = bets_by_game.get(game.id, [])
        score_counter = Counter((bet_item.score_a, bet_item.score_b) for bet_item in game_bets)
        stats = {
            'game': game,
            'label': format_game_label(game),
            'date': game.date,
            'result': result,
            'bets_count': len(game_bets),
            'exact_scores': 0,
            'correct_outcomes': 0,
            'partial_scores': 0,
            'errors': 0,
            'points': 0,
            'average_points': 0,
            'most_common_score': None,
            'most_common_score_count': 0,
        }

        for bet_item in game_bets:
            bet_stats = calculate_bet_stats(bet_item, result, game)
            stats['points'] += bet_stats['points']
            stats['exact_scores'] += bet_stats['exact_scores']
            stats['correct_outcomes'] += bet_stats['correct_outcomes']
            stats['partial_scores'] += bet_stats['partial_scores']
            stats['errors'] += bet_stats['errors']

        if game_bets:
            stats['average_points'] = round(stats['points'] / len(game_bets), 1)
        if score_counter:
            most_common_score, most_common_count = score_counter.most_common(1)[0]
            stats['most_common_score'] = f'{most_common_score[0]} - {most_common_score[1]}'
            stats['most_common_score_count'] = most_common_count

        totals['exact_scores'] += stats['exact_scores']
        totals['correct_outcomes'] += stats['correct_outcomes']
        totals['partial_scores'] += stats['partial_scores']
        totals['errors'] += stats['errors']
        game_stats.append(stats)

    games_with_bets = [stats for stats in game_stats if stats['bets_count']]

    return {
        'total_participants': user_count,
        'active_participants': active_participants,
        'all_evaluated_participants': all_evaluated_participants,
        'average_bets': average_bets,
        'evaluated_games_count': len(evaluated_games),
        'most_exact_game': max(game_stats, key=lambda stats: stats['exact_scores'], default=None),
        'least_exact_game': min(game_stats, key=lambda stats: stats['exact_scores'], default=None),
        'easiest_game': max(games_with_bets, key=lambda stats: stats['average_points'], default=None),
        'hardest_game': min(games_with_bets, key=lambda stats: stats['average_points'], default=None),
        'totals': totals,
        'game_stats': sorted(game_stats, key=lambda stats: stats['date']),
    }


def is_game_closed(game):
    return game.date <= get_current_time()


def should_move_game_to_end(game, now):
    return game.date + timedelta(hours=3) <= now


def get_current_time():
    return datetime.now(APP_TIMEZONE).replace(tzinfo=None)


def is_admin_user():
    return current_user.is_authenticated and current_user.is_admin


def find_user_by_username(username):
    return User.query.filter(db.func.lower(User.username) == username.lower()).first()


@app.route('/')
@login_required
def index():
    if current_user.is_admin:
        return redirect(url_for('admin'))

    now = get_current_time()
    games = Game.query.order_by(Game.date).all()
    games.sort(key=lambda game: (should_move_game_to_end(game, now), game.date))
    user_bets = {
        bet_item.game_id: bet_item
        for bet_item in Bet.query.filter_by(user_id=current_user.id).all()
    }
    game_results = {
        result_item.game_id: result_item
        for result_item in Result.query.all()
    }
    bet_points = {}
    for game_id, bet_item in user_bets.items():
        result_item = game_results.get(game_id)
        if result_item:
            bet_points[game_id] = calculate_points(bet_item, result_item)
    grouped_games = OrderedDict()
    for game in games:
        game_day = game.date.date()
        grouped_games.setdefault(game_day, []).append(game)
    return render_template(
        'index.html',
        grouped_games=grouped_games,
        user_bets=user_bets,
        game_results=game_results,
        bet_points=bet_points,
        now=now,
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = find_user_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin'))
            if should_show_terms_notice(user):
                return redirect(url_for('terms'))
            return redirect(url_for('index'))
        flash('Credenciais inválidas')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not password:
            flash('Usuário e senha são obrigatórios')
            return render_template('register.html')

        if len(username) < 3:
            flash('O usuário deve ter pelo menos 3 caracteres')
            return render_template('register.html')

        if len(password) < 4:
            flash('A senha deve ter pelo menos 4 caracteres')
            return render_template('register.html')

        if password != confirm_password:
            flash('As senhas não combinam')
            return render_template('register.html')

        if find_user_by_username(username):
            flash('Este usuário já existe')
            return render_template('register.html')

        user = User(username=username, is_admin=False)
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


def should_show_terms_notice(user):
    return not user.terms_accepted_at or not user.hide_terms_notice


def participant_home_url():
    if not has_final_standings_pick(current_user):
        return url_for('champion_pick')
    return url_for('index')


@app.route('/termos', methods=['GET', 'POST'])
@login_required
def terms():
    if request.method == 'POST':
        if current_user.is_admin:
            return redirect(url_for('admin'))

        current_user.terms_accepted_at = get_current_time()
        current_user.hide_terms_notice = bool(request.form.get('hide_terms_notice'))
        db.session.commit()
        flash('Termos de uso confirmados')
        return redirect(participant_home_url())

    return render_template('terms.html')


@app.route('/champion-pick', methods=['GET', 'POST'])
@login_required
def champion_pick():
    if current_user.is_admin:
        return redirect(url_for('admin'))

    team_names = get_team_names()
    if request.method == 'POST':
        if has_final_standings_pick(current_user):
            flash('Seus palpites finais já foram confirmados e não podem ser alterados')
            return redirect(url_for('index'))

        selected_champion = request.form['champion'].strip()
        selected_runner_up = request.form['runner_up'].strip()
        selected_third_place = request.form['third_place'].strip()
        selected_teams = {selected_champion, selected_runner_up, selected_third_place}

        if any(team_name not in team_names for team_name in selected_teams):
            flash('Selecione seleções válidas')
            return render_template('champion_pick.html', team_names=team_names)

        if len(selected_teams) < 3:
            flash('Campeão, vice-campeão e terceiro lugar devem ser seleções diferentes')
            return render_template('champion_pick.html', team_names=team_names)

        current_user.champion_pick = selected_champion
        current_user.runner_up_pick = selected_runner_up
        current_user.third_place_pick = selected_third_place
        db.session.commit()
        flash('Palpites finais confirmados')
        return redirect(url_for('index'))

    return render_template('champion_pick.html', team_names=team_names)


@app.route('/bet/<int:game_id>', methods=['GET', 'POST'])
@login_required
def bet(game_id):
    if current_user.is_admin:
        flash('Administrador não participa do bolão')
        return redirect(url_for('admin'))

    if not current_user.is_admin and not has_final_standings_pick(current_user):
        flash('Escolha campeão, vice-campeão e terceiro lugar antes de fazer seu primeiro palpite')
        return redirect(url_for('champion_pick'))

    game = Game.query.get_or_404(game_id)
    existing_bet = Bet.query.filter_by(user_id=current_user.id, game_id=game_id).first()
    result = Result.query.filter_by(game_id=game_id).first()
    closed = is_game_closed(game)

    if request.method == 'POST':
        if closed:
            flash('Palpites encerrados para este jogo')
            return redirect(url_for('index'))

        score_a = int(request.form['score_a'])
        score_b = int(request.form['score_b'])
        if existing_bet:
            existing_bet.score_a = score_a
            existing_bet.score_b = score_b
        else:
            new_bet = Bet(user_id=current_user.id, game_id=game_id, score_a=score_a, score_b=score_b)
            db.session.add(new_bet)
        db.session.commit()
        flash('Palpite salvo')
        return redirect(url_for('index'))

    return render_template('bet.html', game=game, bet=existing_bet, result=result, closed=closed)


@app.route('/ranking')
@login_required
def ranking():
    users = User.query.filter_by(is_admin=False).all()
    ranking_data = []
    for user in users:
        ranking_data.append({'user': user, **calculate_user_performance(user)})
    ranking_data.sort(
        key=lambda item: (
            item['points'],
            item['exact_scores'],
            item['correct_outcomes'],
            item['partial_scores'],
            -item['errors'],
        ),
        reverse=True,
    )
    return render_template('ranking.html', ranking=ranking_data)


@app.route('/meu-desempenho')
@login_required
def my_performance():
    if current_user.is_admin:
        return redirect(url_for('admin'))

    performance = calculate_user_performance(current_user)
    return render_template('my_performance.html', performance=performance)


@app.route('/admin')
@login_required
def admin():
    if not is_admin_user():
        return redirect(url_for('index'))
    games = Game.query.order_by(Game.date).all()
    game_results = {
        result_item.game_id: result_item
        for result_item in Result.query.all()
    }
    users = User.query.filter_by(is_admin=False).all()
    return render_template(
        'admin.html',
        games=games,
        game_results=game_results,
        users=users,
        team_names=get_team_names(),
        official_champion=get_official_champion(),
        official_runner_up=get_official_runner_up(),
        official_third_place=get_official_third_place(),
    )


@app.route('/admin/estatisticas')
@login_required
def admin_statistics():
    if not is_admin_user():
        return redirect(url_for('index'))

    return render_template('admin_statistics.html', stats=get_admin_statistics())


@app.route('/admin/update_official_champion', methods=['POST'])
@login_required
def update_official_champion():
    if not is_admin_user():
        return redirect(url_for('index'))

    champion = request.form['champion'].strip()
    runner_up = request.form['runner_up'].strip()
    third_place = request.form['third_place'].strip()
    team_names = get_team_names()
    selected_teams = {champion, runner_up, third_place}

    if any(team_name not in team_names for team_name in selected_teams):
        flash('Selecione seleções válidas')
        return redirect(url_for('admin'))

    if len(selected_teams) < 3:
        flash('Campeão, vice-campeão e terceiro lugar devem ser seleções diferentes')
        return redirect(url_for('admin'))

    set_setting('official_champion', champion)
    set_setting('official_runner_up', runner_up)
    set_setting('official_third_place', third_place)
    flash('Classificação final oficial atualizada')
    return redirect(url_for('admin'))


@app.route('/admin/add_game', methods=['POST'])
@login_required
def add_game():
    if not is_admin_user():
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


@app.route('/admin/import_group_stage', methods=['POST'])
@login_required
def import_group_stage():
    if not is_admin_user():
        return redirect(url_for('index'))

    created_count = 0
    skipped_count = 0
    for date_text, phase, team_a, team_b in WORLD_CUP_2026_GROUP_STAGE_MATCHES:
        match_date = datetime.strptime(date_text, '%Y-%m-%dT%H:%M')
        existing_game = Game.query.filter_by(
            team_a=team_a,
            team_b=team_b,
            date=match_date,
            phase=phase,
        ).first()
        if existing_game:
            skipped_count += 1
            continue

        game = Game(team_a=team_a, team_b=team_b, date=match_date, phase=phase)
        db.session.add(game)
        created_count += 1

    db.session.commit()
    flash(f'Importação concluída: {created_count} jogos criados, {skipped_count} já existentes')
    return redirect(url_for('admin'))


@app.route('/admin/update_game/<int:game_id>', methods=['POST'])
@login_required
def update_game(game_id):
    if not is_admin_user():
        return redirect(url_for('index'))

    game = Game.query.get_or_404(game_id)
    game.team_a = request.form['team_a'].strip()
    game.team_b = request.form['team_b'].strip()
    game.date = datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M')
    game.phase = request.form['phase'].strip()
    db.session.commit()
    flash('Jogo atualizado')
    return redirect(url_for('admin'))


@app.route('/admin/add_result/<int:game_id>', methods=['POST'])
@login_required
def add_result(game_id):
    if not is_admin_user():
        return redirect(url_for('index'))
    score_a = int(request.form['score_a'])
    score_b = int(request.form['score_b'])
    result = Result.query.filter_by(game_id=game_id).first()
    if result:
        result.score_a = score_a
        result.score_b = score_b
        flash('Resultado atualizado')
    else:
        result = Result(game_id=game_id, score_a=score_a, score_b=score_b)
        db.session.add(result)
        flash('Resultado lançado')
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/admin/delete_game/<int:game_id>', methods=['POST'])
@login_required
def delete_game(game_id):
    if not is_admin_user():
        return redirect(url_for('index'))

    game = Game.query.get_or_404(game_id)
    Bet.query.filter_by(game_id=game.id).delete()
    Result.query.filter_by(game_id=game.id).delete()
    db.session.delete(game)
    db.session.commit()
    flash('Jogo excluído')
    return redirect(url_for('admin'))


@app.route('/admin/add_user', methods=['POST'])
@login_required
def add_user():
    if not is_admin_user():
        return redirect(url_for('index'))
    username = request.form['username'].strip()
    password = request.form['password']
    if not username or not password or find_user_by_username(username):
        return redirect(url_for('admin'))
    user = User(username=username, is_admin=False)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/admin/update_user_password/<int:user_id>', methods=['POST'])
@login_required
def update_user_password(user_id):
    if not is_admin_user():
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    password = request.form['password']
    if len(password) < 4:
        flash('A senha deve ter pelo menos 4 caracteres')
        return redirect(url_for('admin'))

    user.set_password(password)
    db.session.commit()
    flash(f'Senha de {user.username} atualizada')
    return redirect(url_for('admin'))


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not is_admin_user():
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Administradores não podem ser excluídos por aqui')
        return redirect(url_for('admin'))

    Bet.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'Participante {user.username} excluído')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
