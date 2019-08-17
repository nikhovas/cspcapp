from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import *
from django.core.handlers.wsgi import WSGIRequest
from .utilities import reformat_request_get_params, overview_get_format, smart_int, null_check
from django.contrib.auth.decorators import login_required
from .constants import REGIONS_DICT, PAYMENT_TYPES
from django.shortcuts import redirect
from .views_kernel import add_student, generate_contract_pdf, add_contract
from cspc import settings
from .api_requests import new_user


def students_overview(request: WSGIRequest) -> HttpResponse:
    return render(request, 'students_overview.html', {'students_list': StudentsOverviewFunction.execute(
        **dict(overview_get_format(reformat_request_get_params(request.GET))))})


def student_detail_view(request: WSGIRequest, pk: int) -> HttpResponse:
    if request.POST:
        # data = dict(request.POST)
        print(request.POST['course_element'])
        add_contract(request.user, student=StudentPerson.objects.get(pk=pk), **dict(request.POST))
        # print(data)
        # arg_list = \
        #     [
        #         int(data['student_id'][0]), request.user.pk,
        #
        #         int(data['document_no'][0]), str(data['document_series'][0]), str(data['document_type_txt'][0]),
        #         data['person_surname_txt'][0], data['person_name_txt'][0],
        #         data['person_father_name_txt'][0], data['authority_no'][0], data['authority_txt'][0],
        #         datetime.date(int(data['issue_dt_year'][0]), int(data['issue_dt_month'][0]),
        #                       int(data['issue_dt_day'][0])),
        #
        #         int(data['region_cd'][0]), data['city_txt'][0], data['street_txt'][0], data['house_txt'][0],
        #         null_check(data['building_no'][0]), null_check(data['structure_no'][0]), smart_int(data['flat_nm'][0]),
        #
        #         int(data['document_no'][1]), data['document_series'][1], data['document_type_txt'][1],
        #         data['person_surname_txt'][1], data['person_name_txt'][1],
        #         data['person_father_name_txt'][1], data['authority_no'][1], data['authority_txt'][1],
        #         datetime.date(int(data['issue_dt_year'][1]), int(data['issue_dt_month'][1]),
        #                       int(data['issue_dt_day'][1])),
        #
        #         int(data['region_cd'][1]), data['city_txt'][1], data['street_txt'][1], data['house_txt'][1],
        #         null_check(data['building_no'][1]), null_check(data['structure_no'][1]), smart_int(data['flat_nm'][1]),
        #
        #         data['student_phone_no'][0], data['payer_phone_no'][0], data['payer_inn_no'][0],
        #         int(data['course_element_id'][0])
        #     ]
        # cur = connection.cursor()
        # try:
        #     cur.callproc('full_contract_insert', arg_list)
        # except Exception as err:
        #     print(err)
        return redirect(f"/student/detail/{pk}/")
    student_person = StudentPerson.objects.filter(pk=pk)[0]

    info = {'student_person': student_person,
            'person': student_person.person,
            'regions': REGIONS_DICT,
            'payment_types': PAYMENT_TYPES,
            'courses': [(course, CourseElement.objects.filter(course=course)) for course in Course.objects.all()],
            'contracts': Contract.objects.filter(student_person=student_person)
            }
    return render(request, 'student_detail_view.html', info)


def courses_view(request: WSGIRequest) -> HttpResponse:
    if request.POST:
        Course(sphere_txt=request.POST['sphere_txt'], name_txt=request.POST['name_txt'],
               short_nm=request.POST['short_nm'], price_per_hour=int(request.POST['price_per_hour']),
               number_of_hours=int(request.POST['number_of_hours']),
               number_of_month=int(request.POST['number_of_month'])).save()
        return redirect('/courses/')
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


def teachers_view(request: WSGIRequest) -> HttpResponse:
    if request.POST:
        new_user(request)
    return render(request, 'teachers_info_view.html', {'teachers': [
        (i, [
            (j, CourseElementDefiniteClass.objects.filter(course_element=j))
            for j in CourseElement.objects.filter(teacher_person=i.person)
        ]) for i in AuthUserXPerson.objects.all()]})


def versions(request: WSGIRequest, pk: int, model_name: str) -> HttpResponse:
    return render(request, 'versions/version.html', {
        'object': MODEL_TYPES_DICT[model_name].type_name.objects.get(pk=pk)
    })


def meta_base_view(request):
    return render(request, 'base.html')


def contract_version(request: WSGIRequest, pk: int) -> HttpResponse:
    return render(request, 'versions/version.html', {'object': Contract.objects.get(pk=pk)})


def person_version(request: WSGIRequest, pk: int) -> HttpResponse:
    print('+++')
    print(Person.objects.get(pk=pk).simple_version_history_html_table())
    print('+++')
    return render(request, 'versions/person_version.html', {'person': Person.objects.get(pk=pk)})


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


def registration_requests_list(request: WSGIRequest) -> HttpResponse:
    return render(request, 'registration_forms.html', {'forms': RegistrationRequest.objects.all()})


def students_request_list(request: WSGIRequest) -> HttpResponse:
    return render(request, 'student_forms_view.html', {'forms': StudentRequest.objects.all(),
                                                       'REGIONS_DICT': REGIONS_DICT})


def fetch_pdf_resources(uri, rel):
    return settings.BASE_DIR + '/cspcapp' + uri


def print_contract(request: WSGIRequest, pk: int):
    return HttpResponse(generate_contract_pdf(pk), content_type='application/pdf')
