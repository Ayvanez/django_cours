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
 path('group/edit/<int:group_id>', group_edit, name='group_edit'),
 path('teacher/<int:teacher_id>', teacher_schedule, name='teacher_schedule'),
 path('teacher/create', teacher_create, name='teacher_create'),
 path('teacher/edit/<int:teacher_d>/', teacher_edit, name='teacher_edit'),
 path('student/create', student_create, name='student_create'),
 path('student/edit/<int:student_id>', student_edit, name='student_edit'),
 path('discipline/create', discipline_create, name='discipline_create'),
 path('discipline/edit/<int:discipline_id>', discipline_edit, name='discipline_edit'),
 path('programme/create', programme_create, name='programme_create'),
 path('programme/edit/<int:programme_id>', programme_edit, name='programme_edit'),
 path('admin', admin, name='admin'),
 path('make/moderator/<int:user_id>', make_moderator, name='make_moderator'),
 path('make/user/<int:user_id>', make_user, name='make_user')
]