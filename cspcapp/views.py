from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.core.handlers.wsgi import WSGIRequest
from .utilities import reformat_request_get_params, overview_get_format
from django.contrib.auth.decorators import login_required
from .constants import REGIONS_DICT, PAYMENT_TYPES
from django.forms.models import model_to_dict


@login_required
def students_overview(request: WSGIRequest) -> HttpResponse:
    request_get = dict(overview_get_format(reformat_request_get_params(request.GET)))
    query = StudentsOverviewFunction.execute(**request_get)
    get_request_preview = {i: j for i, j in request_get.items() if j is not None}
    return render(request, 'students_overview.html', {'students_list': query, 'request_get': get_request_preview})


@login_required
def student_detail_view(request: WSGIRequest, pk: int) -> HttpResponse:
    student_person = StudentPerson.objects.filter(pk=pk)[0]
    contracts = []
    documents_set = set()
    addresses_set = set()
    courses = []

    for contract in Contract.objects.filter(student_document__person=pk):
        documents_set.add(contract.student_document)
        documents_set.add(contract.payer_document)
        addresses_set.add(contract.student_address)
        addresses_set.add(contract.payer_address)
        contracts.append((contract, ContractPayment.objects.filter(contract=contract).order_by('payment_dt')))

    info = {'student_person': student_person,
            'person': student_person.person,
            'contracts': contracts,
            'regions': REGIONS_DICT,
            'payment_types': PAYMENT_TYPES,
            'documents_set': documents_set,
            'addresses_set': addresses_set,
            'courses': [(course, CourseElement.objects.filter(course=course)) for course in Course.objects.all()]
            }
    return render(request, 'student_detail_view.html', info)


@login_required
def courses_view(request: WSGIRequest) -> HttpResponse:
    courses_info = [(i, CourseElement.objects.filter(course=i)) for i in Course.objects.all()]
    return render(request, 'courses_info_view.html', {'courses_info': courses_info})


@login_required
def teachers_view(request: WSGIRequest) -> HttpResponse:
    courses_info = [(i, CourseElement.objects.filter(course=i)) for i in Course.objects.all()]
    return render(request, 'teachers_info_view.html', {})


def meta_base_view(request):
    return render(request, 'base.html')
