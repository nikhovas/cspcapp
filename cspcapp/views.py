from django.shortcuts import render
from .models import *
from django.core.handlers.wsgi import WSGIRequest
from .utilities import reformat_request_get_params, overview_get_format


def students_overview(request: WSGIRequest):
    request_get = dict(overview_get_format(reformat_request_get_params(request.GET)))
    query = StudentsOverviewFunction.execute(**request_get)
    get_request_preview = {i: j for i, j in request_get.items() if j is not None}
    return render(request, 'students_overview.html', {'students_list': query, 'request_get': get_request_preview})


def student_detail_view(request: WSGIRequest, pk: int):
    student_person = StudentPerson.objects.filter(pk=pk)[0]
    student_info = {'student_person': student_person,
                    'person': student_person.person,
                    'contracts': Contract.objects.filter(student_document__person=pk),
                    }

    return render(request, 'student_detail_view.html', student_info)


def meta_base_view(request):
    return render(request, 'base.html')
