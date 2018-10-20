# encoding: utf-8
"""
__author__:cjhcw
"""
from flask import Blueprint
from flask import request
from flask import jsonify

from database.users_db import requires_auth
from database import articles_db

import utility
import jwt

articles = Blueprint("article", __name__, url_prefix='/api/article')


@articles.route('/create_new_article', methods=['POST'])
@requires_auth
def create_new_article():
    """
    新建文章
    :return:
    """
    data = request.get_json()
    token = request.headers.get('Authorization')
    token = jwt.decode(token[6:], 'secret', algorithms=['HS256'])
    data['article']['uid'] = token['uid']
    result = articles_db.create_new_article(data)
    if result:
        if data['category'] == 'real':
            return jsonify({"code": 101}), 200
        elif data['category'] == 'fake':
            return jsonify({"code": 102}), 201
    else:
        if data['category'] == 'real':
            return jsonify({"code": 103}), 404
        elif data['category'] == 'fake':
            return jsonify({"code": 104}), 404


@articles.route('/get_articles_by_uid', methods=['GET'])
@requires_auth
def get_articles_by_uid():
    """
    根据uid获取文章
    :return:
    """
    token = request.headers.get('Authorization')
    data = jwt.decode(token[6:], 'secret', algorithms=['HS256'])
    category = request.args.get('category')
    page = request.args.get('page')
    limit = request.args.get('limit')
    result, length = articles_db.get_articles_by_uid(data['uid'], category, int(page), int(limit))
    return jsonify({"articles": utility.convert_to_json(result), "total": length}), 200


@articles.route('/edit_article_by_id', methods=['POST'])
@requires_auth
def edit_article_by_id():
    """
    根据article['id']编辑文章
    :return:
    """
    article = request.get_json()
    result = articles_db.edit_article_by_id(article)
    if result:
        return jsonify({"code": 106}), 200
    else:
        return jsonify({"code": 107}), 404


@articles.route('/delete_article_by_id', methods=['DELETE'])
@requires_auth
def delete_article_by_id():
    """
    批量删除文章
    :return:
    """
    data = request.get_json()
    article_ids = data['article_ids']
    result = articles_db.delete_article_by_id(article_ids)
    if result:
        return jsonify({"code": 108}), 200
    else:
        return jsonify({"code": 109}), 404


@articles.route('/get_real_articles', methods=['GET'])
def get_real_articles():
    """
    获取real文章
    :return:
    """
    page = request.args.get('page')
    limit = request.args.get('limit')
    result, length = articles_db.get_real_articles(page, limit)
    return jsonify({"articles": utility.convert_to_json(result), "total": length}), 200