from django.db import models
from django.db import connection
from django.contrib.auth.models import User
from .constants import DAYS_OF_WEEK
from django.forms.models import model_to_dict


class Contract(models.Model):
    contract_id = models.AutoField(primary_key=True)
    contract_dttm = models.DateTimeField()
    student_document = models.ForeignKey('PersonDocument', models.DO_NOTHING, blank=True, null=True,
                                         related_name='student_document')
    student_address = models.ForeignKey('PersonHomeAddress', models.DO_NOTHING, blank=True, null=True,
                                        related_name='student_address')
    student_phone_no = models.CharField(max_length=20, blank=True, null=True)
    payer_document = models.ForeignKey('PersonDocument', models.DO_NOTHING, blank=True, null=True,
                                       related_name='payer_document')
    payer_address = models.ForeignKey('PersonHomeAddress', models.DO_NOTHING, blank=True, null=True,
                                      related_name='payer_address')
    payer_phone_no = models.CharField(max_length=20, blank=True, null=True)
    payer_inn_no = models.CharField(max_length=12)
    course_element = models.ForeignKey('CourseElement', models.DO_NOTHING, blank=True, null=True)

    def uppend_dict(self, args: dict):
        for i in ['contract_id', 'contract_dttm', 'student_document_id', 'student_address_id', 'student_phone_no',
                  'payer_document_id', 'payer_address_id', 'payer_phone_no', 'payer_inn_no', 'course_element_id']:
            if i not in args.keys():
                args[i] = getattr(self, i)

    def dict_equal(self, args: dict) -> bool:
        return False

    class Meta:
        managed = False
        db_table = 'contract'


class ContractPayment(models.Model):
    contract_payment_id = models.AutoField(primary_key=True)
    payment_dt = models.DateField()
    payment_amt = models.IntegerField()
    contract = models.ForeignKey(Contract, models.DO_NOTHING, blank=True, null=True)
    payment_type = models.SmallIntegerField()
    voucher_no = models.CharField(max_length=50, blank=True, null=True)

    def uppend_dict(self, args: dict):
        if 'contract_id' not in args.keys():
            args['contract_id'] = self.contract_id
        if 'payment_type' not in args.keys():
            args['payment_type'] = self.payment_type

    def dict_equal(self, args: dict) -> bool:
        print(model_to_dict(self).items())
        print(args)
        for i, j in model_to_dict(self).items():
            print(1)
            if i == 'contract':
                print(2)
                if args['contract_id'] != self.contract_id:
                    return False
            elif args[i] != j:
                print(2)
                print(i)
                return False
        return True

    class Meta:
        managed = False
        db_table = 'contract_payment'


class ContractTermination(models.Model):
    contract = models.ForeignKey(Contract, models.DO_NOTHING, primary_key=True)
    termination_dt = models.DateField(blank=True, null=True)
    termination_reason_txt = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contract_termination'


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    sphere_txt = models.CharField(max_length=100, blank=True, null=True)
    name_txt = models.CharField(max_length=100)
    short_nm = models.CharField(max_length=20)
    price_per_hour = models.DecimalField(max_digits=65535, decimal_places=65535)
    number_of_hours = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'course'


class CourseClass(models.Model):
    course_class_id = models.AutoField(primary_key=True)
    week_day_txt = models.CharField(max_length=1)
    start_tm = models.TimeField()
    end_tm = models.TimeField()
    course_element = models.ForeignKey('CourseElement', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course_class'


class CourseElement(models.Model):
    course_element_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, models.DO_NOTHING, blank=True, null=True)
    teacher_person = models.ForeignKey('Person', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course_element'

    @property
    def get_week_days_str(self) -> str:
        return " ".join([DAYS_OF_WEEK[int(i.week_day_txt)]
                         for i in CourseClass.objects.filter(course_element=self).order_by('week_day_txt')])


class Person(models.Model):
    person_id = models.AutoField(primary_key=True)
    person_surname_txt = models.CharField(max_length=50)
    person_name_txt = models.CharField(max_length=50)
    person_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
    birth_dt = models.DateField()

    class Meta:
        managed = False
        db_table = 'person'

    @property
    def get_surname_and_initials(self) -> str:
        res = str(self.person_surname_txt) + " " + str(self.person_name_txt)[0] + "."
        if self.person_father_name_txt is not None:
            res += " " + str(self.person_father_name_txt)[0] + "."
        return res



class PersonDocument(models.Model):
    person_document_id = models.AutoField(primary_key=True)
    document_no = models.IntegerField()
    document_series = models.CharField(max_length=10, blank=True, null=True)
    document_type_txt = models.CharField(max_length=20)
    person = models.ForeignKey(Person, models.DO_NOTHING, blank=True, null=True)
    person_surname_txt = models.CharField(max_length=50)
    person_name_txt = models.CharField(max_length=50)
    person_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
    authority_no = models.CharField(max_length=20)
    authority_txt = models.CharField(max_length=150)
    issue_dt = models.DateField()

    def uppend_dict(self, args: dict):
        if 'person_id' not in args.keys():
            args['person_id'] = self.person_id

    def dict_equal(self, args: dict) -> bool:
        for i, j in model_to_dict(self).items():
            if i == 'person':
                if args['person_id'] != self.person_id:
                    return False
            elif args[i] != j:
                return False
        return True

    class Meta:
        managed = False
        db_table = 'person_document'


class PersonHomeAddress(models.Model):
    person_home_address_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, models.DO_NOTHING, blank=True, null=True)
    region_cd = models.SmallIntegerField()
    city_txt = models.CharField(max_length=50)
    street_txt = models.CharField(max_length=50)
    house_txt = models.CharField(max_length=10)
    building_no = models.CharField(max_length=10, blank=True, null=True)
    structure_no = models.CharField(max_length=10, blank=True, null=True)
    flat_nm = models.SmallIntegerField(blank=True, null=True)

    def uppend_dict(self, args: dict):
        if 'person_id' not in args.keys():
            args['person_id'] = self.person_id

    def dict_equal(self, args: dict) -> bool:
        for i, j in model_to_dict(self).items():
            if i == 'person':
                if args['person_id'] != self.person_id:
                    return False
            elif args[i] != j:
                return False
        return True


    class Meta:
        managed = False
        db_table = 'person_home_address'


class StudentPerson(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING, primary_key=True)
    education_start_year = models.DateField(blank=True, null=True)
    school_name_txt = models.CharField(max_length=50, blank=True, null=True)
    liter = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student_person'


class AuthUserXPerson(models.Model):
    auth_user = models.ForeignKey(User, models.DO_NOTHING, primary_key=True)
    person = models.ForeignKey('Person', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_x_person'
        unique_together = (('auth_user', 'person'),)


# view models

class StudentsOverviewView(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING, primary_key=True)
    person_surname_txt = models.CharField(max_length=50)
    person_name_txt = models.CharField(max_length=50)
    person_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
    school_name_txt = models.CharField(max_length=50, blank=True, null=True)
    grade = models.SmallIntegerField()
    liter = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'students_overview_view'


# functions

class StudentsOverviewFunction(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING, primary_key=True)
    person_surname_txt = models.CharField(max_length=50)
    person_name_txt = models.CharField(max_length=50)
    person_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
    school_name_txt = models.CharField(max_length=50, blank=True, null=True)
    grade = models.SmallIntegerField()
    liter = models.CharField(max_length=1, blank=True, null=True)
    has_debt = models.BooleanField(null=True)

    @staticmethod
    def execute(surname: str = None, name: str = None, father_name: str = None, document_series: str = None,
                document_no: int = None, school: str = None, grade: int = None, liter: str = None, dept: bool = False):
        cur = connection.cursor()
        cur.callproc('students_filtered_stub', [name, surname, father_name, document_no, document_series,
                                                school, grade, liter, dept])
        columns = [column[0] for column in cur.description]
        for row in cur:
            yield StudentsOverviewFunction(**dict(zip(columns, row)))

    class Meta:
        managed = False


# class ContractOverviewByPerson(models.Model):
#     contract_id = models.IntegerField()
#     contract_dt = models.DateField()
#     person_id = models.IntegerField()
#     document_series = models.CharField(max_length=10, blank=True, null=True)
#     document_no = models.IntegerField()
#     person_surname_txt = models.CharField(max_length=50)
#     person_name_txt = models.CharField(max_length=50)
#     person_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
#     connection_type_txt = models.CharField(max_length=50)
#     course_id = models.IntegerField()
#     sphere_txt = models.CharField(max_length=100, blank=True, null=True)
#     name_txt = models.CharField(max_length=100)
#     number_of_payments = models.BigIntegerField()
#
#     @staticmethod
#     def execute(person_id: int):
#         cur = connection.cursor()
#         cur.callproc('contract_overview_by_person', [person_id])
#         columns = [column[0] for column in cur.description]
#         print(columns)
#         for row in cur:
#             yield ContractOverviewByPerson(**dict(zip(columns, row)))
#
#     class Meta:
#         managed = False
