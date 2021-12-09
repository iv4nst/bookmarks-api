from flask import Blueprint, request, jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from flasgger import swag_from

from src.constants.http_status_codes import *
from src.database import db, Bookmark

bookmarks = Blueprint('bookmarks', __name__, url_prefix='/api/v1/bookmarks')


@bookmarks.route('/', methods=['POST', 'GET'])  # @bookmarks.get('/')
@jwt_required()
def handle_bookmarks():
    current_user = get_jwt_identity()

    # creating a bookmark
    if request.method == 'POST':
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        # url invalid
        if not validators.url(url):
            return jsonify({'error': 'Enter a valid URL.'}), HTTP_404_NOT_FOUND
        # url already exists
        if Bookmark.query.filter_by(url=url).first():
            return jsonify({'error': 'URL already exists.'}), HTTP_409_CONFLICT

        # add bookmark
        bookmark = Bookmark(body=body, url=url, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        }), HTTP_201_CREATED
    # get all bookmarks
    else:
        # pagination
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=5, type=int)

        all_bookmarks = Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)
        data = [{
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        } for bookmark in all_bookmarks.items]
        meta = {
            'page': all_bookmarks.page,
            'pages': all_bookmarks.pages,
            'total_count': all_bookmarks.total,
            'prev_page': all_bookmarks.prev_num,
            'next_page': all_bookmarks.next_num,
            'has_prev': all_bookmarks.has_prev,
            'has_next': all_bookmarks.has_next
        }
    return jsonify({'data': data, 'meta': meta}), HTTP_200_OK


@bookmarks.get('/<int:id>')
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at
    }), HTTP_200_OK


@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def edit_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    # edit bookmark
    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    # url invalid
    if not validators.url(url):
        return jsonify({'error': 'Enter a valid URL.'}), HTTP_404_NOT_FOUND

    bookmark.url = url
    bookmark.body = body
    db.session.add(bookmark)
    db.session.commit()

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at
    }), HTTP_201_CREATED


@bookmarks.delete('/<int:id>')
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    # delete bookmark
    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT


@bookmarks.get('/stats')
@jwt_required()
@swag_from('./docs/bookmarks/stats.yml')
def get_stats():
    current_user = get_jwt_identity()
    items = Bookmark.query.filter_by(user_id=current_user).all()
    data = [{'visits': item.visits,
             'url': item.url,
             'short_url': item.short_url} for item in items]
    return jsonify({'data': data}), HTTP_200_OK
