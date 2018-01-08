# coding: UTF-8

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# キズナアイのbot用
USER_ID = os.environ.get("USER_ID")
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

# splatoonのbot用
USER_ID_SPLATOON = os.environ.get("USER_ID_SPLATOON")
CONSUMER_KEY_SPLATOON = os.environ.get("CONSUMER_KEY_SPLATOON")
CONSUMER_SECRET_SPLATOON = os.environ.get("CONSUMER_SECRET_SPLATOON")
ACCESS_TOKEN_SPLATOON = os.environ.get("ACCESS_TOKEN_SPLATOON")
ACCESS_TOKEN_SECRET_SPLATOON = os.environ.get("ACCESS_TOKEN_SECRET_SPLATOON")
