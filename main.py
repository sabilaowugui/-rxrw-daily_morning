from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

UID = os.environ["UID"]
KEY = os.environ["KEY"]
API = "http://api.seniverse.com/v3/weather/now.json";


def generate_weather_url():
    """生成带签名的天气API请求URL"""
    ts = str(int(today.timestamp()))
    params = {
        "ts": ts,
        "uid": UID,
        "location": city,
        "ttl": 300
    }
    
    # 按参数名排序生成签名字符串
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    
    # 生成签名
    signature = hmac.new(
        KEY.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha1
    ).digest()
    signature = base64.b64encode(signature).decode()
    params["sig"] = signature
    
    return f"{API}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

def get_weather():
    """获取天气数据"""
    try:
        url = generate_weather_url()
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        weather_info = data["results"][0]["now"]
        return weather_info["text"], int(weather_info["tempature"])
    except Exception as e:
        print(f"Weather API Error: {str(e)}")
        return "未知", 0

#def get_weather():
#  res = requests.get(url).json()
# weather = res['data']['list'][0]
# return weather['weather'], math.floor(weather['temp'])

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)
wea, temp = get_weather()
wm = WeChatMessage(client)
wea, temp = get_weather()
data = {"weather":{"value":wea},"temperature":{"value":temp},"love_days":{"value":get_count()},"birthday_left":{"value":get_birthday()},"words":{"value":get_words(), "color":get_random_color()}}
res = wm.send_template(user_id, template_id, data)
print(res)
