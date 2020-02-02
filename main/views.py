from django.shortcuts import render, redirect
from django import forms
from django.urls import reverse
import time
import json
import os
import datetime
import uuid


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
        json.dump(data, file, ensure_ascii=False)

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
    #day = days_of_week[datetime.datetime.now().weekday()]
    day = 'вторник'
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
    group = get('Groups.json', 'groups', group_id)
    schedule = get('Schedule.json', 'Schedule', group_id, 'group')
    disciplines = id_dict('ED_Disciplines.json', 'ed_disciplines')
    teachers = id_dict('Teachers.json', 'teachers')
    for discipline in disciplines:
        disciplines[discipline]['teacher'] = teachers[disciplines[discipline]['teacher']]
    for day in schedule['days']:
        for tm in day['times']:
            tm['discipline'] = disciplines[tm['discipline']]
    schedule['group'] = group

    return render(request, 'group_detail.html', {'schedule': schedule})


def programme_finder():
    programmes = id_dict('Ed_Programm.json', 'ed_programmes')
    choices = []
    for pr in programmes:
        choices.append((pr, programmes[pr]['title']))
    return choices


class GroupForm(forms.Form):

    number = forms.CharField(label='Номер')
    ed_programme = forms.TypedChoiceField(choices=programme_finder, coerce=int)


def group_create(request):

    if request.method == 'GET':
        form = GroupForm()
        return render(request, 'group_create.html', {'form': form})

    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            new_group = form.cleaned_data
            new_group['id'] = uuid.uuid4().int
            new_group['students'] = []
            add('Groups.json', 'groups', new_group)
            return redirect(reverse('main'))
        else:
            return render(request, 'group_create.html', {'form': form})


def group_edit(request, group_id):
    group = get('Groups.json', 'groups', group_id)

    if request.method == 'GET':
        form = GroupForm(group)
        return render(request, 'group_edit.html', {'form': form})

    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group.update(form.cleaned_data)
            edit('Groups.json', 'groups', group)
            return redirect(reverse('main'))
        else:
            return render(request, 'group_edit.html', {'form': form})


def teacher_schedule(request, teacher_id):
    teacher = get('Teachers.json', 'teachers', teacher_id)
    schedules = id_dict('Schedule.json', 'Schedule')
    groups = id_dict('Groups.json', 'groups')
    disciplines = id_dict('Ed_Disciplines.json', 'ed_disciplines')

    schd = {}
    for schedule in schedules.values():
        for day in schedule['days']:
            for tm in day['times']:
                if disciplines[tm['discipline']]['teacher'] == teacher_id:
                    tm['discipline'] = disciplines[tm['discipline']]
                    if day['day'] in schd:
                        schd[day['day']].append(tm)
                    else:
                        schd[day['day']] = [tm]

    return render(request, 'teacher.html', {'schedule': schd, 'teacher': teacher})


def admin(request):
    pass


statuses = (
    ('Assistant', 'Assistant'),
    ('Associate Professor', 'Associate Professor'),
)


class TeacherForm(forms.Form):

    full_name = forms.CharField()
    status = forms.ChoiceField(choices=statuses)


def teacher_create(request):
    if request.method == 'GET':
        form = TeacherForm()
        return render(request, 'teacher_create.html', {'form': form})

    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            new_teacher = form.cleaned_data
            new_teacher['id'] = uuid.uuid4().int
            add('Teachers.json', 'teachers', new_teacher)
            return redirect(reverse('main'))
        else:
            return render(request, 'teacher_create.html', {'form': form})


def group_finder():
    groups = id_dict('Groups.json', 'groups')
    choices = []
    for gr in groups:
        choices.append((gr, groups[gr]['number']))
    return choices


class StudentForm(forms.Form):

    full_name = forms.CharField()
    group = forms.TypedChoiceField(choices=group_finder, coerce=int)


def student_create(request):
    if request.method == 'GET':
        form = StudentForm()
        return render(request, 'student_create.html', {'form': form})

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            new_student = form.cleaned_data
            _id = uuid.uuid4().int
            new_student['id'] = _id
            group = get('Groups.json', 'groups', new_student['group'])
            group['students'].append(_id)
            edit('Groups.json', 'groups', group)
            add('Teachers.json', 'teachers', new_student)
            return redirect(reverse('main'))
        else:
            return render(request, 'teacher_create.html', {'form': form})


def teacher_edit(request, teacher_id):
    teacher = get('Teachers.json', 'teachers', teacher_id)

    if request.method == 'GET':
        form = TeacherForm(teacher)
        return render(request, 'teacher_edit.html', {'form': form})

    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            teacher.update(form.cleaned_data)
            edit('Teachers.json', 'teachers', teacher)
            return redirect(reverse('main'))
        else:
            return render(request, 'group_edit.html', {'form': form})


def student_edit(request, student_id):
    student = get('Student.json', 'students', student_id)

    if request.method == 'GET':
        form = StudentForm(student)
        return render(request, 'student_edit.html', {'form': form})

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student.update(form.cleaned_data)
            edit('Student.json', 'students', student)
            return redirect(reverse('main'))
        else:
            return render(request, 'student_edit.html', {'form': form})


work_types = (
    ('Practical work', 'Practical work'),
    ('Labolatory work', 'Labolatory work'),
    ('Lecture', 'Lecture')
)


def teacher_finder():
    teachers = id_dict('Teachers.json', 'teachers')

    choices = []
    for t, d in teachers.items():
        choices.append((t, d['full_name']))

    return choices


class DisciplineForm(forms.Form):
    title = forms.CharField()
    type_of_work = forms.ChoiceField(choices=work_types)
    teacher = forms.TypedChoiceField(choices=teacher_finder, coerce=int)
    ed_programme = forms.TypedChoiceField(choices=programme_finder, coerce=int)
    term = forms.ChoiceField(choices=((x, x) for x in range(1, 8)))


def discipline_create(request):
    if request.method == 'GET':
        form = DisciplineForm()
        return render(request, 'discipline_create.html', {'form': form})

    if request.method == 'POST':
        form = DisciplineForm(request.POST)
        if form.is_valid():
            new_discipline = form.cleaned_data
            _id = uuid.uuid4().int
            new_discipline['id'] = _id
            programme = get('Ed_Programm', 'ed_programmes', new_discipline['ed_programme'])
            programme['ed_disciplines'].append(_id)
            edit('Ed_Programm', 'ed_programmes', programme)
            add('Ed_Disciplines.json', 'ed_disciplines', new_discipline)
            return redirect(reverse('main'))
        else:
            return render(request, 'discipline_create.html', {'form': form})


def discipline_edit(request, discipline_id):
    discipline = get('Ed_Disciplines.json', 'ed_disciplines', discipline_id)

    if request.method == 'GET':
        form = DisciplineForm(discipline)
        return render(request, 'discipline_edit.html', {'form': form})

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            discipline.update(form.cleaned_data)
            edit('Ed_Disciplines.json', 'ed_disciplines', discipline)
            return redirect(reverse('main'))
        else:
            return render(request, 'discipline_edit.html', {'form': form})


class ProgrammeForm(forms.Form):
    title = forms.CharField()
    description = forms.CharField(widget=forms.TextInput)
    unique_code = forms.CharField()


def programme_create(request):
    if request.method == 'GET':
        form = ProgrammeForm()
        return render(request, 'programme_create.html', {'form': form})

    if request.method == 'POST':
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            new_programme = form.cleaned_data
            new_programme['id'] = uuid.uuid4().int
            new_programme['ed_discipline'] = []
            add('ED_Programm.json', 'ed_programmes', new_programme)
            return redirect(reverse('main'))
        else:
            return render(request, 'programme_create.html', {'form': form})


def programme_edit(request, programme_id):
    programme = get('Ed_Programm.json', 'students', programme_id)

    if request.method == 'GET':
        form = ProgrammeForm()
        return render(request, 'programme_edit.html', {'form': form})

    if request.method == 'POST':
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            programme.update(form.cleaned_data)
            edit('Ed_Programm.json', 'ed_programmes', programme)
            return redirect(reverse('main'))
        else:
            return render(request, 'programme_edit.html', {'form': form})
