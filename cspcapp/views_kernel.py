from .models import Person, PersonHomeAddress, PersonDocument, StudentPerson, Contract, StudentRequest, CourseElement
import datetime
from .utilities import reformat_request_get_params, overview_get_format, smart_int, null_check, http_basic_auth
from django.db import connection
from cspc import settings
from django.template.loader import get_template, render_to_string
from django.template import Context
from io import StringIO, BytesIO
from .constants import REGIONS_DICT, PAYMENT_TYPES
from xhtml2pdf import pisa


def add_student(user_id: int, **data):

    person = Person(person_surname_txt=data['person_surname_txt'][0],
                    person_name_txt=data['person_name_txt'][0],
                    person_father_name_txt=data['person_father_name_txt'][0]
                    if data['person_father_name_txt'][0] != '' else None,
                    birth_dt=data['birth_dt'][0] if 'birth_dt' in data else
                    datetime.date(int(data['birth_year'][0]), int(data['birth_month'][0]), int(data['birth_day'][0])))
    person.save(user_id=user_id)

    student = StudentPerson(education_start_year=data['education_dt'][0] if 'education_dt' in data else
                            datetime.date(int(data['education_year'][0]), int(data['education_month'][0]),
                                          int(data['education_day'][0])),
                            school_name_txt=data['school_name_txt'][0],
                            liter=data['liter'][0], person=person)
    student.create_save(user_id=user_id)

    if 'course_element' in data:
        for i in data['course_element']:
            print('aaaaaaaaaa111a')

            if data['document_type_txt'][0] and data['document_type_txt'][0] != '':
                arg_list = \
                    [
                        person.pk, user_id,

                        int(data['document_no'][0]), str(data['document_series'][0]), str(data['document_type_txt'][0]),
                        data['person_surname_txt'][0], data['person_name_txt'][0],
                        data['person_father_name_txt'][0], data['authority_no'][0], data['authority_txt'][0],
                        data['issue_dt'][0] if 'issue_dt' in data else
                        datetime.date(int(data['issue_year'][0]), int(data['issue_month'][0]),
                                      int(data['issue_day'][0])),

                        int(data['region_cd'][0]), data['city_txt'][0], data['street_txt'][0], data['house_txt'][0],
                        null_check(data['building_no'][0]), null_check(data['structure_no'][0]),
                        smart_int(data['flat_nm'][0]),

                        int(data['document_no'][1]), data['document_series'][1], data['document_type_txt'][1],
                        data['person_surname_txt'][1], data['person_name_txt'][1],
                        data['person_father_name_txt'][1], data['authority_no'][1], data['authority_txt'][1],
                        data['issue_dt'][1] if 'issue_dt' in data else
                        datetime.date(int(data['issue_year'][1]), int(data['issue_month'][1]),
                                      int(data['issue_day'][1])),

                        int(data['region_cd'][1]), data['city_txt'][1], data['street_txt'][1], data['house_txt'][1],
                        null_check(data['building_no'][1]), null_check(data['structure_no'][1]),
                        smart_int(data['flat_nm'][1]),

                        data['phone'][0], data['phone'][1], data['inn'][0], int(i)
                    ]

                cur = connection.cursor().callproc('full_contract_insert', arg_list)
            else:
                print('14 lower')
                arg_list = \
                    [
                        person.pk, user_id,

                        data['person_surname_txt'][0], data['person_name_txt'][0],
                        data['person_father_name_txt'][0],

                        int(data['document_no'][1]), data['document_series'][1], data['document_type_txt'][1],
                        data['person_surname_txt'][1], data['person_name_txt'][1],
                        data['person_father_name_txt'][1], data['authority_no'][1], data['authority_txt'][1],
                        data['issue_dt'][1] if 'issue_dt' in data else
                        datetime.date(int(data['issue_year'][1]), int(data['issue_month'][1]),
                                      int(data['issue_day'][1])),

                        int(data['region_cd'][1]), data['city_txt'][1], data['street_txt'][1], data['house_txt'][1],
                        null_check(data['building_no'][1]), null_check(data['structure_no'][1]),
                        smart_int(data['flat_nm'][1]),

                        data['phone'][1], data['inn'][0], int(i)
                    ]

                cur = connection.cursor().callproc('full_contract_insert_lower_14', arg_list)


def fetch_pdf_resources(uri, rel):
    return settings.BASE_DIR + '/cspcapp' + uri


def generate_contract_pdf(pk: int):
    result = BytesIO()
    template = get_template('docs/contract_paper.html')
    html = template.render({'contract': Contract.objects.get(pk=pk), 'REGIONS_DICT': REGIONS_DICT})
    print(settings.PROJECT_ROOT)
    pdf = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=result, encoding='UTF-8',
                         link_callback=fetch_pdf_resources)
    if not pdf.err:
        return result.getvalue()
    else:
        return None


def generate_contract_pdf_unchecked(student_req: StudentRequest):
    for i in student_req.courses.split(' '):
        elem = CourseElement.objects.get(pk=int(i))
        result = BytesIO()
        template = get_template('docs/contract_paper_unchecked.html')
        html = template.render({'data': student_req, 'REGIONS_DICT': REGIONS_DICT, 'course_element': elem})
        print(settings.PROJECT_ROOT)
        pdf = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=result, encoding='UTF-8',
                             link_callback=fetch_pdf_resources)
        yield result.getvalue()
