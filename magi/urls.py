from django.urls import path
from . import views

urlpatterns = [
   
    path('getSellerProfile',views.getSellerProfile),
    path('listProduct',views.listProduct),
    path('getSettingInformation',views.getSettingInformation),
    path('stop',views.stopListing),
    path('getListingStatus',views.getListingStatus),
    path('getLog',views.getLog),
    path('getProducts',views.getProducts),
    path('checkProductStatus',views.checkProductStatus)


]
