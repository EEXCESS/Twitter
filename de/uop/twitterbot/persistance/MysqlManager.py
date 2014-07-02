from peewee import *
import Config


custom_db = MySQLDatabase(port=Config.database_port, database=Config.database_db, user=Config.database_user,
                          passwd=Config.database_pw)


class CustomModel(Model):
    class Meta:
        database = custom_db


class User(CustomModel):
    username = CharField(unique=True)
    twitterId = CharField(unique=True)
    userStatus = CharField()
    created = DateTimeField()
    updated = DateTimeField()


class UserTweet(CustomModel):
    user = ForeignKeyField(User, related_name="tweets")
    twitterId = CharField()
    tweet = CharField()
    created = DateTimeField()
    updated = DateTimeField()
    status = CharField()
    rawInput = TextField()


class Recommendation(CustomModel):
    userTweet = ForeignKeyField(UserTweet, related_name="recommendations")
    selectedId = CharField()
    created = DateTimeField()
    updated = DateTimeField()
    status = CharField()
    fullRecommendation = TextField()
    text = CharField()
