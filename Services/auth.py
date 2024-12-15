from flask import jsonify
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity
from Database.user import users

# Authenticates a user using their email and password.
def authenticate_user(data):

    email = data.get('email', None)
    password = data.get('password', None)

    if not email or not password:
        return {'msg': 'Missing email or password'}, 400

    user = users.get(email, None)
    if not user or user['password'] != password:
        return {'msg': 'Incorrect email or password'}, 401

    # Generate access token
    access_token = create_access_token(identity=email)
    return {
        'msg': 'Login successful',
        'user': email,
        'access_token': access_token
    }, 200

# Retrieves the current logged-in user from the JWT.
def get_logged_in_user():
    current_user = get_jwt_identity()
    
    return {
        'logged_in_as': current_user,
        'msg': 'You have access to this resource'
    }, 200
