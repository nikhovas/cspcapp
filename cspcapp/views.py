from django.shortcuts import render
from .models import *
from django.core.handlers.wsgi import WSGIRequest
from django.db import connections
import sqlite3
from . import sql_raws
from .utilities import reformat_request_get_params, overview_get_format


def students_overview(request: WSGIRequest):
    request_get = overview_get_format(dict(reformat_request_get_params(request.GET)))
    # arr = dict(request_get)
    # print(arr)
    try:
        query = StudentsOverviewFunction.execute(**dict(request_get))
    except:
        query = StudentsOverviewView.objects.all()

    # query = StudentsOverviewFunction.execute(**arr)

    return render(request, 'students_overview.html', {'students_list': query})


def student_detail_view(request: WSGIRequest, pk: int):
    student_person = StudentPerson.objects.filter(pk=pk)[0]
    student_info = {'student_person': student_person,
                    'person': student_person.person,
                    'contracts': Contract.objects.filter(student_document__person=pk),
                    }

    return render(request, 'student_detail_view.html', student_info)


def meta_base_view(request):
    return render(request, 'base.html')
