from django.shortcuts import render, redirect
from django import forms
from django.urls import reverse
import time
import json
import os
import datetime


def find_person(login_name, password):
    with open('Users.json', 'r', encoding='UTF-8') as file:
        data2 = json.load(file)
    for person in data2['users']:
        if person['login'] == login_name:
            if person['password'] == password:
                return person
        else:
            return False
    return False


class UserCreationForm(forms.Form):
    login = forms.CharField(max_length=32)
    surname = forms.CharField(max_length=32)
    name = forms.CharField(max_length=32)
    patronymic = forms.CharField(max_length=32)
    password1 = forms.CharField(max_length=32, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=32, widget=forms.PasswordInput)

    def save(self):
        with open('Users.json', 'r', encoding='utf8') as users_file:
            users = json.load(users_file)

        new_user = {
            'id': int(time.time()),
            'login': self.cleaned_data['login'],
            'password': self.cleaned_data['password1'],
            'full_name': self.cleaned_data['surname'] + ' ' + self.cleaned_data['name'] + ' ' + self.cleaned_data[
                'patronymic']
        }
        with open('Users.json', 'w', encoding='utf8') as users_file:
            users['users'].append(new_user)
            json.dump(users, users_file)
        return new_user

    def is_valid(self):
        if super().is_valid():
            if self.cleaned_data['password1'] == self.cleaned_data['password2']:
                return True
        return False


class UserLoginForm(forms.Form):
    login = forms.CharField(max_length=32)
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)


def auth(request, user):
    request.session['user'] = user


def login(request):
    if 'person' in request.session:
        return redirect(reverse('main_page'))
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            person = find_person(form.cleaned_data['login'], form.cleaned_data['password'])
            if person:
                auth(request, person)
                return redirect(reverse('main_page'))
        return redirect(reverse('login'))
    form = UserLoginForm()
    return render(request, 'autorization.html', {"form": form})


def logout(request):
    if 'user' in request.session:
        del request.session['user']
    return redirect(reverse('main'))


def is_auth(request):
    return 'user' in request.session


def register(request):
    if is_auth(request):
        return redirect(reverse('main'))
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth(request, user)
            return redirect(reverse('groups_view'))
        else:
            return redirect(reverse('register'))
    form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def groups_view(request):
    with open('Groups.json', 'r', encoding='utf8') as groups_data, \
            open('Students.json', 'r', encoding='utf8') as studets_data:
        groups = json.load(groups_data)
        groups_list = groups['groups']
        students = json.load(studets_data)
        students_list = students['students']
        for group in groups_list:
            for i in range(len(group['students'])):
                for student in students_list:
                    if group['students'][i] == student['id']:
                        group['students'][i] = student
        print(groups_list)
        return render(request, 'group_list.html', {'group_list': groups_list})


days_of_week = {
    0: 'понедельник',
    1: 'вторник',
    3: 'среда'
}


def add(to, list_name, element):
    with open(to, 'r', encoding='utf8') as file:
        data = json.load(file)

    data[list_name].append(element)
    with open(to, 'w', encoding='utf8') as file:
        json.dump(data, file)

    return 1


def edit(to, list_name, element):
    with open(to, 'r', encoding='utf8') as file:
        data = json.load(file)

    for i in range(len(data[list_name])):
        if data[list_name][i]['id'] == element['id']:
            data[list_name][i] = element
            break
    else:
        return 0

    with open(to, 'w', encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False)

    return 1


def get(frm, list_name, value, field='id'):
    with open(frm, 'r', encoding='utf8') as file:
        data = json.load(file)
    for el in data[list_name]:
        if el[field] == value:
            return el


def id_dict(frm, list_name):
    i_dict = {}
    with open(frm, 'r', encoding='utf8') as file:
        data = json.load(file)
    for el in data[list_name]:
        i_dict[el['id']] = el

    return i_dict


def main_view(request):
    day = days_of_week[datetime.datetime.now().weekday()]
    with open('Schedule.json', 'r', encoding='utf8') as file:
        data = json.load(file)

    schedule = []
    groups = id_dict('Groups.json', 'groups')
    disciplines = id_dict('Ed_Disciplines.json', 'ed_disciplines')
    teachers = id_dict('Teachers.json', 'teachers')
    for disc in disciplines.values():
        disc['teacher'] = teachers[disc['teacher']]

    for group in data['Schedule']:
        for _day in group['days']:
            if _day['day'] == day:
                for tm in _day['times']:
                    tm['discipline'] = disciplines[tm['discipline']]

                schedule.append({'name': groups[group['group']],
                                 'info': _day})

    return render(request, 'main.html', {'groups': schedule, 'day': datetime.datetime.now()})


def group_detail(request, group_id):
    group = get('Schedule.json', 'Schedule', group_id)


def group_create(request):
    pass


def group_edit(request, group_id):
    pass


def teacher_schedule(request, teacher_id):
    pass


def admin(request):
    pass


def teacher_create(request):
    pass


def student_create(request):
    pass


def teacher_edit(request):
    pass


def student_edit(request):
    pass


def discipline_create(request):
    pass


def discipline_edit(request):
    pass


def programme_create(request):
    pass


def programme_edit(request):
    pass
