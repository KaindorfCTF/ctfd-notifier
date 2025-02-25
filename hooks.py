import json
from asyncio import run

import CTFd.cache as cache
import requests as rq
import tweepy
from aiogram import Bot
from CTFd.models import Challenges, Solves, Teams, Users
from CTFd.utils.config import is_teams_mode
from sqlalchemy.event import listen

from ...utils.modes import get_model
from .db_utils import DBUtils


def discord_notify(solve, webhookurl):
    text = _getText(solve)

    embed = {"title": "First Blood!", "color": 15158332, "description": text}

    data = {"embeds": [embed]}

    try:
        rq.post(
            webhookurl,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
        )
    except rq.exceptions.RequestException as e:
        print(e)


def twitter_notify(
    solve, consumer_key, consumer_secret, access_token, access_token_secret, hashtags
):
    text = _getText(solve, hashtags)
    try:
        AUTH = tweepy.OAuthHandler(consumer_key, consumer_secret)
        AUTH.set_access_token(access_token, access_token_secret)
        API = tweepy.API(AUTH)
        API.update_status(status=text)
    except tweepy.TweepError as e:
        print(e)


def telegram_notify(solve, token: str, chat_id: int, message_thread_id: int):
    text = _getText(solve)
    bot = Bot(token)
    run(bot.send_message(chat_id, text, message_thread_id))


def on_solve(mapper, conn, solve):
    config = DBUtils.get_config()
    solves = _getSolves(solve.challenge_id)

    if solves == 1:
        if config.get("discord_notifier") == "true":
            discord_notify(solve, config.get("discord_webhook_url"))

        if config.get("twitter_notifier") == "true":
            twitter_notify(
                solve,
                config.get("twitter_consumer_key"),
                config.get("twitter_consumer_secret"),
                config.get("twitter_access_token"),
                config.get("twitter_access_token_secret"),
                config.get("twitter_hashtags"),
            )

        if config.get("telegram_notifier") == "true":
            telegram_notify(
                solve,
                config.get("telegram_bot_token"),
                config.get("telegram_chat_id"),
                config.get("telegram_message_thread_id"),
            )


def _getSolves(challenge_id):
    Model = get_model()

    solve_count = (
        Solves.query.join(Model, Solves.account_id == Model.id)
        .filter(
            Solves.challenge_id == challenge_id,
            Model.hidden == False,
            Model.banned == False,
        )
        .count()
    )

    return solve_count


def _getChallenge(challenge_id):
    challenge = Challenges.query.filter_by(id=challenge_id).first()
    return challenge


def _getUser(user_id):
    user = Users.query.filter_by(id=user_id).first()
    return user


def _getTeam(team_id):
    team = Teams.query.filter_by(id=team_id).first()
    return team


def _getText(solve, hashtags=""):
    name = ""
    score = 0
    place = 0
    cache.clear_standings()
    user = _getUser(solve.user_id)
    challenge = _getChallenge(solve.challenge_id)

    if is_teams_mode():
        team = _getTeam(user.team_id)
        name = team.name
        score = team.get_score()
        place = team.get_place()
    else:
        name = user.name
        score = user.get_score()
        place = user.get_place()

    if not hashtags == "":
        text = f"{name} got first blood on {challenge.name} and is now in {place} place with {score} points! {hashtags}"
    else:
        text = f"{name} got first blood on {challenge.name} and is now in {place} place with {score} points!"

    return text


def load_hooks():
    listen(Solves, "after_insert", on_solve)
