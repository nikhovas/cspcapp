from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse
from .models import *
from django.core.handlers.wsgi import WSGIRequest
from .utilities import reformat_request_get_params, overview_get_format, smart_int, null_check
from django.contrib.auth.decorators import login_required
from .constants import REGIONS_DICT, PAYMENT_TYPES
from django.shortcuts import redirect
from .views_kernel import add_student, generate_contract_pdf, add_contract
from cspc import settings
from .api_requests import new_user
from .views_kernel import superuser_only


def students_overview(request: WSGIRequest) -> HttpResponse:
    return render(request, 'students_overview.html', {'students_list': [
        i for i in StudentsOverviewFunction.execute(
            **dict(overview_get_format(reformat_request_get_params(request.GET)))
        ) if i.person.has_contract_with_teacher(request.user.authuserxperson.person) or request.user.is_superuser
    ]})


def courses_view(request: WSGIRequest) -> HttpResponse:
    return render(request, 'courses_info_view.html', {'object_set': Course.objects.all()})


@superuser_only
def teachers_view(request: WSGIRequest) -> HttpResponse:
    if request.POST:
        new_user(request)
    return render(request, 'teachers_info_view.html', {'object_set': AuthUserXPerson.objects.all()})


@superuser_only
def versions(request: WSGIRequest, pk: int, model_name: str) -> HttpResponse:
    return render(request, 'versions/version.html', {
        'object': MODEL_TYPES_DICT[model_name].type_name.objects.get(pk=pk)
    })


def meta_base_view(request):
    return render(request, 'base.html')


@superuser_only
def student_add_function(request: WSGIRequest) -> HttpResponse:
    if request.POST:
        print(type(request.user))
        add_student(request.user, is_approved=True, **dict(request.POST))
        return redirect('/')
    else:
        return render(request, 'student_add.html', {'courses': CourseElement.objects.all()})


def account_settings(request: WSGIRequest) -> HttpResponse:
    auth_user_x_person = AuthUserXPerson.objects.filter(auth_user=request.user)[0]
    return render(request, 'account_settings.html', {
        'person': auth_user_x_person.person,
        'courses_info': [
            (j, CourseElementDefiniteClass.objects.filter(course_element=j))
            for j in CourseElement.objects.filter(teacher_person=auth_user_x_person.person)
        ]
    })


@superuser_only
def reg_request(request: WSGIRequest) -> HttpResponse:
    if request.POST['password'] != request.POST['password_repeat']:
        return JsonResponse({})
    reg_req = RegistrationRequest.objects.create(person_surname_txt=request.POST['surname'],
                                                 person_name_txt=request.POST['name'],
                                                 person_father_name_txt=request.POST['father_name'],
                                                 birth_dt=datetime.date(int(request.POST['birth_dt_year']),
                                                                        int(request.POST['birth_dt_month']),
                                                                        int(request.POST['birth_dt_day'])),
                                                 username=request.POST['username'],
                                                 password=request.POST['password'])
    return redirect('/accounts/login/')


@superuser_only
def registration_requests_list(request: WSGIRequest) -> HttpResponse:
    return render(request, 'registration_forms.html', {'forms': RegistrationRequest.objects.all()})


@superuser_only
def students_request_list(request: WSGIRequest) -> HttpResponse:
    return render(request, 'student_forms_view.html', {'forms': StudentRequest.objects.all(),
                                                       'REGIONS_DICT': REGIONS_DICT})


@superuser_only
def fetch_pdf_resources(uri, rel):
    return settings.BASE_DIR + '/cspcapp' + uri


def print_contract(request: WSGIRequest, pk: int):
    return HttpResponse(generate_contract_pdf(pk), content_type='application/pdf')


def details(request: WSGIRequest, pk: int, model_name: str) -> HttpResponse:
    if request.POST:
        if model_name == Contract._meta.db_table:
            add_contract(request.user, student=StudentPerson.objects.get(pk=pk), **dict(request.POST))
            return redirect(f"/{model_name}/detail/{pk}/")
    return render(request, 'models/main.html', {'object': MODEL_TYPES_DICT[model_name].type_name.objects.get(pk=pk)})


def queries(request: WSGIRequest, model_name: str) -> HttpResponse:
    return render(request, 'models/main.html', {'object_set': MODEL_TYPES_DICT[model_name].type_name.objects.all()})