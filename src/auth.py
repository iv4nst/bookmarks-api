from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import validators
from flasgger import swag_from

from src.constants.http_status_codes import *
from src.database import db, User

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@auth.post('/register')
@swag_from('./docs/auth/register.yml')
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    # validate username
    if len(username) < 3:
        return jsonify({'error': 'Username is too short.'}), HTTP_400_BAD_REQUEST
    if not username.isalnum() or ' ' in username:
        return jsonify({'error': 'Username should be alphanumeric without spaces.'}), HTTP_400_BAD_REQUEST
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': 'Username is taken.'}), HTTP_409_CONFLICT
    # validate email
    if not validators.email(email):
        return jsonify({'error': 'Email is not valid.'}), HTTP_400_BAD_REQUEST
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': 'Email is taken.'}), HTTP_409_CONFLICT
    # validate password
    if len(password) < 6:
        return jsonify({'error': 'Password is too short.'}), HTTP_400_BAD_REQUEST

    # create user
    pwd_hash = generate_password_hash(password)
    user = User(username=username, email=email, password=pwd_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'User created',
        'user': {
            'username': username,
            'email': email
        }}), HTTP_201_CREATED


@auth.post('/login')
@swag_from('./docs/auth/login.yml')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    user = User.query.filter_by(email=email).first()
    if user:
        # if password is correct
        if check_password_hash(user.password, password):
            # create tokens
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return jsonify({
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'username': user.username,
                    'email': user.email
                }
            }), HTTP_200_OK
    return jsonify({'error': 'Wrong credentials.'}), HTTP_401_UNAUTHORIZED


@auth.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()  # get user id

    user = User.query.filter_by(id=user_id).first()
    # if user:

    return jsonify({
        'username': user.username,
        'email': user.email
    }), HTTP_200_OK


@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_user_token():
    identity = get_jwt_identity()  # get user id
    access_token = create_access_token(identity)
    return jsonify({
        'access': access_token
    }), HTTP_200_OK
