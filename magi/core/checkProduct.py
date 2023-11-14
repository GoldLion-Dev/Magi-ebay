import requests
import re
from bs4 import BeautifulSoup
from magi.serializers import *
from ebaysdk import response
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
from ebaysdk.policies import Connection as Policies
from datetime import datetime
import pytz

def checkPrice(item_link,item_code,database_price,listing_date,countdowned_date,setting):

    currency_rate = setting['currency_rate'] 
    profit_rate = setting['profit_rate']   

    try:
        response = requests.get(item_link)
        soup = BeautifulSoup(response.content,'html.parser')
        original_price = soup.select_one('.item-detail__price').text
        price_list = re.findall(r"[0-9]+", original_price)
        total_price = ''
        if type(price_list) == list:
            for price in price_list:
                total_price = total_price + price
        else:
            total_price = price_list 
        if total_price != database_price:
            # print(total_price)
            print(database_price)
            product = Product.objects.get(item_url=item_link)
            serializer = ProductSerializer(product,{"price":total_price},partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors) 

            
            try:
                # Create a connection to the eBay Trading API
                api = Trading(domain='api.ebay.com',config_file='ebay.yaml')

                # Specify the item ID of the listing you want to update
                item_id = item_code
                shipping_cost = calculateShippingCost(total_price,setting)
                # Specify the new price for the listing
                price = float(total_price) + float(shipping_cost)
                new_price = price * float(setting['currency_rate']) * float(setting['profit_rate']) / 10000 

                # Create the request to revise the item's price
                request = {
                    'Item': {
                        'ItemID': item_id,
                        'StartPrice': new_price
                    }
                }

                # Send the revise request to eBay
                response = api.execute('ReviseFixedPriceItem', request)

                if response.reply.Ack == 'Success':
                    print('Price successfully updated.')
                else:
                    print('Error updating price:', response.reply.Errors)
            except:
                pass        
    except:
        # Set the item ID and the new quantity
        item_id = item_code
        new_quantity = 0

        try:
            # Create a Trading API connection
            api = Trading(domain='api.ebay.com',config_file='ebay.yaml')

            # Create the request XML payload
            request_data = {
                'InventoryStatus': {
                    'ItemID': item_id,
                    'Quantity': new_quantity
                }
            }

            # Call the ReviseInventoryStatus API
            response = api.execute('ReviseInventoryStatus', request_data)

            # Check the response status
            if response.reply.Ack == 'Success':
                print('Inventory updated successfully.')
            else:
                print('Failed to update inventory.')

        except Exception as e:
            print('An error occurred:', str(e))      
            pass 



    current_time = datetime.now(tz=pytz.timezone('Asia/Tokyo'))
        # format specification
    format = '%Y-%m-%d'

    # applying strftime() to format the datetime
    datetime_string = current_time.strftime(format)

    # Convert the strings to datetime objects
    date1 = datetime.strptime(listing_date, '%Y-%m-%d').date()
    date2 = datetime.strptime(datetime_string, '%Y-%m-%d').date()

    # Calculate the difference between the two dates
    delta = date2 - date1

    # Print the number of days between the two dates
    print(delta.days)

    if float(delta.days) > float(setting['countdown_duration']) and float(delta.days) < float(setting['endlist_duration']) and countdowned_date == None:
        product = Product.objects.get(item_url=item_link)
        serializer = ProductSerializer(product,{"countdowned_date":datetime_string},partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors) 

        changed_price = float(database_price) - float(setting['countdown_money'])

        try:
            # Create a connection to the eBay Trading API
            api = Trading(domain='api.ebay.com',config_file='ebay.yaml')

            # Specify the item ID of the listing you want to update
            item_id = item_code

            # Specify the new price for the listing
            new_price = changed_dollar_price
            shipping_cost = calculateShippingCost(changed_price,setting)
            # Specify the new price for the listing
            price = float(changed_price) + float(shipping_cost)
            new_price = price * float(setting['currency_rate']) * float(setting['profit_rate']) / 10000 
            # Create the request to revise the item's price
            request = {
                'Item': {
                    'ItemID': item_id,
                    'StartPrice': new_price
                }
            }

            # Send the revise request to eBay
            response = api.execute('ReviseFixedPriceItem', request)

            if response.reply.Ack == 'Success':
                print('Price successfully updated.')
            else:
                print('Error updating price:', response.reply.Errors)
        except:
            pass    

    if float(delta.days) > float(setting['endlist_duration']):    

        # Set the item ID and the new quantity
        item_id = item_code
        new_quantity = 0

        try:
            # Create a Trading API connection
            api = Trading(domain='api.ebay.com',config_file='ebay.yaml')

            # Create the request XML payload
            request_data = {
                'InventoryStatus': {
                    'ItemID': item_id,
                    'Quantity': new_quantity
                }
            }

            # Call the ReviseInventoryStatus API
            response = api.execute('ReviseInventoryStatus', request_data)

            # Check the response status
            if response.reply.Ack == 'Success':
                print('Inventory updated successfully.')
            else:
                print('Failed to update inventory.')

        except Exception as e:
            print('An error occurred:', str(e))      
            pass 



def calculateShippingCost(price,setting):
        price = float(price)
        if price < 3000:
            return setting['shipping_cost1']
        if price >= 3000 and price < 10000:
            return setting['shipping_cost2']
        if price <= 10000 and price < 20000:
            return setting['shipping_cost3']
        if price >= 20000 :
            return setting['shipping_cost4']



    