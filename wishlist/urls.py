from django.urls import path

from . import views

urlpatterns = [
    path('redirect/', views.display_list, name="display_list"),
    path('admin/', views.display_list_admin, name="display_list_admin"),
    path('', views.display_list_adopter, name="display_list_adopter"),

]
