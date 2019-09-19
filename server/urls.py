from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^card-list$', views.card_list),
    url(r'^namegen$', views.name_generator),
]