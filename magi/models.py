from django.db import models


class Setting(models.Model):
  currency_rate = models.CharField(max_length=255)
  profit_rate = models.CharField(max_length=255)
  countdown_duration = models.CharField(max_length=255)
  countdown_money = models.CharField(max_length=255)
  endlist_duration = models.CharField(max_length=255)
  description = models.TextField(max_length=10000)
  shipping_cost1 = models.CharField(max_length=255)
  shipping_cost2 = models.CharField(max_length=255)
  shipping_cost3 = models.CharField(max_length=255)
  shipping_cost4 = models.CharField(max_length=255)
  class Meta:
        db_table = 'setting' 

class Product(models.Model):
  log_id = models.CharField(max_length=255,null=True)
  item_url = models.CharField(max_length=255,null=True)
  item_code = models.CharField(max_length=255,null=True)
  image_url = models.CharField(max_length=255,null=True)
  title = models.CharField(max_length=255,null=True)
  price = models.CharField(max_length=255,null=True)
  listing_date = models.CharField(max_length=255,null=True)
  countdowned_date = models.CharField(max_length=255,null=True)

  class Meta:
        db_table = 'product'         

class Log(models.Model):
  search_url = models.CharField(max_length=1000)
  date_time = models.TextField(max_length=255)
  class Meta:
        db_table = 'log'   

        
class Character(models.Model):
  japanese_name = models.CharField(max_length=255)                
  english_name = models.CharField(max_length=255)                
  class Meta:
        db_table = 'character'