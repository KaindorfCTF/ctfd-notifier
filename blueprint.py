from flask import request, render_template, Blueprint, abort
from .db_utils import DBUtils
from CTFd.utils.decorators import admins_only, authed_only

import requests as rq
import tweepy

notifier_bp = Blueprint("notifier", __name__, template_folder="templates")


def load_bp(plugin_route):
    @notifier_bp.route(plugin_route, methods=["GET"])
    @admins_only
    def get_config():
        config = DBUtils.get_config()
        return render_template("ctfd_notifier/config.html", config=config)

    @notifier_bp.route(plugin_route, methods=["POST"])
    @admins_only
    def update_config():
        config = request.form.to_dict()
        del config["nonce"]

        errors = test_config(config)

        if len(errors) > 0:
            return render_template("ctfd_notifier/config.html", config=DBUtils.get_config(), errors=errors)
        else:
            DBUtils.save_config(config.items())
            return render_template("ctfd_notifier/config.html", config=DBUtils.get_config())

    return notifier_bp


def test_config(config):
    errors = list()
    if "discord_notifier" in config:
        if config["discord_notifier"]:
            webhookurl = config["discord_webhook_url"]

            if not webhookurl.startswith("https://discordapp.com/api/webhooks/") \
            and not webhookurl.startswith("https://discord.com/api/webhooks"):
                errors.append("Invalid Webhook URL!")
            else:
                try:
                    r = rq.get(webhookurl)
                    if not r.status_code == 200:
                        errors.append("Could not verify that the Webhook is working!")
                except rq.exceptions.RequestException as e:
                    errors.append("Invalid Webhook URL!")

    if "twitter_notifier" in config:
        if config["twitter_notifier"]:
            try:
                AUTH = tweepy.OAuthHandler(config.get("twitter_consumer_key"), config.get("twitter_consumer_secret"))
                AUTH.set_access_token(config.get("twitter_access_token"), config.get("twitter_access_token_secret"))
                API = tweepy.API(AUTH)
                API.home_timeline()
            except tweepy.TweepError:
                errors.append("Invalid authentication Data!")

    return errors
