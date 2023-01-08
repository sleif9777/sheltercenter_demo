from django.urls import path

from . import views

urlpatterns = [
    path('redirect/', views.display_list, name="display_list"),
    path('admin/', views.display_list_admin, name="display_list_admin"),
    path('remove/<int:dog_id>/', views.remove_dog_from_wishlist, name="remove_dog_from_wishlist"),
    path('litters/', views.litter_mgmt, name="litter_mgmt"),
    path('', views.display_list_adopter, name="display_list_adopter"),
    path('email_batch/<str:message_type>/<int:litter_id>/', views.create_watchlist_email_batch, name="create_watchlist_email_batch_litter"),
    path('email_batch/<str:message_type>/<int:dog_id>', views.create_watchlist_email_batch, name="create_watchlist_email_batch_dog"),

]
