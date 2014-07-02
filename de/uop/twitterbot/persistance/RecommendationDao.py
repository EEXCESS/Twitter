from persistance import MysqlManager, Enums
import datetime


def create_recommendation(user_tweet_id, full_recommendation, text):
    rec = MysqlManager.Recommendation()
    rec.userTweet = user_tweet_id
    rec.created = datetime.datetime.now()
    rec.updated = datetime.datetime.now()
    rec.fullRecommendation = full_recommendation
    rec.text = text
    rec.status = Enums.RecommendationStatus.new.value
    rec.save()

    return rec.id


def get_new_recommendations():
    select = MysqlManager.Recommendation.select().where(MysqlManager.Recommendation.status ==
                                                        Enums.RecommendationStatus.new.value)
    recs = select.execute()

    return recs


def update_status(rec, status):
    rec.status = status.value
    rec.updated = datetime.datetime.now()
    rec.save()
