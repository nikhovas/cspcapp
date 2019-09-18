from .models import *
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from django.db import connection
from .utilities import reconstruct_params, post_request_to_dict_slicer, values_from_dict_by_keys, smart_int, \
    null_check, reconstruct_args
import datetime
from .forms import UserForm
from django.shortcuts import redirect
from .views_kernel import add_student
from django.db.utils import IntegrityError
import sys
import os
import cspc.settings
import cspcapp.constants
from .views_kernel import superuser_only


# Configuration Block


DELETE_RENAMING = {'payment': 'contract_payment'}


# Edit Block


@superuser_only
def data_edit(request: WSGIRequest, object_type: str) -> HttpResponse:
    if object_type in RELINKS_FOR_EDIT:
        object_type = RELINKS_FOR_EDIT[object_type]
    config = MODEL_TYPES_DICT[object_type]
    params = post_request_to_dict_slicer(request.POST)
    editing_object = config.type_name.objects.get(pk=request.POST['id'])
    del params['csrfmiddlewaretoken']
    del params['id']
    reconstruct_args(params=params, to_date=config.to_date, date_to_timestamp=config.date_to_timestamp,
                     to_time=config.to_time)
    for i, j in params.items():
        rsetattr(editing_object, i, j)
    if hasattr(editing_object, 'change_user'):
        editing_object.change_user = request.user
    editing_object.save()
    return JsonResponse({})


# Add Block


@superuser_only
def course_detail_add(request: WSGIRequest) -> JsonResponse:
    # data = dict(request.POST)
    CourseElementDefiniteClass.objects.create(class_dt=datetime.date(int(request.POST['class_dt_year']),
                                                                     int(request.POST['class_dt_month']),
                                                                     int(request.POST['class_dt_day'])),
                                              start_tm=datetime.time(int(request.POST['start_tm_hour']),
                                                                     int(request.POST['start_tm_minute'])),
                                              end_tm=datetime.time(int(request.POST['end_tm_hour']),
                                                                   int(request.POST['end_tm_minute'])),
                                              course_element_id=int(request.POST['course_element_id']))
    return JsonResponse({})


# Delete BLock


@superuser_only
def object_delete(request: WSGIRequest, object_type: str) -> HttpResponse:
    id = request.POST['id']
    try:
        if object_type == 'contract':
            contract = Contract.objects.get(pk=id)
            date = request.POST['delete_date']
            if date is '':
                date = datetime.datetime.now().date()
            ContractTermination.objects.create(contract=contract, termination_dt=date,
                                               termination_reason_txt=request.POST['delete_reason'])
            contract.delete(user=request.user)
        else:
            MODEL_TYPES_DICT[object_type].type_name.objects.get(pk=id).delete(user=request.user)
    except IntegrityError:
        exc_type, value, exc_traceback = sys.exc_info()
        return JsonResponse({
            'success': False,
            'error_msg': f"Ошибка: есть зависимости, не подлежащие автоматическому удалению\n\n\n{value}"
        })
    except HasRelatedObjectsException as error:
        res = 'Ошибка: есть зависимости, не подлежащие автоматическому удалению:'
        for i in error.relations_set:
            res += f"\n{i[0].ru_localization} -> {i[1].ru_localization}"
        return JsonResponse({'success': False, 'error_msg': res})
    return JsonResponse({'success': True})


@superuser_only
def new_user(request: WSGIRequest) -> JsonResponse:
    _new_user = User.objects.create_user(username=request.POST['username'], password=request.POST['password'],
                                         first_name=request.POST['name'], last_name=request.POST['surname'])
    new_person = Person(person_surname_txt=request.POST['surname'],
                        person_name_txt=request.POST['name'],
                        person_father_name_txt=request.POST['father_name'],
                        birth_dt=datetime.date(int(request.POST['person.birth_dt__year']),
                                               int(request.POST['person.birth_dt__month']),
                                               int(request.POST['person.birth_dt__day'])))
    new_person.save()
    conn = AuthUserXPerson(auth_user=_new_user, person=new_person)
    conn.save()
    return JsonResponse({})


@superuser_only
def get_teacher_users(request: WSGIRequest) -> JsonResponse:
    return JsonResponse([{
        'surname': i.person.person_surname_txt,
        'name': i.person.person_name_txt,
        'father_name': i.person.person_father_name_txt,
        'username': i.auth_user.username,
        'id': i.person.id
    } for i in AuthUserXPerson.objects.all()])


@superuser_only
def submit_registration_form(request: WSGIRequest) -> JsonResponse:
    template = RegistrationRequest.objects.get(pk=request.POST['id'])
    _new_user = User.objects.create_user(username=template.username, password=template.password)
    _new_user.save()
    new_person = Person(person_surname_txt=template.person_surname_txt,
                        person_name_txt=template.person_name_txt,
                        person_father_name_txt=template.person_father_name_txt,
                        birth_dt=template.birth_dt, change_user=request.user)
    new_person.save()
    AuthUserXPerson.objects.create(auth_user=_new_user, person=new_person)
    return JsonResponse({})


@superuser_only
def submit_student_form(request: WSGIRequest) -> JsonResponse:
    try:
        req = StudentRequest.objects.get(pk=request.POST['id'])
        now = datetime.datetime.now().date()
        ed_year = now.year - req.student_class
        if now.month > 6:
            ed_year += 1
    except Exception:
        return JsonResponse({'result': False, 'error': 'Ошибка обработки класса'})
    try:
        add_student(request.user,
                    document_no=[req.student_document_no, req.payer_document_no],
                    document_series=[req.student_document_series, req.payer_document_series],
                    person_surname_txt=[req.student_surname_txt, req.payer_surname_txt],
                    person_name_txt=[req.student_name_txt, req.payer_name_txt],
                    person_father_name_txt=[req.student_father_name_txt, req.payer_father_name_txt],
                    authority_no=[req.student_authority_no, req.payer_authority_no],
                    authority_txt=[req.student_authority_txt, req.payer_authority_txt],
                    issue_dt=[req.student_issue_dt, req.payer_issue_dt],
                    document_type_txt=[req.student_document_type_txt, req.payer_document_type_txt],

                    region_cd=[req.student_region_cd, req.payer_region_cd],
                    area_txt=[req.student_area_txt, req.payer_area_txt],
                    city_txt=[req.student_city_txt, req.payer_city_txt],
                    street_txt=[req.student_street_txt, req.payer_street_txt],
                    house_txt=[req.student_house_txt, req.payer_house_txt],
                    building_no=[req.student_building_no, req.payer_building_no],
                    structure_no=[req.student_structure_no, req.payer_structure_no],
                    flat_nm=[req.student_flat_nm, req.payer_flat_nm],

                    birth_dt=[req.student_birth_dt],
                    education_dt=[datetime.date(ed_year, 9, 1)],
                    school_name_txt=[req.student_school_name_txt],
                    liter=[req.student_liter],

                    student_phone_no=[req.student_phone_no],
                    payer_phone_no=[req.payer_phone_no],
                    payer_inn_no=[req.payer_inn_no],

                    course_element=req.courses.split(' ')
                    )
        req.delete()
        return JsonResponse({'result': True})
    except Exception:
        return JsonResponse({'result': False, 'error': 'Ошибка обработки полей'})


def search_dates_in_json(data: dict):
    dates_keys = {}
    for i, j in data.items():
        if type(j) is not dict:
            divided = i.split('__')
            if len(divided) == 2:
                if divided[0] not in dates_keys:
                    dates_keys[divided[0]] = {divided[1]: j}
                else:
                    dates_keys[divided[0]][divided[1]] = j
        else:
            search_dates_in_json(j)
    for i, j in dates_keys.items():
        try:
            date = datetime.date(int(j['year']), int(j['month']), int(j['day']))
            del data[i + '__year']
            del data[i + '__month']
            del data[i + '__day']
            data[i] = date
        except Exception:
            pass


def generate_object(data: dict, object_elem):
    for i, j in data.items():
        if type(j) is dict:
            elem = (object_elem._meta.get_field(i).related_model)()
            generate_object(j, elem)
            data[i] = elem
        setattr(object_elem, i, data[i])
    object_elem.save()


@superuser_only
def course_element_add(request: WSGIRequest) -> JsonResponse:
    data = dict(request.POST)
    course_element = CourseElement.objects.create(course_id=request.POST['course_id'],
                                                  teacher_person_id=request.POST['teacher_id'])
    course_element.save()
    course_element_id = course_element.pk
    for k in range(0, 7):
        if data['course_class_start_hour'][k] != '' and data['course_class_start_minute'][k] != '' and \
                data['course_class_end_hour'][k] != '' and data['course_class_end_minute'][k] != '':
            CourseClass(start_tm=datetime.time(int(data['course_class_start_hour'][k]),
                                               int(data['course_class_start_minute'][k])),
                        end_tm=datetime.time(int(data['course_class_end_hour'][k]),
                                             int(data['course_class_end_minute'][k])),
                        week_day_txt=str(k), course_element_id=course_element_id).save()
    return JsonResponse({
        'html': render(request, 'models/course_element/main.html', {'object': course_element}).content.decode('utf-8')
    })


def add_object(request: WSGIRequest, object_type) -> JsonResponse:
    elem = MODEL_TYPES_DICT[object_type].type_name()
    args_dict = {}
    args = {i: j[0] for i, j in dict(request.POST).items()}
    for i, j in dict(request.POST).items():
        path = i.split('.')
        last_elem = args_dict
        for k in path[:-1]:
            if k not in last_elem:
                last_elem[k] = {}
            last_elem = last_elem[k]
        last_elem[path[-1]] = j[0]

    search_dates_in_json(args_dict)
    if object_type == 'contract':
        flat_nm = args_dict['student_address']['flat_nm']
        args_dict['student_address']['flat_nm'] = None if flat_nm is '' else int(flat_nm)
        flat_nm = args_dict['payer_address']['flat_nm']
        args_dict['payer_address']['flat_nm'] = None if flat_nm is '' else int(flat_nm)
        if args_dict['student_document']['document_type_txt'] == '':
            del args_dict['student_document']
            del args_dict['student_address']

    generate_object(args_dict, elem)

    return JsonResponse({
        'html': render(request, 'models/' + object_type +'/main.html', {'object': elem}).content.decode('utf-8')
    })


def add_course_class(request: WSGIRequest) -> JsonResponse:
    try:
        date = datetime.date(int(request.POST['class_dt_year']), int(request.POST['class_dt_month']), int(request.POST['class_dt_day']))
    except Exception:
        return JsonResponse({'result': False, 'error': 'Неправильный формат даты'})
    try:
        start_tm = datetime.time(int(request.POST['start_tm_hour']), int(request.POST['start_tm_minute']))
    except Exception:
        return JsonResponse({'result': False, 'error': 'Неправильный формат времени начала'})
    try:
        end_tm = datetime.time(int(request.POST['end_tm_hour']), int(request.POST['end_tm_minute']))
    except Exception:
        return JsonResponse({'result': False, 'error': 'Неправильный формат времени окончания'})
    try:
        ce = CourseElement.objects.get(pk=request.POST['course_element_id'])
        if ce.teacher_person.authuserxperson.auth_user != request.user:
            return JsonResponse({'result': False, 'error': 'ОШИБКА БЕЗОПАСНОСТИ: ДАННЫЙ ЭЛЕМЕНТ НЕ ПРИНАДЛЕЖИТ ВАМ'})
    except Exception:
        return JsonResponse({'result': False, 'error': 'ОШИБКА БЕЗОПАСНОСТИ: НЕ СУЩЕСТВУЮЩИЙ ЭЛЕМЕНТ'})
    # try:
    #
    # except Exception:
    #     return JsonResponse({'html': render(request, 'models/course_class/main.html', {'object': elem}).content.decode('utf-8')})
    elem = CourseElementDefiniteClass(course_element_id=request.POST['course_element_id'], class_dt=date,
                                      start_tm=start_tm, end_tm=end_tm)
    elem.save()
    return JsonResponse({
        'result': True,
        'html': render(request, 'models/course_class/main.html', {'object': elem}).content.decode('utf-8')
    })


def edit_course_class(request: WSGIRequest) -> JsonResponse:
    try:
        date = datetime.date(int(request.POST['class_dt_year']), int(request.POST['class_dt_month']), int(request.POST['class_dt_day']))
    except Exception:
        return JsonResponse({'result': False, 'error': 'Неправильный формат даты'})
    try:
        start_tm = datetime.time(int(request.POST['start_tm_hour']), int(request.POST['start_tm_minute']))
    except Exception:
        return JsonResponse({'result': False, 'error': 'Неправильный формат времени начала'})
    try:
        end_tm = datetime.time(int(request.POST['end_tm_hour']), int(request.POST['end_tm_minute']))
    except Exception:
        return JsonResponse({'result': False, 'error': 'Неправильный формат времени окончания'})
    try:
        ce = CourseElementDefiniteClass.objects.get(pk=request.POST['id'])
        if ce.course_element.teacher_person.authuserxperson.auth_user != request.user:
            return JsonResponse({'result': False, 'error': 'ОШИБКА БЕЗОПАСНОСТИ: ДАННЫЙ ЭЛЕМЕНТ НЕ ПРИНАДЛЕЖИТ ВАМ'})
        ce.class_dt = date
        ce.start_tm = start_tm
        ce.end_tm = end_tm
        ce.save()
        return JsonResponse({
            'result': True
        })
    except Exception:
        return JsonResponse({'result': False, 'error': 'ОШИБКА БЕЗОПАСНОСТИ: НЕ СУЩЕСТВУЮЩИЙ ЭЛЕМЕНТ'})


def delete_course_class(request: WSGIRequest) -> JsonResponse:
    try:
        ce = CourseElementDefiniteClass.objects.get(pk=request.POST['id'])
        if ce.course_element.teacher_person.authuserxperson.auth_user != request.user:
            return JsonResponse({'result': False, 'error': 'ОШИБКА БЕЗОПАСНОСТИ: ДАННЫЙ ЭЛЕМЕНТ НЕ ПРИНАДЛЕЖИТ ВАМ'})
        ce.delete()
        return JsonResponse({
            'result': True
        })
    except Exception:
        return JsonResponse({'result': False, 'error': 'ОШИБКА БЕЗОПАСНОСТИ: НЕ СУЩЕСТВУЮЩИЙ ЭЛЕМЕНТ'})



def get_session_data(request: WSGIRequest) -> JsonResponse:
    models_dict = {}
    parent_dir = os.path.join(os.path.join(cspc.settings.BASE_DIR, 'templates'), 'models')
    for subdir in next(os.walk(parent_dir))[1]:
        child_1_dir = os.path.join(parent_dir, subdir)
        models_dict[subdir] = {file[:-5]: open(os.path.join(child_1_dir, file), 'r').read()
                               for file in next(os.walk(child_1_dir))[2]}
    return JsonResponse({
        'models': models_dict,
        'statics': {
            'REGIONS_DICT': REGIONS_DICT,
            'PAYMENT_TYPES': cspcapp.constants.PAYMENT_TYPES,
            'DAYS_OF_WEEK': cspcapp.constants.DAYS_OF_WEEK,
            'courses': [i for i in Course.objects.values()],
            'course_elements': [i for i in CourseElement.objects.values()],
            'teachers': [i for i in AuthUserXPerson.objects.values()],
            'user': {'pk': request.user.pk, 'username': request.user.username, 'is_superuser': request.user.is_superuser}
        }
    })


@superuser_only
def change_user_password(request: WSGIRequest) -> JsonResponse:
    if request.POST:
        if 'user_id' not in request.POST:
            JsonResponse({'result': False, 'error': 'отсутствует id пользователя'})
        if 'new_password' not in request.POST or request.POST['new_password'] == '':
            JsonResponse({'result': False, 'error': 'пустой пароль'})
        u = User.objects.get(pk=request.POST['user_id'])
        u.set_password(request.POST['new_password'])
        u.save()
        return JsonResponse({'result': True})
    else:
        return JsonResponse({'result': False, 'error': 'отсутствует тело запроса'})
