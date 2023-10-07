import json
import os
import pandas as pd
from dotenv import load_dotenv
from urllib.request import urlopen
from datetime import datetime
from pytz import timezone
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import pytz
import sys

def get_weather_icon(icon_str):
    if icon_str == "01d" or icon_str == "01n":
        return "☀️"
    elif (
        icon_str == "02d"
        or icon_str == "02n"
        or icon_str == "03d"
        or icon_str == "03n"
        or icon_str == "04d"
        or icon_str == "04n"
    ):
        return "☁️"
    elif (
        icon_str == "09d" or icon_str == "09n" or icon_str == "10d" or icon_str == "10n"
    ):
        return "☂️"
    elif icon_str == "11d" or icon_str == "11n":
        return "⚡️"
    elif icon_str == "13d" or icon_str == "13n":
        return "☃️"
    else:
        return ""


def send_to_line(df):
    texts = []
    count = 1
    for k, v in df:
        if count == 1:
            texts.append(f"【{k}】")
            for _, d in v.iterrows():
                texts.append(
                    f"{d['time']}時 {get_weather_icon(d['icon'])} {d['temp']}℃　 [{d['rain']}mm/3h]"
                )
            texts.append("")
            count += 1

    line_bot = LineBotApi(os.getenv("LINE_ACCESS_TOKEN"))
    # line_bot = LineBotApi(os.environ["LINE_ACCESS_TOKEN"])
    # line_bot = LineBotApi(sys.argv[3])
        
    try:
        line_bot.multicast(os.getenv("LINE_USER_ID").split(","), TextSendMessage(text="\n".join(texts)))
        # line_bot.multicast(os.environ["LINE_USER_ID"].split(","), TextSendMessage(text="\n".join(texts)))
        # line_bot.multicast(sys.argv[4].split(","), TextSendMessage(text="\n".join(texts)))
        print('成功')
    except LineBotApiError as e:
        print('send_to_line関数内でエラーが発生しました。')
        print('Error occurred: {}'.format(e))


def main():
    url = "http://api.openweathermap.org/data/2.5/forecast"
    id = os.getenv("OWM_PLACE_ID")
    # id = os.environ["OWM_PLACE_ID"]
    # id = sys.argv[1]
    api_key = os.getenv("OWM_API_KEY")
    # api_key = os.environ["OWM_API_KEY"]
    # api_key = sys.argv[2]

    res = urlopen(f"{url}?id={id}&appid={api_key}&lang=ja&units=metric").read()
    res_json = json.loads(res)

    arr_rj = []
    for rj in res_json["list"]:
        conv_rj = {}
        timezone = pytz.timezone("Asia/Tokyo")
        timestamp = datetime.fromtimestamp(rj["dt"], tz=timezone)
        weekday_japanese = ["月", "火", "水", "木", "金", "土", "日"][timestamp.weekday()]
        conv_rj["date"] = timestamp.strftime("%m月%d日 {}曜日".format(weekday_japanese))
        conv_rj["time"] = timestamp.strftime("%H")
        conv_rj["description"] = rj["weather"][0]["description"]
        conv_rj["icon"] = rj["weather"][0]["icon"]
        conv_rj["temp"] = round(rj["main"]["temp"])
        conv_rj["rain"] = round(rj["rain"]["3h"], 1) if "rain" in rj else 0
        arr_rj.append(conv_rj)

    try:
        send_to_line(pd.DataFrame(arr_rj).groupby("date"))
        print('正常にメッセージを送信できました！')
    except LineBotApiError as e:
        print('main関数内でエラーが発生しました。')
        print('Error occurred: {}'.format(e))


load_dotenv()
main()