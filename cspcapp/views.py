from django.shortcuts import render
from .models import *
from django.core.handlers.wsgi import WSGIRequest
from django.db import connections
import sqlite3
from . import sql_raws


def students_overview(request: WSGIRequest):
    return render(request, 'students_overview.html', {'students_list': StudentsOverviewView.objects.all()})


def student_detail_view(request: WSGIRequest, pk: int):
    student_person = StudentPerson.objects.filter(pk=pk)[0]
    student_info = {'student_person': student_person,
                    'person': student_person.person,
                    'contracts': Contract.objects.filter(student_document__person=pk),
                    }



    return render(request, 'student_detail_view.html', student_info)


def meta_base_view(request):
    return render(request, 'base.html')
