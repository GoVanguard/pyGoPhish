from django.urls import path
from . import views


urlpatterns = [
    # /
    path('', views.root, name='root'),
    path('home', views.home, name='home'),
    path('signin', views.signIn, name='signin'),
    path('signout', views.signOut, name='signout'),
    path('domain', views.home, name='domain'),
    path('callback', views.callback, name='callback'),
    path('gophish', views.goPhish, name='gophish'),
    path('setup', views.emailSetup, name='setup'),
    path('test', views.emailTest, name='test'),
    path('schedule', views.PhishingTripListView.as_view(), name='schedule'),
    path('schedule/<slug:pk>', views.PhishingTripDetailView.as_view(), name='schedule-detail'),
]
