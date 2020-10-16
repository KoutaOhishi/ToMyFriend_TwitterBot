#coding: utf-8

import os, json
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime
import requests
from PIL import Image
from requests_oauthlib import OAuth1Session

Date = datetime.date.today()

REPOSITORY_PATH = str("/".join(os.path.abspath(__file__).split("/")[0:-2])) + "/ToMyFriend_TwitterBot"

WEB_URL = "https://www.seikyoonline.com/paper/"
API_URL = "https://notify-api.line.me/api/notify"
TOKEN = "YOUR_TOKEN"

DRIVER_BIN = REPOSITORY_PATH + "/chromedriver"

FILENAME = REPOSITORY_PATH + "/"+str(Date)+".png"

def web():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=DRIVER_BIN,chrome_options=chrome_options)

    print "open Google Chrome"
    driver.get(Web_url)

    driver.find_element_by_class_name("apspan").click() # ”もっと見る”をクリック

    html_list = driver.find_element_by_class_name("acc_dnone")
    items = html_list.find_elements_by_tag_name("li")

    get_image = False

    for item in items:
        if item.text.find(u"わが友に贈る") == True or item.text.find(u"今週のことば") == True:
            image_URL = str(item.find_element_by_tag_name("a").get_attribute("href"))
            print image_URL
            get_image = True
            print "open 聖教オンライン「わが友に贈る」"
            driver = webdriver.Chrome(executable_path=DRIVER_BIN,chrome_options=chrome_options)
            driver.get(image_URL)
            driver.find_element_by_class_name("type_d_main").click()

            #2020.3.27 サイトの仕様上、画像だけのページに移動できなくなった
            #driver.switch_to.window(driver.window_handles[1])
            #cur_url = driver.current_url
            #response = requests.get(cur_url, stream=True)
            #with open(FILENAME, 'wb') as file:
            #    for chunk in response.iter_content(chunk_size=1024):
            #        file.write(chunk)

            #2020.3.27 スクリーンショットを取ることで対応
            #driver.save_screenshot(FILENAME)
            #screen_shot = Image.open(FILENAME)
            #crop_img = screen_shot.crop((255, 282, 644, 473)) #(left, upper, right, lower)
            #crop_img.save(FILENAME, quality=100)
            
            #2020.10.16 オリジナルのURLを取得する方法に変更
            type_d_main = driver.find_element_by_class_name("type_d_main")
            img_tag = type_d_main.find_element_by_tag_name("img")
            img_url = img_tag.get_attribute("src")
            response = requests.get(img_url, stream=True)
            with open(FILENAME, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)

            print "close Google Chrome"


    if get_image == False:
        print "「わが友に贈る」のページが見つかりませんでした"
        send_error_message_to_line()

    driver.quit()


def line():
    headers = {"Authorization" : "Bearer " + TOKEN}
    message =  "[" + str(Date) + "]" + ' わが友に贈る'
    payload = {"message" : message}
    files = {"imageFile": open(FILENAME, "rb")}

    r = requests.post(API_URL ,headers = headers ,params=payload, files=files)

    print str(Date)+" Sent to Line Notify"

def send_error_message_to_line():
    headers = {"Authorization" : "Bearer " + TOKEN}
    message =  str(Date) + " 画像の取得に失敗しました。"
    payload = {"message" : message}

    r = requests.post(API_URL ,headers = headers ,params=payload)

    print str(Date)+" Sent error message to line"


def tweet():
    CK = "hogehoge" #CONSUMER_KEY
    CS = "hogehoge" #CONSUMER_SECRET
    AT = "hogehoge" #ACCESS_TOKEN
    ATS = "hogehoge" #ACCESS_TOKEN_SECRET
    twitter = OAuth1Session(CK, CS, AT, ATS)

    url_media = "https://upload.twitter.com/1.1/media/upload.json"
    url_text = "https://api.twitter.com/1.1/statuses/update.json"

    files = {"media" : open(FILENAME, 'rb')}
    req_media = twitter.post(url_media, files = files)

    if req_media.status_code != 200:
        print("MEDIA UPLOAD FAILED... %s", req_media.text)
        exit()

    media_id = json.loads(req_media.text)['media_id']

    text = "【"+str(Date)+"】\n#わが友に贈る" #投稿するメッセージ
    params = {"status" : text, "media_ids" : [media_id]}
    req_media = twitter.post(url_text, params = params)

    if req_media.status_code != 200:
        print("TEXT UPLOAD FAILED... %s", req_text.text)
        exit()

    print "Tweeted!"


def main():
    web()
    line()
    tweet()

if __name__ == "__main__":
    main()
