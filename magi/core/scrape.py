from bs4 import BeautifulSoup
from urllib.parse import quote
from langdetect import detect
from tkinter import messagebox
import requests
import re
import json
import sqlite3
# import MeCab
from datetime import datetime
import pytz
import sudachipy
from magi.serializers import *
from ebaysdk import response
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
from ebaysdk.policies import Connection as Policies


listing_status = ''
class Scrape:

    def __init__(self,input_values=None,bussiness_policy=None):
        self.url = input_values['url']
        self.currency_rate = input_values['currency_rate']
        self.profit_rate = input_values['profit_rate']
        self.description = input_values['description']
        self.paymentList = bussiness_policy['payment']['profileName']
        self.returnList = bussiness_policy['return']['profileName']
        self.shippingList = bussiness_policy['shipping']['profileName']
        self.paymentId = bussiness_policy['payment']['profileId']
        self.returnId = bussiness_policy['return']['profileId']
        self.shippingId = bussiness_policy['shipping']['profileId']
        self.psa10 = ''
        self.psa9 = ''
        if 'graded' in input_values:
            self.graded = True
        else:
            self.graded = False  
        if 'psa' in input_values:
            if input_values['psa'] == 'psa10':
              self.psa10 = True
            if input_values['psa'] == 'psa9':
              self.psa9 = True  
       
        self.character = ''
       

    def extract(self):
        url = self.url
        global listing_status
        listing_status = 'start'

        while True:
           
            response = requests.get(url)
            soup = BeautifulSoup(response.content,'html.parser')
            if soup.select_one('.next a') == None:
                break
            next_url = soup.select_one('.next a')
            next_url = next_url['href']

            item_links = [a['href'] for a in soup.select('.item-list__box a')]
            for item_link in item_links:
                

                image_list = []
                item_link = 'https://magi.camp' + item_link 
                result = self.checkItemCode(item_link)
                if result == True:
                    try:
                        response = requests.get(item_link)
                        soup = BeautifulSoup(response.content,'html.parser')
                        title = soup.select_one('.item-detail h2').text
                        replaced_title = self.replaceCharacterName(title)
                        translated_title = self.translate(replaced_title)
                    
                    except:
                        pass
                  
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
                    translated_description = self.translate(description)

                    # current date and time
                    date_time = datetime.now(tz=pytz.timezone('Asia/Tokyo'))

                        # format specification
                    format = '%Y-%m-%d %H:%M:%S'

                        
                        # applying strftime() to format the datetime
                    datetime_string = date_time.strftime(format)
                   
                    self.listProduct(translated_title,self.description,total_price, image_list, self.character,item_link)
                    self.character = ''
                  
                    if listing_status == 'stop':
                        print('The thread was stopped in if.')
                        break
                  
          
            url = 'https://magi.camp' + next_url
            if listing_status == 'stop':
                print('The thread was stopped in if.')
                break
        listing_status = 'stop'
        return 
       


    def convertToEncodeURL(self,sentence):
        converted_string = quote(sentence)
        return converted_string

    def translate(self,sentence):
        root_url = "http://translate.google.com/translate_a/single?client=webapp&sl=auto&tl=en&hl=en&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&dt=gt&pc=1&otf=1&ssel=0&tsel=0&kc=1&tk=&q="
        root_url = root_url + self.convertToEncodeURL(sentence)
        headers = {"Content-Type": "application/json"}
        response = requests.post(root_url, headers=headers)
        content = response.content.decode('utf-8')
        content = json.loads(content)
        return content[0][0][0]
     
    def replaceCharacterName(self,title):

        records = Character.objects.all()
        serializer = CharacterSerializer(records, many=True)
        title_collection = self.extract_japanese_words(title)

        for record in serializer.data:
            japanese_name = record['japanese_name']

            for item in title_collection:   
                if item == japanese_name:
                    title = title.replace(japanese_name,record['english_name'])
                    self.character = record['english_name']
                  

        print(title)
        return title


    def extract_japanese_words(self,sentence):
        tokenizer = sudachipy.Dictionary().create()
        tokens = tokenizer.tokenize(sentence)
        japanese_words = []
        
        for token in tokens:
            if token.part_of_speech()[0] == '名詞':  # Only consider nouns
                japanese_words.append(token.surface())
        print(japanese_words)        
        
        return japanese_words
        
         


    def checkItemCode(self, itemCode):

        record = Product.objects.filter(item_url=itemCode).first()
        
        if record is None:
            serializer = ProductSerializer(data={'item_url':itemCode})
            if serializer.is_valid():
                    serializer.save()
            return True        
        else:
            return False
        
    def listProduct(self,title, description, price, image_list,character,item_link):
        
        setting = Setting.objects.first()
        serializer = SettingSerializer(setting)
        setting = serializer.data
        shipping_cost = self.checkShippingCost(price,setting)
        print(shipping_cost)
        original_price = price
        price = float(price) + float(shipping_cost)
        price = price * float(self.currency_rate) * float(self.profit_rate) / 10000 
        qty = '1'
        categoryId = '183454'

       
        if self.graded == False:
                conditionId = '4000'
                
        else:
                conditionId = '2750'   
    
        
        try:
            api = Trading(domain='api.ebay.com',config_file='ebay.yaml')
        
            request = {
                            "Item":{
                                            "Title":"<![CDATA[{0}]]>".format(title),
                                            "Description":"<![CDATA[{0}]]>".format(description),
                                            "ListingDuration":"GTC",
                                            "ListingType":"FixedPriceItem",
                                            "Location":"Japan",
                                            "StartPrice":"{}".format(price),
                                            "Country":"JP",
                                            "Currency":"USD",
                                            "Quantity":"{}".format(qty),
                                            "ConditionID":"{}".format(conditionId),
                                            "ConditionDescriptors":{
                                                "ConditionDescriptor":{}
                                            },
                                            "SKU":"{}".format(item_link),
                                            "ConditionDisplayName":"Graded",
                                            "PaymentMethods":"PayPal",
                                            "PayPalEmailAddress":"kevinzoo.lancer@gmail.com",
                                            "DispatchTimeMax":"1",
                                            "ShipToLocations":"None",
                                            "ReturnPolicy":{
                                                "ReturnsAcceptedOption":"ReturnsAccepted",
                                                "ReturnsWithinOption":"Days_30"
                                            },
                                            "PrimaryCategory":{
                                                "CategoryID":"{}".format(categoryId)
                                            },
                                            "PictureDetails":{
                                                "PictureURL":image_list,
                                            },
                                            "ItemCompatibilityList":{
                                                    "Compatibility":{
                                                        "NameValueList":[
                                                            {"Name":"Year","Value":"2010"},
                                                            {"Name":"Make","Value":"Hummer"},
                                                            {"Name":"Model","Value":"H3"}
                                                        ],
                                                        "CompatibilityNotes":"An example compatibility"
                                                    }
                                            },

                                        

                                            "ItemSpecifics":{
                                                "NameValueList":[
                                                  
                                                {
                                                        "Name":"UPC",
                                                        "Value":"Does not apply"
                                                    },
                                                    
                                                {
                                                        "Name":"Game",
                                                        "Value":"Pokémon TCG"
                                                    },
                                                    
                                                    
                                                {
                                                        "Name":"Card Name",
                                                        "Value":"Pokemon Card"
                                                    },
                                                
                                               
                                                {
                                                        "Name":"Card Type",
                                                        "Value":"No  Pokémonset "
                                                    },
                                                
                                                {
                                                        "Name":"Character",
                                                        "Value":"{}".format(self.character)
                                                    },
                                                
                                                
                                                ]
                                            },

                                        "SellerProfiles":{

                                                    "SellerPaymentProfile":{
                                                    
                                                            "PaymentProfileName":"{}".format(self.paymentList[0]),  
                                                            "PaymentProfileID":"{}".format(self.paymentId)
                                                            },
                                                    "SellerReturnProfile":{
                                            
                                                            "ReturnProfileName":"{}".format(self.returnList[0]),  
                                                            "ReturnProfileID":"{}".format(self.returnId)
                                                    },
                                                    "SellerShippingProfile":{
                                                
                                                            "ShippingProfileName": "{}".format(self.shippingList[0]),
                                                            "ShippingProfileID":"{}".format(self.shippingId) 
                                                    },
                                            } ,

            
            
                                            
                                            "Site":"US"

                                    }
                                            
                    
                        }


            if self.graded == False:
                conditionId = '4000'
                conditionDescriptorName = '40001'
                conditionDescriptorValue = '400010'
                conditionDescriptor = {
                    "Name":"{}".format(conditionDescriptorName),     
                    "Value":"{}".format(conditionDescriptorValue),
                }
                request['Item']['ConditionDescriptors']['ConditionDescriptor'] = conditionDescriptor
            else:
                conditionId = '2750'   
                conditionDescriptorName = '27501' 
                conditionDescriptorValue = '275010' 
                conditionDescriptorName1 = '27502' 
           
                if self.psa10 == True:
                    conditionDescriptorValue1 = '275020' 
                if self.psa9 == True:
                    conditionDescriptorValue1 = '275022'
                if self.psa10 == '' & self.psa9 == '':
                    conditionDescriptorValue1 = '275020' 

                conditionDescriptor = [
                    {
                        "Name":"{}".format(conditionDescriptorName),     
                        "Value":"{}".format(conditionDescriptorValue),
                    },
                    {
                        "Name":"{}".format(conditionDescriptorName1),     
                        "Value":"{}".format(conditionDescriptorValue1),
                    }
                ]

                
            request['Item']['ConditionDescriptors']['ConditionDescriptor'] = conditionDescriptor
            response=api.execute("AddItem", request)
            print(response.dict())
            if ('ItemID' in response.dict()):
                res  = response.dict()
                self.itemId = res['ItemID']
                print(self.itemId)
                date_time = datetime.now(tz=pytz.timezone('Asia/Tokyo'))
                # format specification
                format = '%Y-%m-%d'

                # applying strftime() to format the datetime
                datetime_string = date_time.strftime(format)
                print(datetime_string)
                log_id = Log.objects.latest('id').id
                product = Product.objects.get(item_url=item_link)
                if type(image_list) == list:
                    image = image_list[0]
                else:
                    image = image_list    
                serializer = ProductSerializer(product,data={'log_id':log_id,'title':title,'price':original_price,'image_url':image,'listing_date':datetime_string,'item_code':self.itemId},partial=True)
                if serializer.is_valid():
                    serializer.save()
                return True        
              
            print(response.reply)

        except ConnectionError as e:
            print(e)
            print(e.response.dict())
            pass     

        # return    




    def stop(self):
        global listing_status
        listing_status = 'stop'


    def getListingStatus(self):
        global listing_status
        return listing_status

    def checkShippingCost(self,price, setting):
        price = float(price)
        if price < 3000:
            return setting['shipping_cost1']
        if price >= 3000 and price < 10000:
            return setting['shipping_cost2']
        if price <= 10000 and price < 20000:
            return setting['shipping_cost3']
        if price >= 20000 :
            return setting['shipping_cost4']
