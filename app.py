import random
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup


from flask import Flask, abort, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (CarouselColumn, CarouselTemplate, FollowEvent,
                            MessageAction, MessageEvent, TemplateSendMessage, URIAction,
                            TextMessage, TextSendMessage, ImageSendMessage, ButtonsTemplate)
from sqlalchemy import func

# init
app = Flask (__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kslugeilknyusm:881fccc7272f44c3d1418bc4dfc67345a070c2bdf3bee0fb6988ec05c19be5e7@ec2-34-230-153-41.compute-1.amazonaws.com:5432/de1uns2t9bopo3'
db = SQLAlchemy(app)
db.create_all()

line_bot_api = LineBotApi('516KsFfnTZ7zAfSfGUJhTYt4T2PBnRThlzS5LZ5DApqHpHV/eb4ODPT5aXcWiKkpkwVvXBU/c66yG7WGF/2m1HTRZdXIOZiVF1LXBBMEyGulfhuyYXRIMTkWvXA8H0NJM1/rF2P/ILtBkEjKrloqywdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('4506bcd2d49c87a004060cae9d223e7e')


# const
LIFF_URL  = 'https://liff.line.me/1657167128-RMEY8X7b'
SERVER_URL = 'https://linefresh-bot.herokuapp.com'
TASK_LIST = TemplateSendMessage(
        alt_text = '尋寶任務',
        template = CarouselTemplate(
            columns = [
                CarouselColumn(title='每日簽到', text='點擊按鈕完成簽到', thumbnail_image_url=f'{SERVER_URL}/static/img/tasks/sign_in.png',
                    actions = [MessageAction(label='簽到', text='探險家來簽到')]),
                CarouselColumn(title='VOOM投稿', text='參加「我站在鐵花裡」活動，回傳已投稿的貼文連結', thumbnail_image_url=f'{SERVER_URL}/static/img/tasks/voom_post.png', 
                    actions = [URIAction(label = '我站在鐵花裡', uri='https://liff.line.me/1657167128-RMEY8X7b/')]),
                CarouselColumn(title='MUSIC LIVE序號', text='登錄「MUSIC LIVE鐵花音樂表演」序號', thumbnail_image_url=f'{SERVER_URL}/static/img/tasks/music_live.png',
                    actions = [MessageAction(label='登錄序號', text='登錄序號')]),
                CarouselColumn(title='鐵花LOGO尋寶趣', text='尋找商圈LOGO，掃描QR code', thumbnail_image_url=f'{SERVER_URL}/static/img/tasks/logo_hunt.png',
                    actions = [URIAction(label = '詳情請見活動辦法', uri='https://liff.line.me/1657167128-RMEY8X7b/')]),
                CarouselColumn(title='分享歌單', text='將鐵花精選歌手名單分享給好友', thumbnail_image_url =f'{SERVER_URL}/static/img/tasks/share_song_list.png',
                    actions = [URIAction(label='分享給好友', uri='https://liff.line.me/1657167128-RMEY8X7b/music')]),
                CarouselColumn(title='探索音樂人', text='點擊進入兩位歌手的介紹頁面，即可獲得轉盤抽獎機會', thumbnail_image_url=f'{SERVER_URL}/static/img/tasks/singer_info.png',
                    actions = [URIAction(label='探索音樂人', uri='https://liff.line.me/1657167128-RMEY8X7b/music')])
            ]
        )
    )
VOOM_POST = [
    TextSendMessage(text="【任務說明】\n1. 前往 VOOM 話題卡投稿貼文，並設置為「公開」\n2. 點選分享按鈕後，複製貼文連結，並將連結貼上回傳至官方帳號\n3. 系統判定貼文內容後，即完成任務！"), 
    ImageSendMessage(
        original_content_url = f'{SERVER_URL}/static/img/voom_link.jpg', 
        preview_image_url = f'{SERVER_URL}/static/img/voom_link.jpg'
    ),
    TemplateSendMessage(
        alt_text='VOOM 話題卡: https://liff.line.me/1657167128-RMEY8X7b/',
        template=ButtonsTemplate(
            text='由此前往 VOOM 話題卡✨',
            actions=[URIAction(label='點我前往', uri='https://liff.line.me/1657167128-RMEY8X7b/')]
        )
    )
]

# SQL Tables
class User_Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.user_id'))
    coupon_name = db.Column(db.String, db.ForeignKey('coupons.coupon_name'))
    detail = db.Column(db.String)
    verified = db.Column(db.Boolean, default=False)
    datetime = db.Column(db.DateTime)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, unique=True)
    raffle_num = db.Column(db.Integer, default=0)
    tasks = db.relationship("Tasks", backref="users")
    coupons = db.relationship("User_Coupon", backref="users")

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    task_name = db.Column(db.String)
    detail = db.Column(db.String, default="")
    datetime = db.Column(db.DateTime)
    user_id = db.Column(db.String, db.ForeignKey('users.user_id'))

class Coupons(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    coupon_name = db.Column(db.String, unique = True)
    total_num = db.Column(db.Integer)
    remain_num = db.Column(db.Integer)
    description = db.Column(db.String)
    notice = db.Column(db.String)
    img_wide = db.Column(db.String)
    img_large = db.Column(db.String)
    users = db.relationship("User_Coupon", backref="coupons")

class Line_Points(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    guid = db.Column(db.String, unique = True)
    used = db.Column(db.Boolean, default = False)


# SQL Query
def get_user(user_id):
    user = Users.query.filter(Users.user_id == user_id).first()
    if user is None:
        user = Users(user_id=user_id)
        db.session.add(user)
        db.session.commit()
    return user

def update_task(user, task_name, detail):
    task = get_task(user, task_name, detail)
    if task is not None: return False

    add_task(user, task_name, detail)
    print(f"[TASK] {user.user_id} | {task_name} | {detail}")
    return True

def get_task(user, task_name, detail):
    if task_name in ["sign_in", "share_song_list"]:
        local_datetime = current_time()
        return Tasks.query.filter(Tasks.user_id == user.user_id, Tasks.task_name == task_name, Tasks.datetime >= local_datetime.date()).first()
    if task_name in ["singer_info", "logo_hunt", "trivia_quiz"]:
        return Tasks.query.filter(Tasks.user_id == user.user_id, Tasks.task_name == task_name, Tasks.detail == detail).first()
    if task_name in ["music_live_number", "voom_post"]:
        return Tasks.query.filter(Tasks.user_id == user.user_id, Tasks.task_name == task_name).first()

def add_task(user, task_name, detail):
    if task_name == "singer_info":
        counts = Tasks.query.filter(Tasks.user_id == user.user_id, Tasks.task_name == task_name).count()
        if (counts + 1) % 2 == 0: user.raffle_num += 1
    else: user.raffle_num += 1

    task = Tasks(user_id=user.user_id, task_name=task_name, detail=detail, datetime = datetime.utcnow() + timedelta(hours=8))
    db.session.add(task)
    db.session.commit()

def raffle_coupon():
    coupon_list = Coupons.query.filter(Coupons.remain_num > 0).all()
    print("coupon_list: ")
    for coupon in coupon_list:
        print(f"{coupon.coupon_name}, {coupon.remain_num}")
    remain_num = Coupons.query.with_entities(func.sum(Coupons.remain_num)).filter(Coupons.remain_num > 0).first()[0]
    print(f"remain_num: {remain_num}")
    raffle_index = random.randint(1, remain_num)
    print(f"raffle_index: {raffle_index}")
    for coupon in coupon_list:
        if raffle_index > coupon.remain_num: raffle_index -= coupon.remain_num
        else: return coupon

def add_user_coupon(user):
    coupon = raffle_coupon()
    print(f"raffle_coupon: {coupon.coupon_name}, {coupon.remain_num}")
    user_coupon = User_Coupon(user_id=user.user_id, coupon_name=coupon.coupon_name, datetime=current_time())
    print(f"raffle_user_coupon: {user_coupon.coupon_name}")
    
    if user_coupon.coupon_name == "line_point":
        line_points = Line_Points.query.filter(Line_Points.used == False).first()
        line_points.used = True
        user_coupon.detail = line_points.guid
        user_coupon.verified = True
        coupon.remain_num -= 1
        print(f"coupon_remain: {coupon.remain_num}")

    user.raffle_num -= 1
    db.session.add(user_coupon)
    db.session.commit()

    return user_coupon

def current_time():
    return datetime.utcnow() + timedelta(hours=8)


# linebot handler
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

WELCOME_MESSAGE = """\
嗨 {display_name}
歡迎加入鐵花商圈官方帳號～
🎉7/15～8/7 為【音 JOY 鐵花尋寶祭】活動期間，LINE 結合數位體驗與豐富好禮，為鐵花商圈帶來全新的旅遊體驗！

<活動方式>
1️⃣試著點擊並完成下方【尋寶任務】
2️⃣完成後可獲得【優惠轉盤】機會，好禮拿不完🤩
3️⃣點擊【LOGO尋寶趣】到活動店家掃描尋寶條碼，更有機會獲得 Marshall 音響🎵
4️⃣還有【鐵花好音樂】與【鐵花情報站】等你來尋寶🏴‍☠️

🔗關注活動粉專：https://bit.ly/3QWX85L
🔗活動詳情請看：https://bit.ly/3nprlwz

立即探索下方圖文選單，享受數位慢活體驗😍\
"""
@handler.add(FollowEvent)
def handle_follow(event):
    user = get_user(event.source.user_id)
    display_name = line_bot_api.get_profile(user.user_id).display_name
    line_bot_api.reply_message(event.reply_token, [
        TextSendMessage(text=WELCOME_MESSAGE.format(display_name=display_name)), 
        ImageSendMessage(original_content_url = f'{SERVER_URL}/static/img/poster.jpg',preview_image_url = f'{SERVER_URL}/static/img/poster.jpg')
    ])

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user = get_user(event.source.user_id)
    message_text = event.message.text

    if message_text == "尋寶任務":
        return line_bot_api.reply_message(event.reply_token, TASK_LIST)
    if message_text == "探險家來簽到":
        message_text = "簽到任務成功！\n已獲得一次轉盤機會🥳\n快去優惠轉盤查看吧！" if update_task(user, "sign_in", "") else "你今天已經簽到過囉～來挑戰其他任務吧！"
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message_text))
    if message_text == "登錄序號":
        message_text = "【任務說明】\n1. 前往 LINE MUSIC 索取鐵花音樂表演免費門票\n2. LINE MUSIC 通知查看訂單號碼\n3. 回到鐵花商圈官方帳號，在對話框輸入「MUSIC 訂單號碼」，即可完成任務！"
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message_text))
    if message_text == "探險家資訊":
        display_name = line_bot_api.get_profile(user.user_id).display_name
        message_text = f"嗨{display_name}!\n你的剩餘抽獎次數為 {user.raffle_num} 次"
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message_text))
    if message_text == "VOOM":
        return line_bot_api.reply_message(event.reply_token, VOOM_POST)
    if message_text.startswith("https://linevoom.line.me/post/"):
        if not fetch_voom_post(message_text):
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text="網址或貼文內容錯誤😵‍💫\n再試一次看看吧！"))
        if not update_task(user, "voom_post", ""):
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你已完成過任務了喔～來挑戰看看其他任務吧！"))
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text="恭喜完成 VOOM 投稿！✨\n已獲得一次抽獎機會，快去優惠轉盤查看吧！"))

    # Echo
    return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message_text))

def fetch_voom_post(url):
    response = requests.get(url)
    if response.status_code == 404: return False
    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.select_one("div.post_text").text
    return True if "站在鐵花裡" in content else False

# LIFF router
@app.route("/")
@app.route("/liff")
def liff():
    path = request.args.get("liff.state")
    if path is not None:
        print(path)
        return redirect(f"/liff{path}")
    return redirect("/liff/regulation")

@app.route("/liff/regulation")
def liff_regulation():
    return render_template('regulation.html')

@app.route("/liff/article")
def liff_article():
    return render_template('article.html')

@app.route("/liff/coupon")
def liff_coupon():
    return render_template('coupon.html')

@app.route("/liff/coupon_1")
def liff_coupon_1():
    return render_template('coupon_1.html')

@app.route("/liff/logo")
def liff_logo():
    return render_template('logo.html')

@app.route("/liff/music")
def liff_music():
    return render_template('music.html')

@app.route("/liff/live")
def liff_live():
    return render_template('live.html')

@app.route("/liff/spin")
def liff_spin():
    return render_template('spin.html')

@app.route("/liff/singer/<singer_name>")
def liff_singer(singer_name:str):
    singer_name = singer_name.replace(".html", "")
    print(singer_name)
    return render_template(f'singer/{singer_name}.html')


# LIFF api
@app.route("/liff/user/raffle", methods=["POST"])
def liff_user_raffle():
    data = request.json
    user = get_user(data["user_id"])
    return {"raffle_num": user.raffle_num}

@app.route("/liff/user/logo", methods=["POST"])
def liff_user_logo():
    data = request.json
    user = get_user(data["user_id"])
    tasks = Tasks.query.filter(Tasks.user_id == user.user_id, Tasks.task_name == "logo_hunt").all()
    logo_list = [logo.detail for logo in tasks]
    print(logo_list)
    return {"logo_list": logo_list}

@app.route("/liff/user/singer", methods=["POST"])
def liff_user_singer():
    data = request.json
    user = get_user(data["user_id"])
    tasks = Tasks.query.filter(Tasks.user_id == user.user_id, Tasks.task_name == "singer_info").all()
    singer_list = [singer.detail for singer in tasks]
    return {"singer_list": singer_list}

@app.route("/liff/user/coupon", methods=["POST"])
def liff_user_coupon():
    data = request.json
    user = get_user(data["user_id"])
    available_coupon = []
    used_coupon = []
    no_remain = []
    for coupon in user.coupons:
        if coupon.coupon_name == "line_point":
            continue
        if not coupon.verified and coupon.coupons.remain_num > 0:
            available_coupon.append({"id": coupon.id, "img": coupon.coupons.img_wide})
        elif coupon.verified:
            used_coupon.append({"id": coupon.id, "img": coupon.coupons.img_wide})
        elif coupon.coupons.remain_num == 0:
            no_remain.append({"id": coupon.id, "img": coupon.coupons.img_wide})
    # coupons = User_Coupon.query.filter(User_Coupon.user_id == user.user_id, User_Coupon.verified == False).all()
    # coupon_list = [{"id": coupon.id, "coupon_name": coupon.coupon_name, "img": coupon.coupons.img_wide} for coupon in coupons]
    # print(coupon_list)
    return {"available_coupon": available_coupon, "used_coupon": used_coupon, "no_remain": no_remain}

@app.route("/liff/update", methods=["POST"])
def liff_update():
    # update_task: share_song_list, singer_info, logo_hunt
    data = request.json
    user = get_user(data["user_id"])
    result = update_task(user, data["task_name"], data["detail"])
    return {"updated": result, "task_name": data["task_name"]}

@app.route("/liff/raffle", methods=["POST"])
def liff_raffle():
    data = request.json
    user = get_user(data["user_id"])
    if user.raffle_num == 0: return {"updated": False}

    user_coupon = add_user_coupon(user)
    spin_deg = random.randint(2880, 3240)
    print(f"[Raffle] {spin_deg}")

    # if user_coupon.coupon_name == "line_point":
    #     link = f"https://txp.rs/viewvoucher.aspx?voucherguid={user_coupon.detail}"
    #     line_bot_api.push_message(user.user_id, TextSendMessage(text=f"恭喜你抽中 LINE POINTS! 點擊下方連結領取：{link}"))
    return {"updated": True, "spin_deg": spin_deg, "coupon_name": user_coupon.coupon_name, "detail": user_coupon.detail}

@app.route("/liff/push_message", methods=["POST"])
def liff_push_message():
    data = request.json
    user = get_user(data["user_id"])
    guid = data["user_id"]

    link = f"https://txp.rs/viewvoucher.aspx?voucherguid={guid}"
    line_bot_api.push_message(user.user_id, TextSendMessage(text=f"恭喜你抽中 LINE POINTS! 點擊下方連結領取：{link}"))

@app.route("/liff/check_coupon", methods=["POST"])
def liff_check_coupon():
    data = request.json
    user_coupon = User_Coupon.query.get(data["id"])

    if user_coupon.user_id != data["user_id"]:
        return {"result": False, "error": "User ID not match"}
    if user_coupon.verified:
        return {"result": False, "error": "Coupon has been used"}

    coupon = user_coupon.coupons
    return {"result": True, "img": coupon.img_large, "desc": coupon.description, "notice": coupon.notice}

@app.route("/liff/verify", methods=["POST"])
def liff_verify():
    data = request.json
    user_coupon = User_Coupon.query.get(data["id"])

    if user_coupon.user_id != data["user_id"]:
        return {"result": False, "error": "User ID not match"}
    if user_coupon.verified:
        return {"result": False, "error": "Coupon has been used"}

    user_coupon.verified = True
    user_coupon.coupons.remain_num -= 1
    db.session.commit()
    return {"result": True}

# main
if __name__ == "__main__":
    db.create_all()
    app.run()
