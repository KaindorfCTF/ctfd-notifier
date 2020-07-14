from .models import NotifierConfig

from CTFd.models import (
    db
)


class DBUtils:
    DEFAULT_CONFIG = [
        {"key": "discord_notifier", "value": "false"},
        {"key": "discord_webhook_url", "value": ""},
        {"key": "twitter_notifier", "value": "false"},
        {"key": "twitter_consumer_key", "value": ""},
        {"key": "twitter_consumer_secret", "value": ""},
        {"key": "twitter_access_token", "value": ""},
        {"key": "twitter_access_token_secret", "value": ""},
        {"key": "twitter_hashtags", "value": ""},
        {"key": "teamsound_notifier", "value": "true"},
        {"key": "teamsound_clients", "value": "10.80.X.100"}
    ]

    @staticmethod
    def get(key):
        return NotifierConfig.query.filter_by(key=key).first()

    @staticmethod
    def get_config():
        configs = NotifierConfig.query.all()
        result = {}

        for c in configs:
            result[str(c.key)] = str(c.value)

        return result

    @staticmethod
    def save_config(config):
        for c in config:
            q = db.session.query(NotifierConfig)
            q = q.filter(NotifierConfig.key == c[0])
            record = q.one_or_none()

            if record:
                record.value = c[1]
                db.session.commit()
            else:
                config = NotifierConfig(key=c[0], value=c[1])
                db.session.add(config)
                db.session.commit()
        db.session.close()

    @staticmethod
    def load_default():
        for cv in DBUtils.DEFAULT_CONFIG:
            # Query for the config setting
            k = DBUtils.get(cv["key"])
            # If its not created, create it with its default value
            if not k:
                c = NotifierConfig(key=cv["key"], value=cv["value"])
                db.session.add(c)
        db.session.commit()
