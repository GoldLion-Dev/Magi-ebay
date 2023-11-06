from bs4 import BeautifulSoup
from urllib.parse import quote
from datetime import datetime
from langdetect import detect
from threading import Thread, Event
from tkinter import messagebox
import requests
import re
import json
import sqlite3
import MeCab
import pytz


class Scrape:

    character_name = ''
    def __init__(self,url=None,currency_rate=None,profit_rate=None,paymentList=None,returnList=None,shippingList=None,paymentId=None,returnId=None,shippingId=None ):
        self.url = url
        self.currency_rate = currency_rate
        self.profit_rate = profit_rate
        self.paymentList = paymentList
        self.returnList = returnList
        self.shippingList = shippingList
        self.paymentId = paymentId
        self.returnId = returnId
        self.shippingId = shippingId


    def extract(self,event:Event):
        global character_name
        url = self.url
        while True:
            if event.is_set():
                print('The thread was stopped prematurely.')
                break
            messagebox.showinfo('hi','pass while')
            response = requests.get(url)
            soup = BeautifulSoup(response.content,'html.parser')
            if soup.select_one('.next a') == None:
                break
            messagebox.showinfo('hi','pass pagination')    
            next_url = soup.select_one('.next a')
            next_url = next_url['href']
            item_links = [a['href'] for a in soup.select('.item-list__box a')]
            for item_link in item_links:
                messagebox.showinfo('hi','pass all product')
                if event.is_set():
                    print('The thread was stopped prematurely.')
                    break

                image_list = []
                item_link = 'https://magi.camp' + item_link 
                response = requests.get(item_link)
                soup = BeautifulSoup(response.content,'html.parser')
                title = soup.select_one('.item-detail h2').text
                messagebox.showinfo('hi',title)
                print(title)
                
                replaced_title = self.replaceCharacterName(title)
                messagebox.showinfo('hi',replaced_title)
                translated_title = self.translate(replaced_title)
                print(translated_title)
                print(character_name)
                # self.translate(title)
                image_links = soup.select('.js-slider-thumb')
                for image_link in image_links:
                    image_list.append(image_link['src'])

                original_price = soup.select_one('.item-detail__price').text
                price_list = re.findall(r"[0-9]+", original_price)
                total_price = ''
                if type(price_list) == list:
                    for price in price_list:
                        total_price = total_price + price
                else:
                    total_price = price_list        
                description = soup.select_one('.item-introduction').text
                # print(image_list)
                print(total_price)
                messagebox.showinfo('hi',total_price)
                # print(description)

                  # current date and time
                date_time = datetime.now(tz=pytz.timezone('Asia/Tokyo'))

                    # format specification
                format = '%Y-%m-%d %H:%M:%S'

                    
                    # applying strftime() to format the datetime
                datetime_string = date_time.strftime(format)
                file_path = 'logs/log.txt'
                try:
                    file = open(file_path, 'a',encoding='utf-8')

                except:
                    messagebox.showinfo('alert','log file error') 

                
                file.write(datetime_string + '\n')
                file.write(translated_title + '\n')
                file.write(character_name + '\n')
                file.write(total_price + '\n')
                file.close()
                character_name = ''
              
            url = 'https://magi.camp' + next_url

        messagebox.showinfo("通知","商品の出品は終了しました。") 


    def convertToEncodeURL(self,sentence):
        converted_string = quote(sentence)
        return converted_string

    def translate(self,sentence):
        root_url = "http://translate.google.com/translate_a/single?client=webapp&sl=auto&tl=en&hl=en&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&dt=gt&pc=1&otf=1&ssel=0&tsel=0&kc=1&tk=&q="
        root_url = root_url + self.convertToEncodeURL(sentence)
        response = requests.get(root_url)
        content = response.content.decode('utf-8')
        content = json.loads(content)
        return content[0][0][0]
     
    def replaceCharacterName(self,title):
        global character_name
        database = r"database\character.db"
        try:
           con = sqlite3.connect(database)

        except:
            messagebox.showinfo('alert','database error')   
    
        cursor = con.cursor()
        sqlite_select_query = """SELECT * from character"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        messagebox.showinfo('hi','pass database')

        title_collection = self.extract_japanese_words(title)
        messagebox.showinfo('hi','title collection')

        for record in records:
            japanese_name = record[1]
          

            for item in title_collection:
               
                if item == japanese_name:
                    title = title.replace(japanese_name,record[2])
                    character_name = record[2]
                  
        messagebox.showinfo('hi','pass for')
        messagebox.showinfo('hi',title)

        print(title)
        return title


    def extract_japanese_words(self,sentence):
        
         messagebox.showinfo('hi','into extract words')
        
         try:

            wakati = MeCab.Tagger("-Owakati")
         except:

            messagebox.showinfo('hi',' no pass mecab')

         try:
             content =  wakati.parse(sentence).split()
         except:
             messagebox.showinfo('hi','extracted japanese word error')

         return content