import PySimpleGUI as sg
import threading
from threading import Thread, Event

from PySimpleGUI.PySimpleGUI import Input
from tkinter import messagebox
from ebaysdk import response
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
from ebaysdk.policies import Connection as Policies

from core.scrape import Scrape



def output():

    
    api = Policies(domain='svcs.ebay.com',config_file='config/ebay.yaml')
    res = api.execute('getSellerProfiles')
    result = res.dict()
    paymentProfiles = result['paymentProfileList']['PaymentProfile']
    returnProfiles = result['returnPolicyProfileList']['ReturnPolicyProfile']
    shippingProfiles = result['shippingPolicyProfile']['ShippingPolicyProfile']
    paymentlist = []
    returnlist = []
    shippinglist = []
    paymentID = []
    returnID = []
    shippingID = []
    for payment in paymentProfiles:
        paymentlist.append(payment['profileName'])
        paymentID.append(payment['profileId'])
    for returnPolicy in returnProfiles:
        returnlist.append(returnPolicy['profileName'])
        returnID.append(returnPolicy['profileId'])
    for shipping in shippingProfiles:
        shippinglist.append(shipping['profileName'])
        shippingID.append(shipping['profileId']) 

    layout =[

            [sg.Text('入力URL:',size=(17,1)),sg.Input(default_text = "https://magi.camp/items/search?forms_search_items%5Bkeyword%5D=PSA10&forms_search_items%5Bgoods_id%5D=1&forms_search_items%5Bbrand_id%5D=3&forms_search_items%5Bseries_id%5D=31&forms_search_items%5Bfrom_price%5D=&forms_search_items%5Bto_price%5D=1000000&forms_search_items%5Bquality%5D=old&forms_search_items%5Bstatus%5D=presented&forms_search_items%5Bsort%5D=price_desc&forms_search_items%5Bpage%5D=1", size=(70, 1), key='url')],
            [sg.Text("為替レート:１万円:",size=(17,1)),sg.Input(size=(10,1),default_text="80",key='rating'),sg.Text("$")],
            [sg.Text("価格改定：",size=(17,1)),sg.Input(size=(10,1),default_text="1.5",key='priceTime')],
            [sg.Text("ビジネスポリシーを選択してください")],
            [sg.Text("Payment Policy", size=(15,1)),sg.Text("Return Policy",size=(15,1)),sg.Text("Shipping Policy")],
            [sg.Listbox(paymentlist, size=(15, 5),key='paymentlist', enable_events=True,),sg.Listbox(returnlist, size=(15, 5),key='returnlist', enable_events=True),sg.Listbox(shippinglist, size=(15, 5),key='shippinglist', enable_events=True)],
            [sg.Text('',size=(55,1)),sg.Button('Start',size=(10,1)),  sg.Button('Stop',size=(10,1))],
 
        ]

    window = sg.Window('Magi -> Ebay',layout)
    event_t = Event()
    checkformflag1=True
    checkformflag2=True
    checkformflag3=True
    checkformflag4=True
    checkformflag5=True
    checkPayment=False
    checkReturn=False
    checkShipping=False

    while True:
        event,values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        elif event == "Start":

            if values['paymentlist'] != []:
                checkPayment = True
            else:
                messagebox.showinfo("Alert","Please select payment policy")  

            if  values['returnlist'] != []:
                checkReturn = True
            else:
                messagebox.showinfo("Alert","Please select return policy")  

            if values['shippinglist'] != []:
                checkShipping = True
            else:
                messagebox.showinfo("Alert","Please select shipping policy") 


            if values['url'] == '':
                messagebox.showinfo("Alert","Please input Target Url")
                checkformflag1=False
            else: 
                checkformflag1=True
            if values['rating']=='':
                messagebox.showinfo('Alert',"Please input exchange rating")
                checkformflag2=False
            else:
                checkformflag2=True
            if values['priceTime']=='':
                messagebox.showinfo("Alert","Please input Price Time")   
                checkformflag3=False
            else:
                checkformflag3=True
            
            if checkformflag1==True&checkformflag2==True&checkformflag3==True&checkPayment==True&checkReturn==True&checkShipping==True:
                        
                paymentIndex = paymentlist.index(values['paymentlist'][0])
                returnIndex = returnlist.index(values['returnlist'][0])
                shippingIndex = shippinglist.index(values['shippinglist'][0])
                paymentId = paymentID[paymentIndex]
                returnId = returnID[returnIndex]
                shippingId = shippingID[shippingIndex]
                scrape = Scrape(values['url'],values['rating'],values['priceTime'],values['paymentlist'],values['returnlist'],values['shippinglist'],paymentId,returnId,shippingId)
                event_t.clear()
                t = threading.Thread(target=scrape.extract,args=(event_t,), daemon=True)
                t.start()
                window['Start'].Update(disabled=True)
                
        elif event == "Stop":
            window['Start'].Update(disabled=False)
            event_t.set()
           
        elif event == sg.WINDOW_CLOSED:
            event_t.set()
            break