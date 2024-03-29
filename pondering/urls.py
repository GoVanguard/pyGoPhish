from django.urls import path
from pondering import views
from django.urls import re_path 
from django.views.generic import RedirectView


urlpatterns = [
    path('', views.root, name='root'),
    path('home', views.home, name='home'),
    path('signin', views.signIn, name='signin'),
    path('callback', views.callback, name='callback'),
    path('signout', views.signOut, name='signout'),
    path('domain', views.home, name='domain'),
    path('gophish', views.goPhish, name='gophish'),
    path('setup', views.emailSetup, name='setup'),
    path('test', views.emailTest, name='test'),
    path('enumerate', views.enumerate, name='enumerate'),
    path('modify', views.PhishingListView.as_view(), name='modify'),
    path('schedule', views.PhishingTripListView.as_view(), name='schedule'),
    path('settings/<slug:pk>', views.PhishingTripDetailView.as_view(), name='schedule-detail'),
]
