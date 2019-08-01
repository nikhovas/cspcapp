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
    courses_info = []
    for i in Course.objects.all():
        print(i.price_per_hour)
        course_elements = []
        for j in CourseElement.objects.filter(course=i):
            filtered_classes = []
            for k in range(0, 7):
                on_current_day = CourseClass.objects.filter(course_element=j).filter(week_day_txt=str(k))
                if len(on_current_day) == 0:
                    filtered_classes.append(None)
                else:
                    filtered_classes.append(on_current_day[0])
            course_elements.append((j, filtered_classes))

        courses_info.append((i, course_elements))
    # courses_info = [(i, CourseElement.objects.filter(course=i)) for i in Course.objects.all()]
    teachers_list = AuthUserXPerson.objects.all()
    return render(request, 'courses_info_view.html', {'courses_info': courses_info, 'teachers_list': teachers_list})


@login_required
def teachers_view(request: WSGIRequest) -> HttpResponse:
    teachers_info = [(i, CourseElement.objects.filter(course=i)) for i in Course.objects.all()]
    # Тут нужно изменить на учителей
    return render(request, 'teachers_info_view.html', {'teachers': AuthUserXPerson.objects.all()})


@login_required
def versions(request: WSGIRequest, pk: int) -> HttpResponse:
    cursor = connection.cursor()
    # common_info = cursor.execute(f"select * from ")
    return render(request, 'contracts_versions.html', {})


def meta_base_view(request):
    return render(request, 'base.html')

