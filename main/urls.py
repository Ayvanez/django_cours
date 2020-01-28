from django.urls import path
from .views import *

urlpatterns = [
 path('login', login, name='login'),
 path('logout', logout, name='logout'),
 path('register', register, name='register'),
 path('groups', groups_view, name='groups_view'),
 path('main', main_view, name='main'),
 path('group/<int:group_id>', group_detail, name='group_detail'),
 path('group/create', group_create, name='group_create'),
 path('group/edit', group_edit, name='group_edit')

]