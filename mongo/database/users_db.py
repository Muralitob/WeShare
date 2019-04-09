# encoding: utf-8
"""
__author__:cjhcw
"""
import jwt
from functools import wraps
from flask import request
from bson import ObjectId

from core_manager.mongo_manager import mongo_manager
from models.User import User
from models.Article import Article

from utility import page_limit_skip, get_this_time, get_next_id_sequence, get_word_escape

user_collection = 'users'
collcetions_collection = 'collections'
like_collection = 'like_articles'
attention_collection = 'attentions'


def register(data):
    """
    用户注册
    :param data: 用户注册信息
    :return:
    """
    data['level'] = '0002'
    data['uid'] = get_next_id_sequence(0)
    data['major'] = ''
    data['nickname'] = data['account']
    data['birthday'] = ''
    data['sign'] = ''
    data['branch'] = ''
    data['sex'] = ''
    data['register_time'] = get_this_time()
    data['login_time'] = None
    user = User.query_one(data['account'])
    if user:
        return False
    else:
        return User.save_one(data)


def login(data):
    """
    用户登录
    :param data: 账号密码
    :return:
    """
    user = User.query_one(data['account'])
    if user and user['pwd'] == data['pwd']:
        User.update_one(data['account'], {'login_time': get_this_time()})
        encoded = jwt.encode({
            'account': user['account'],
            'uid': str(user['uid']),
            'organization': str(user['level']),
            'update_time': str(get_this_time())}, 'secret', algorithm='HS256')
        return_object = {
            'status': 'login success',
            'code': 200,
            'token': encoded,
            'account': user['account'],
            'org': str(user['level']),
            'uid': str(user['uid'])
        }
        return return_object
    else:
        return False


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token:
            payload = jwt.decode(token[6:], 'secret', algorithms=['HS256'])
            user = User.query_one_by_uid(int(payload['uid']))
            if user:
                return f(*args, **kwargs)
        else:
            cookie_uid = request.cookies.get('uid')
            cookie_user = User.query_one_by_uid(int(cookie_uid))
            if cookie_user:
                return f(*args, **kwargs)

    return decorated


def get_user_info(other_id, uid):
    """
    获取用户信息
    :param other_id: 目标账号id
    :param uid: 此账号id
    :return:
    """
    one = User.query_one_by_uid(other_id)
    if uid:
        attention = mongo_manager.find_one(attention_collection,
                                           {'uid': uid, 'attention_uid': other_id})
        if attention:
            one['attentioned'] = True
        else:
            one['attentioned'] = False
    return one


def get_me_info(uid):
    """
    获取自己的用户信息
    :param uid: 用户id
    :return:
    """
    if uid:
        uid = int(uid)
        one = User.query_one_by_uid(uid)
        attentions = list(mongo_manager.find(attention_collection, {'uid': uid}))
        if attentions:
            attention_uids = [att['attention_uid'] for att in attentions]
        else:
            attention_uids = []
        one['attention_uids'] = attention_uids
        one['attention_count'] = mongo_manager.find_count(attention_collection, {'uid': uid})
        one['attentioned_count'] = mongo_manager.find_count(attention_collection, {'attention_uid': uid})
        return one


def edit_user_info(uid, data):
    """
    编辑用户信息
    :param uid: 用户id
    :param data: 要修改的信息
    :return:
    """
    if '_id' in data:
        data.pop('_id')
    return User.update_one_by_uid(uid, data)


def get_collections_by_uid(uid, page, limit):
    """
    获取用户收藏
    :param uid: 用户id
    :param page: 页码
    :param limit: 每页数量
    :return:
    """
    skip, limit = page_limit_skip(limit, page)
    result = list(
        mongo_manager.find(collcetions_collection,
                           {'uid': uid}).skip(skip).limit(limit).sort([('create_time', -1)]))
    articles = []
    for item in result:
        article = Article.query_by_id(item['article_id'])
        article['col_num'] = mongo_manager.find_count(collcetions_collection,
                                                      {'article_id': article['_id']})
        article['like_num'] = mongo_manager.find_count(like_collection,
                                                       {'article_id': article['_id']})
        articles.append(article)
    length = mongo_manager.find_count(collcetions_collection,
                                      {'uid': uid})
    return articles, length


def save_collection(uid, article_id):
    """
    保存收藏
    :param uid: 用户id
    :param article_id: 文章id
    :return:
    """
    query = {'uid': uid, 'article_id': ObjectId(article_id)}
    collcetion = mongo_manager.find_one(collcetions_collection, query)
    if collcetion:
        return False
    return mongo_manager.save_one(collcetions_collection,
                                  {'uid': uid,
                                   'article_id': ObjectId(article_id),
                                   'create_time': get_this_time(),
                                   'update_time': get_this_time()}).acknowledged


def delete_collections(uid, article_ids):
    """
    取消收藏
    :param uid: 用户id
    :param article_ids: 取消收藏的文章id
    :return:
    """
    for article_id in article_ids:
        article = mongo_manager.find_one(collcetions_collection,
                                         {'uid': uid, 'article_id': ObjectId(article_id)})
        if article:
            mongo_manager.remove_one(collcetions_collection,
                                     {'uid': uid, 'article_id': ObjectId(article_id)})
        else:
            return False
    return True


def add_attention(uid, attention_uid):
    """
    关注用户
    :param uid: 用户id
    :param attention_uid: 关注者id
    :return:
    """
    is_attentions = mongo_manager.find_one(attention_collection,
                                           {'uid': uid, 'attention_uid': attention_uid})
    if is_attentions:
        return False
    else:
        return mongo_manager.save_one(attention_collection,
                                      {'uid': uid, 'attention_uid': attention_uid}).acknowledged


def delete_attention(uid, attention_uid):
    """
    取消关注
    :param uid: 用户id
    :param attention_uid: 关注者id
    :return:
    """
    is_attentions = mongo_manager.find_one(attention_collection,
                                           {'uid': uid, 'attention_uid': attention_uid})
    if not is_attentions:
        return False
    else:
        return mongo_manager.remove_one(attention_collection,
                                        {'uid': uid, 'attention_uid': attention_uid}).acknowledged


def get_attentions(uid, page, limit, user_type=None):
    """
    获取uid的关注
    :param uid: 用户id
    :param page: 页码
    :param limit: 每页数量
    :param user_type:
    :return:
    """
    if user_type:
        user_type = "attention_uid"
        find_type = "uid"
    else:
        user_type = "uid"
        find_type = "attention_uid"
    skip, limit = page_limit_skip(limit, page)
    attentions = list(mongo_manager.find(attention_collection,
                                         {user_type: uid}).skip(skip).limit(limit))
    users = []
    for attention in attentions:
        user = User.query_one_by_uid(attention[find_type])
        if user:
            users.append(user)
    count = mongo_manager.find_count(attention_collection, {user_type: uid})
    return users, count


def search_user(keyword):
    """
    账号或昵称关键词
    :param keyword:
    :return:
    """
    if keyword:
        keyword = get_word_escape(keyword)
        query = {"$or": [{"account": {"$regex": keyword}},
                         {"nickname": {"$regex": keyword}}]}
        user_list = list(mongo_manager.find(user_collection, query))
        total = mongo_manager.find_count(user_collection, query)
    else:
        user_list = list(mongo_manager.find(user_collection, {}))
        total = mongo_manager.find_count(user_collection, {})
    return user_list, total


def reset_password_from_admin(uids):
    """
    管理员重置密码 用于用户找回密码
    重置后的密码 qjxy123456
    :param uids: 用户ids
    :return:
    """
    r = True
    for uid in uids:
        r = mongo_manager.update_one(user_collection, {"uid": uid},
                                     {"$set": {"pwd": "100e488a477e0b4b6faa72db9ecc8bc276329733"}}).acknowledged
    return r


def delete_users(uids):
    """
    要删除的id的list
    :param uids: 用户id
    :return:
    """
    return mongo_manager.remove_many(user_collection, {"uid": {"$in": uids}}).acknowledged
