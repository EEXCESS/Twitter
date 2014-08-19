from persistance import MysqlManager, Enums
import datetime
import logging


def create_user(username, twitter_id):
    user = MysqlManager.User()
    user.username = username
    user.twitterId = twitter_id
    user.created = datetime.datetime.now()
    user.updated = datetime.datetime.now()
    user.userStatus = Enums.UserStatus.normal.value
    user.save()

    return user


def add_user(username, twitter_id):
    user = get_user_by_twitter_id(twitter_id)

    if user is None:
        user = create_user(username, twitter_id)

    return user


def update(twitter_id):
    user = get_user_by_twitter_id(twitter_id)

    if user is not None:
        user.updated = datetime.datetime.now()
        user.save()


def get_user_by_twitter_id(twitter_id):

    try:
        user = MysqlManager.User.get(MysqlManager.User.twitterId == twitter_id)
    except MysqlManager.User.DoesNotExist as e:
        user = None

    return user


def is_new_user(twitter_id):

    try:
        user = MysqlManager.User.get(MysqlManager.User.twitterId == twitter_id)
    except MysqlManager.User.DoesNotExist as e:
        user = None

    if user is None:
        return True
    else:
        return False
