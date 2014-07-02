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

    return user.id


def add_user(username, twitter_id):
    user = get_user_by_twitter_id(twitter_id)

    if user is None:
        user_id = create_user(username, twitter_id)
    else:
        user_id = user.id

    return user_id


def update(twitter_id):
    user = get_user_by_twitter_id(twitter_id)

    if user is not None:
        user.updated = datetime.datetime.now()
        user.save()


def get_user_by_twitter_id(twitter_id):

    try:
        user = MysqlManager.User.get(MysqlManager.User.twitterId == twitter_id)
    except MysqlManager.User.DoesNotExist as e:
        logging.exception(e)
        user = None

    return user
