from django.shortcuts import render
from .models import *
from django.db import connections
import sqlite3
from . import sql_raws


def students_overview(request):
    return render(request, 'students_overview.html', {'students_list': StudentsOverviewView.objects.all()})


def student_detail_view(request, pk):
    # template_variables = {'person': Person.objects.filter(pk=pk)[0],
    #                       'documents': PersonDocument.objects.filter(person_id=pk),
    #                       'addresses': PersonHomeAddress.objects.filter(person_id=pk),
    #                       'connected_persons': PersonXPerson.objects.filter(person_id=pk),
    #                       'school_info': StudentSchoolInfo.objects.filter(person_id=pk).order_by('education_start'),
    #                       'contracts': ContractOverviewByPerson.execute(pk)}
    #                       # 'phones': PersonPhone.objects.filter(person_id=pk),
    #                       # 'emails': PersonEmail.objects.filter(person_id=pk)}

    template_variables = {'person': Person.objects.filter(pk=pk)[0],
                          'documents': PersonDocument.objects.filter(person_id=pk),
                          'addresses': PersonHomeAddress.objects.filter(person_id=pk),
                          'connected_persons': PersonXPerson.objects.filter(person_id=pk),
                          'school_info': StudentSchoolInfo.objects.filter(person_id=pk).order_by('education_start')}

    return render(request, 'student_detail_view.html', template_variables)


def meta_base_view(request):
    return render(request, 'base.html')
