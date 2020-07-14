from CTFd.models import (
    db,
)


class NotifierConfig(db.Model):
    key = db.Column(db.String(length=128), primary_key=True)
    value = db.Column(db.Text)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return "<NotifierConfig (0) {1}>".format(self.key, self.value)
