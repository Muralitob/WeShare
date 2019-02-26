# encoding: utf-8
"""
__author__:cjhcw
"""
from core_manager.mongo_manager import mongo_manager

from utility import get_this_time

chats_collection = "chats"


def add_new_chat(data, uid):
    """
    新建聊天
    :param data:
    :param uid:
    :return:
    """
    data.update({"from": uid, "time": get_this_time()})
    chat = {
        "relations": [uid, data["to"]],
        "content": [data]
    }
    return mongo_manager.save_one(chats_collection, chat).acknowledged


def get_record_by_uid(uid):
    """
    用户记录
    :param uid:
    :return:
    """
    records = list(mongo_manager.find(chats_collection, {"relations": uid}))
    return records


def add_new_msg(data, uid):
    """
    后续聊天
    :param data:
    :param uid:
    :return:
    """
    data.update({"from": uid, "time": get_this_time()})
    record = mongo_manager.find_one(chats_collection,
                                    {"$and": [{"relations": uid}, {"relations": data["to"]}]})
    record["content"].append(data)
    record.pop("relations")
    return mongo_manager.update_one(chats_collection, {"_id": record.pop("_id")},
                                    {"$set": record}).acknowledged
