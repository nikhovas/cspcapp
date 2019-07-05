from typing import List


student_overview_raw = '''
select s.person_id, cs.name,
case
  when strftime('%m','now') < 7
    then strftime('%Y','now') - s.education_start_year - 1
  else strftime('%Y','now') - s.education_start_year
end grade, ssi.class_liter,
surname_txt, name_txt, father_name_txt, ppd.passport_no
from cspcapp_person cp
inner join cspcapp_personaddressdata pad on cp.id = pad.person_id
inner join cspcapp_personpassportdata ppd on cp.id = ppd.person_id
inner join cspcapp_studentschoolinfo ssi on cp.id = ssi.student_id
inner join cspcapp_school cs on ssi.school_id = cs.id
inner join cspcapp_student s on cp.id = s.person_id;
'''


def student_connected_persons_list(student: int):
    return '''
    select cs.id as id, connected.id as person_id, connection
    from cspcapp_person student
    inner join cspcapp_studentconnectedperson cs on student.id = cs.connected_person_id
    inner join cspcapp_person connected on cs.connected_person_id = connected.id
    where cs.id = {};
    '''.format(student)


# def persons_by_id(ids: List[int]):
#     _str = '('
#     for i in ids:
#         _str += str(i) + ', '
#     return '''
#     select birth_date, inn_no, phone_no, email_txt
#     from cspcapp_person
#     where id in {};
#     '''.format(_str + ');')
#
#
# def person_documents_by_ids(ids: List[int]):
#     _str = '('
#     for i in ids:
#         _str += str(i) + ', '
#     return '''
#     select passport_no, surname_txt, name_txt, father_name_txt, passport_issue_authority_no, passport_issue_date
#     from cspcapp_personpassportdata
#     where person_id in {}};
#     '''.format(_str + ');')
#
#
# def person_addresses_by_ids(ids: List[int]):
#     _str = '('
#     for i in ids:
#         _str += str(i) + ', '
#     return '''
#     select city, street, house_no, building_no, flat_no
#     from cspcapp_personaddressdata
#     where person_id in {});
#     '''.format(_str + ');')


def persons_by_id(ids: List[int]):
    _str = '('
    for i in ids:
        _str += str(i) + ', '
    return '''
    select birth_date, inn_no, phone_no, email_txt
    from cspcapp_person
    where id in {};
    '''.format('(' + ','.join(str(id) for id in ids) + ')')


def person_documents_by_ids(ids: List[int]):
    _str = '('
    for i in ids:
        _str += str(i) + ', '
    return '''
    select passport_no, surname_txt, name_txt, father_name_txt, passport_issue_authority_no, passport_issue_date
    from cspcapp_personpassportdata
    where person_id in {};
    '''.format('(' + ','.join(str(id) for id in ids) + ')')


def person_addresses_by_ids(ids: List[int]):
    _str = '('
    for i in ids:
        _str += str(i) + ', '
    return '''
    select city, street, house_no, building_no, flat_no
    from cspcapp_personaddressdata
    where person_id in {};
    '''.format('(' + ','.join(str(id) for id in ids) + ')')


def get_person_school_info(person_id: int):
    return '''
    select statement_date, class_liter, name
    from cspcapp_studentschoolinfo
    inner join cspcapp_school cs on cspcapp_studentschoolinfo.school_id = cs.id
    where student_id = {};
    '''.format(person_id)


def get_contracts_by_student(person_id: int):
    return '''
    select ct.id, sphere, name, connection, count(cp.id), agreement_dt, count(cc.contract_id)
    from cspcapp_contract ct
    inner join cspcapp_course cs on cs.id = ct.course_id
    left join cspcapp_contractpayment cp on ct.id = cp.contract_id
    inner join cspcapp_studentconnectedperson scp on ct.student_id = scp.student_id and ct.payer_id = scp.connected_person_id
    left join cspcapp_contracttermination cc on ct.id = cc.contract_id
    where ct.student_id = {}
    group by ct.id, sphere, name, connection, agreement_dt;
    '''.format(person_id)
