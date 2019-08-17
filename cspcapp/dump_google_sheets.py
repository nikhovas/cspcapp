from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from .constants import REGIONS_DICT

from .models import *
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.core.mail import send_mail, EmailMessage

from .utilities import reconstruct_params, post_request_to_dict_slicer, values_from_dict_by_keys, smart_int, \
    null_check, reconstruct_args

from .views_kernel import generate_contract_pdf, generate_contract_pdf_unchecked, add_student

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1Sweq_eZ03PXz6LwbhIWRzLN51G-ooEXa8CYP0KeHbSg'
SPREADSHEET_ID = '1Sweq_eZ03PXz6LwbhIWRzLN51G-ooEXa8CYP0KeHbSg'
SAMPLE_RANGE_NAME = 'data'


def open_spreadsheet():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('sheets', 'v4', credentials=creds)


def submit_student_form(request: WSGIRequest) -> JsonResponse:
    req = StudentRequest.objects.get(pk=request.POST['id'])
    now = datetime.datetime.now().date()
    ed_year = now.year - req.student_class
    if now.month > 6:
        ed_year += 1
    add_student(request.user.pk,
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

                phone=[req.student_phone_no, req.payer_phone_no],
                inn=[req.payer_inn_no],

                course_element=req.courses.split(' ')
                )
    req.delete()
    return JsonResponse({})


def dump_to_local_database(reuqest: WSGIRequest) -> HttpResponse:
    service = open_spreadsheet()
    range = 'student_14_elder_form_answers!A2:BD1102'

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range).execute()
    values = result.get('values', [])

    for row in values:
        if len(row) == 0:
            continue
        try:
            row[42]
        except IndexError:
            row.append('')
        try:
            row[43]
        except IndexError:
            row.append('')
        courses_vals = ' '.join([i.split(' ')[0] for i in ''.join(row[38]).split(', ')])
        new_elem = StudentRequest(
            is_two_side=True, student_surname_txt=row[1], student_name_txt=row[2], student_father_name_txt=row[3],
            student_birth_dt=datetime.datetime.strptime(row[4], '%d.%m.%Y').date(), student_class=row[5],
            student_school_name_txt=row[6], student_liter=row[7], student_phone_no=row[20], student_document_no=row[9],
            student_document_series=null_check(row[8]), student_document_type_txt=row[39], student_authority_no=row[11],
            student_authority_txt=row[10], student_issue_dt=datetime.datetime.strptime(row[12], '%d.%m.%Y').date(),
            student_region_cd=int(str(row[13]).split(' ')[0]), student_area_txt=row[42], student_city_txt=row[14],
            student_street_txt=row[15],
            student_house_txt=row[16], student_building_no=null_check(row[17]),
            student_structure_no=null_check(row[18]), student_flat_nm=smart_int(row[19]),
            payer_surname_txt=row[21], payer_name_txt=row[22], payer_father_name_txt=row[23], payer_inn_no=row[36],
            payer_phone_no=row[37], payer_document_no=row[25], payer_document_series=null_check(row[24]),
            payer_document_type_txt=row[40], payer_authority_no=row[27], payer_authority_txt=row[26],
            payer_issue_dt=datetime.datetime.strptime(row[28], '%d.%m.%Y').date(),
            payer_region_cd=int(str(row[29]).split(' ')[0]), payer_area_txt=row[43], payer_city_txt=row[30],
            payer_street_txt=row[31],
            payer_house_txt=row[32], payer_building_no=null_check(row[33]), payer_structure_no=null_check(row[34]),
            payer_flat_nm=smart_int(row[35]),
            courses=courses_vals
        )
        new_elem.save()
        email = EmailMessage('Договора платных курсов', 'Письмо прислано автоматически, не отвечайте на него',
                             'cspcapp@gmail.com', [row[41]])
        email.content_subtype = 'html'
        new_num = 1
        for i in generate_contract_pdf_unchecked(new_elem):
            email.attach(f"contract_{new_num}.pdf", i, 'application/pdf')
            new_num += 1
        email.send()

    sheet.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range).execute()

    range = 'student_14_lower_form_answers!A2:AC1102'

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range).execute()
    values = result.get('values', [])

    for row in values:
        if len(row) == 0:
            continue
        courses_vals = ' '.join([i.split(' ')[0] for i in ''.join(row[26]).split(', ')])
        try:
            row[28]
        except IndexError:
            row.append('')
        new_elem = StudentRequest(
            is_two_side=False, student_surname_txt=row[1], student_name_txt=row[2], student_father_name_txt=row[3],
            student_birth_dt=datetime.datetime.strptime(row[4], '%d.%m.%Y').date(), student_class=row[5],
            student_school_name_txt=row[6], student_liter=row[7],
            payer_surname_txt=row[8], payer_name_txt=row[9], payer_father_name_txt=row[10], payer_inn_no=row[24],
            payer_phone_no=row[25], payer_document_no=row[13], payer_document_series=null_check(row[12]),
            payer_document_type_txt=row[14], payer_authority_no=row[15], payer_authority_txt=row[16],
            payer_issue_dt=datetime.datetime.strptime(row[16], '%d.%m.%Y').date(),
            payer_region_cd=int(str(row[17]).split(' ')[0]), payer_area_txt=row[28], payer_city_txt=row[18],
            payer_street_txt=row[19],
            payer_house_txt=row[20], payer_building_no=null_check(row[21]), payer_structure_no=null_check(row[22]),
            payer_flat_nm=smart_int(row[23]),
            courses=courses_vals
        )
        new_elem.save()

        email = EmailMessage('Договора платных курсов', 'Письмо прислано автоматически, не отвечайте на него',
                             'cspcapp@gmail.com', [row[27]])
        email.content_subtype = 'html'
        new_num = 1
        for i in generate_contract_pdf_unchecked(new_elem):
            email.attach(f"contract_{new_num}.pdf", i, 'application/pdf')
            new_num += 1
        email.send()

    sheet.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range).execute()

    return HttpResponse()


def update_form_info(reuqest: WSGIRequest) -> HttpResponse:
    service = open_spreadsheet()

    values = [[str(i) + " " + j] for i, j in REGIONS_DICT.items()]
    body = {'values': values}
    service.spreadsheets().values().clear(spreadsheetId=SPREADSHEET_ID, range='regions_list!A2:A100').execute()
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='regions_list!A2:A100',
        valueInputOption='RAW',
        body=body).execute()

    service = open_spreadsheet()

    values = [[
        f"{i.pk} {i.course.sphere_txt} {i.course.name_txt} {i.course.short_nm} - {i.teacher_person.person_surname_txt} "
        f"{i.teacher_person.person_name_txt} {i.teacher_person.person_father_name_txt or ''} {i.get_week_days_str}"]
        for i in CourseElement.objects.all()
    ]
    body = {'values': values}
    service.spreadsheets().values().clear(spreadsheetId=SPREADSHEET_ID, range='course_list!A2:A100').execute()
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='course_list!A2:A100',
        valueInputOption='RAW',
        body=body).execute()

    return HttpResponse()
