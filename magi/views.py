from django.shortcuts import render

from urllib.parse import quote
from datetime import datetime
import pytz
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ebaysdk import response
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
from ebaysdk.policies import Connection as Policies
from ebaysdk.exception import ConnectionError
from magi.core.scrape import Scrape
import magi.core.checkProduct as Check
from .serializers import *
from rest_framework import status


instance = ''

@api_view(['GET','POST'])
def getSellerProfile(request):
    print(request.data)
    inputs = request.data
    api = Policies(domain='svcs.ebay.com',config_file='ebay.yaml')
    res = api.execute('getSellerProfiles')
    result = res.dict()
    paymentProfiles = result['paymentProfileList']['PaymentProfile']
    returnProfiles = result['returnPolicyProfileList']['ReturnPolicyProfile']
    shippingProfiles = result['shippingPolicyProfile']['ShippingPolicyProfile']
    paymentlist = []
    returnlist = []
    shippinglist = []
    
    for payment in paymentProfiles:
        paymentRow = {}
        paymentRow['profileId'] = payment['profileId']
        paymentRow['profileName'] = payment['profileName']
        paymentlist.append(paymentRow)
    for returnPolicy in returnProfiles:
        returnRow = {}
        returnRow['profileId'] = returnPolicy['profileId']
        returnRow['profileName'] = returnPolicy['profileName']
        returnlist.append(returnRow)
    for shipping in shippingProfiles:
        shippingRow = {}
        shippingRow['profileId'] = shipping['profileId']
        shippingRow['profileName'] = shipping['profileName']
        shippinglist.append(shippingRow)
    result = {}
    result['paymentlist']   = paymentlist
    result['returnlist']   = returnlist
    result['shippinglist']   = shippinglist
    return Response(result)


    
@api_view(['GET','POST'])
def listProduct(request):
    

    request_data = request.data
    bussiness_policy = request_data['businessPolicy']
    input_values = request_data['inputValues']
    print(bussiness_policy,input_values)

    date_time = datetime.now(tz=pytz.timezone('Asia/Tokyo'))
    format = '%Y-%m-%d %H:%M:%S'
 
    string = date_time.strftime(format)
    serializer = LogSerializer(data = {'search_url':input_values['url'],'date_time':string})
    if serializer.is_valid():
        serializer.save()
    else:
        print(serializer.errors)  
       
  
    first_record = Setting.objects.first()
       
    if first_record is None:
        serializer = SettingSerializer(data=input_values)
        if serializer.is_valid():
                serializer.save()
        
    else:
        serializer = SettingSerializer(first_record,input_values,partial=True)
        if serializer.is_valid():
            serializer.save()
           
        else:
            print(serializer.errors) 
           
            return Response({"status": "500","errors":serializer.errors}, status=status.HTTP_200_OK)    
    scrape = Scrape(input_values,bussiness_policy)
    global instance
    instance = scrape
    
    scrape.extract()

    return Response({"status": "200"}, status=status.HTTP_200_OK) 

@api_view(['GET','POST'])
def getSettingInformation(request):
   setting = Setting.objects.first()
   serializer = SettingSerializer(setting)
   print(serializer.data)
   return Response({"status": "200", "result": serializer.data}, status=status.HTTP_200_OK) 

@api_view(['GET','POST'])   
def stopListing(request):
    global instance
    if instance != '':
       instance.stop()
       return Response({"status": "200"}, status=status.HTTP_200_OK) 
    if instance == '':
       instance.stop()
       return Response({"status": "200"}, status=status.HTTP_200_OK) 

@api_view(['GET','POST'])   
def getListingStatus(request):
    global instance
   
    if instance != '':
        result = instance.getListingStatus()
        return Response({"status": "200","result":result}, status=status.HTTP_200_OK) 

    if instance == '':
        return Response({"status": "500","instance":instance}, status=status.HTTP_200_OK) 


@api_view(['GET','POST'])
def getLog(request):
   logs = Log.objects.all()
   serializer = LogSerializer(logs, many=True)
   print(serializer.data)
   return Response({"status": "200", "result": serializer.data}, status=status.HTTP_200_OK)     


@api_view(['GET','POST'])
def getProducts(request):
    input = request.data
    products = Product.objects.filter(log_id=input['log_id']).values('id','title','price','image_url','listing_date','item_code')
    data = list(products)
    return Response({"status": "200", "result": data}, status=status.HTTP_200_OK) 

@api_view(['GET','POST'])    
def checkProductStatus(request):
    
    settingObject = Setting.objects.first()
    settingSerializer = SettingSerializer(settingObject)
    setting = settingSerializer.data
    
    products = Product.objects.all()
    serializer = ProductSerializer(products,many=True)

    for product in serializer.data:
        if (product['item_code'] != None) and (product['listing_date'] != None):
            Check.checkPrice(product['item_url'],product['item_code'],product['price'],product['listing_date'],product['countdowned_date'],setting)
            print('hi')

    return Response({"status": "200"}, status=status.HTTP_200_OK)             