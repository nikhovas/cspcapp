from django.db import models
from django.db import connection
from django.contrib.auth.models import User
from .constants import DAYS_OF_WEEK
from django.forms.models import model_to_dict
from .utilities import rsetattr, rgetattr
from django.db.models.fields.related import OneToOneField as O2of
import datetime
from django.db.models import Sum
from django.core.exceptions import FieldError


class HasRelatedObjectsException(Exception):
    def __init__(self, relations_set: set):
        self.relations_set = relations_set


class Model(models.Model):
    ru_localization = ''

    def save(self, *args, **kwargs):
        if hasattr(self, 'also_save'):
            for i in self.also_save:
                getattr(self, i).save()
        if not hasattr(self, 'is_edited') or getattr(self, 'is_edited'):
            self.__dict__['is_edited'] = False
            super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.__dict__['is_edited'] = True
        super().__init__(*args, **kwargs)

    def __setattr__(self, item, value):
        if item is not 'change_user':
            was_edited = hasattr(self, 'is_edited') and getattr(self, 'is_edited')
            try:
                self.__dict__[item] = value
                if item != 'change_user' and item != 'change_user_id':
                    self.__dict__['is_edited'] = True
            except Exception:
                self.__dict__['is_edited'] = was_edited
                raise
        super().__setattr__(item, value)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, user=None):
        try:
            not_deleted = self.delete_connections()
            if len(not_deleted) is not 0:
                raise HasRelatedObjectsException(not_deleted)
        except FieldError:
            pass
        super().delete(using, keep_parents)

    def get_related_connections(self, deep=False, ignore_options=()) -> set:
        connections = set()
        for i in self.__class__._meta.get_fields():
            if i.auto_created and not i.concrete:
                print(i.on_delete not in ignore_options)
                rel_class = i.related_model
                related_objects = rel_class.objects.filter(**{i.field_name: self.pk})
                if related_objects.count() is not 0:
                    connections.add((i.related_model, i.model))
                    if deep and hasattr(i.related_model, 'get_related_connections'):
                        for j in related_objects:
                            connections |= j.get_related_connections(deep=deep, ignore_options=ignore_options)
        return connections

    def delete_connections(self) -> set:
        connections = set()
        for i in self.__class__._meta.get_fields():
            if i.auto_created and not i.concrete:
                rel_class = i.related_model
                print(i.__dict__)
                rel_objects = rel_class.objects.filter(**{i.field_name: self.pk})
                if i.on_delete == models.CASCADE:
                    if hasattr(i.related_model, 'delete_connections'):
                        for j in rel_objects:
                            connections |= j.delete_connections()
                else:
                    if rel_objects.count() != 0:
                        connections.add((i.related_model, i.model))
        return connections


class Contract(Model):
    ru_localization = 'Контракт'
    contract_id = models.AutoField(primary_key=True)
    student_person = models.ForeignKey('StudentPerson', blank=True, on_delete=models.CASCADE)
    student_document = models.OneToOneField('PersonDocument', models.DO_NOTHING, blank=True, null=True,
                                            related_name='student_document')
    student_address = models.OneToOneField('PersonHomeAddress', models.DO_NOTHING, blank=True, null=True,
                                           related_name='student_address')
    student_phone_no = models.CharField(max_length=20, blank=True, null=True)
    payer_document = models.OneToOneField('PersonDocument', models.DO_NOTHING, blank=True, null=True,
                                          related_name='payer_document')
    payer_address = models.OneToOneField('PersonHomeAddress', models.DO_NOTHING, blank=True, null=True,
                                         related_name='payer_address')
    payer_phone_no = models.CharField(max_length=20, blank=True, null=True)
    payer_inn_no = models.CharField(max_length=12)
    course_element = models.ForeignKey('CourseElement', models.DO_NOTHING, blank=True, null=True)
    change_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'contract'

    @property
    def payment_details(self):
        payed = ContractPayment.objects.filter(contract=self).aggregate(Sum('payment_amt'))['payment_amt__sum'] or 0
        full_price = self.course_element.course.total_price
        return {
            'payed_sum': payed,
            'full_price': full_price,
            'need_to_pay': full_price - payed
        }


class ContractPayment(Model):
    ru_localization = 'Оплата контракта'
    contract_payment_id = models.AutoField(primary_key=True)
    payment_dt = models.DateField()
    payment_amt = models.IntegerField()
    contract = models.ForeignKey(Contract, models.CASCADE, blank=True, null=True)
    payment_type = models.SmallIntegerField()
    voucher_no = models.CharField(max_length=50, blank=True, null=True)
    change_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'contract_payment'


class ContractTermination(Model):
    ru_localization = 'Расторжение контракта'
    contract = models.OneToOneField(Contract, models.CASCADE, primary_key=True)
    termination_dt = models.DateField(blank=True, null=True)
    termination_reason_txt = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contract_termination'


class Course(Model):
    ru_localization = 'Курс'
    course_id = models.AutoField(primary_key=True)
    sphere_txt = models.CharField(max_length=100, blank=True, null=True)
    name_txt = models.CharField(max_length=100)
    short_nm = models.CharField(max_length=20)
    price_per_hour = models.IntegerField()
    number_of_hours = models.IntegerField()
    number_of_month = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'course'

    @property
    def total_price(self):
        return self.price_per_hour * self.number_of_hours

    @property
    def half_price(self):
        return self.price_per_hour * self.number_of_hours / 2


class CourseClass(Model):
    ru_localization = 'Элемент в расписании курса'
    course_class_id = models.AutoField(primary_key=True)
    week_day_txt = models.CharField(max_length=1)
    start_tm = models.TimeField()
    end_tm = models.TimeField()
    course_element = models.ForeignKey('CourseElement', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course_class'


class CourseElement(Model):
    ru_localization = 'Элемент курса'
    course_element_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, models.CASCADE, blank=True, null=True)
    teacher_person = models.ForeignKey('Person', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course_element'

    @property
    def get_week_days_str(self) -> str:
        return " ".join([DAYS_OF_WEEK[int(i.week_day_txt)]
                         for i in CourseClass.objects.filter(course_element=self).order_by('week_day_txt')])

    def custom_delete(self, user_id: int):
        CourseClass.objects.filter(course_element=self).delete()
        super(CourseElement, self).custom_delete(user_id)

    def get_course_class(self):
        return None

    def set_course_class(self, value):
        if getattr(self, 'classElems', None) is None:
            self.classElems = CourseClass.objects.filter(course_element=self)
        course_class_objects = CourseClass.objects.filter(course_element=self)
        for k in range(0, 7):
            on_current_day = course_class_objects.filter(week_day_txt=str(k))

            if value[4 * k] == '' or value[4 * k + 1] == '' or value[4 * k + 2] == '' or value[4 * k + 3] == '':
                if len(on_current_day) != 0:
                    on_current_day.delete()
            else:
                srt_tm_h = int(value[4 * k + 0])
                srt_tm_m = int(value[4 * k + 1])
                end_tm_h = int(value[4 * k + 2])
                end_tm_m = int(value[4 * k + 3])
                start_tm = datetime.time(srt_tm_h, srt_tm_m)
                end_tm = datetime.time(end_tm_h, end_tm_m)
                if len(on_current_day) == 0:
                    new_element = CourseClass(start_tm=start_tm, end_tm=end_tm, week_day_txt=str(k),
                                              course_element=self)
                    new_element.save()
                else:
                    on_current_day[0].start_tm = start_tm
                    on_current_day[0].end_tm = end_tm
                    on_current_day[0].save()

    course_class = property(get_course_class, set_course_class)


class Person(Model):
    ru_localization = 'Личность'
    person_id = models.AutoField(primary_key=True)
    person_surname_txt = models.CharField(max_length=50)
    person_name_txt = models.CharField(max_length=50)
    person_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
    birth_dt = models.DateField()
    change_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'person'

    @property
    def get_surname_and_initials(self) -> str:
        res = str(self.person_surname_txt) + " " + str(self.person_name_txt)[0] + "."
        if self.person_father_name_txt is not None:
            res += " " + str(self.person_father_name_txt)[0] + "."
        return res

    # @property
    # def student_person_cast(self):
    #     return StudentPerson.objects.get(pk=self.pk)


class PersonDocument(Model):
    ru_localization = 'Документ'
    person_document_id = models.AutoField(primary_key=True)
    document_no = models.IntegerField()
    document_series = models.CharField(max_length=10, blank=True, null=True)
    document_type_txt = models.CharField(max_length=20)
    person_surname_txt = models.CharField(max_length=50)
    person_name_txt = models.CharField(max_length=50)
    person_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
    authority_no = models.CharField(max_length=20)
    authority_txt = models.CharField(max_length=150)
    issue_dt = models.DateField()
    change_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'person_document'


class PersonHomeAddress(Model):
    ru_localization = 'Адрес'
    person_home_address_id = models.AutoField(primary_key=True)
    region_cd = models.SmallIntegerField()
    area_txt = models.CharField(max_length=50)
    city_txt = models.CharField(max_length=50)
    street_txt = models.CharField(max_length=50)
    house_txt = models.CharField(max_length=10)
    building_no = models.CharField(max_length=10, blank=True, null=True)
    structure_no = models.CharField(max_length=10, blank=True, null=True)
    flat_nm = models.SmallIntegerField(blank=True, null=True)
    change_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'person_home_address'


class StudentPerson(Model):
    ru_localization = 'Личность студента'
    person = models.OneToOneField(Person, models.CASCADE, primary_key=True)
    education_start_year = models.DateField(blank=True, null=True)
    school_name_txt = models.CharField(max_length=50, blank=True, null=True)
    liter = models.CharField(max_length=1, blank=True, null=True)
    change_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'student_person'


class AuthUserXPerson(Model):
    ru_localization = ''
    also_save = ('auth_user', 'person')
    auth_user_x_person_id = models.AutoField(primary_key=True)
    auth_user = models.OneToOneField(User, models.CASCADE)
    person = models.OneToOneField('Person', models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_user_x_person'


    # def save(self, *args, **kwargs):
    #     self.auth_user.save()
    #     self.person.save()
    #     super().save(*args, **kwargs)


class CourseElementDefiniteClass(Model):
    ru_localization = 'Отчет о занятии курса'
    course_element_definite_class_id = models.AutoField(primary_key=True)
    course_element = models.ForeignKey('CourseElement', models.CASCADE, blank=True)
    class_dt = models.DateField()
    start_tm = models.TimeField()
    end_tm = models.TimeField()

    class Meta:
        managed = False
        db_table = 'course_element_definite_class'


class RegistrationRequest(Model):
    ru_localization = 'ЗАпрос на регистрацию'
    registration_request_id = models.AutoField(primary_key=True)
    person_surname_txt = models.CharField(max_length=50)
    person_name_txt = models.CharField(max_length=50)
    person_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
    birth_dt = models.DateField()
    username = models.CharField(max_length=50, blank=True, unique=True)
    password = models.CharField(max_length=50, blank=True)

    class Meta:
        managed = False
        db_table = 'registration_request'


class StudentRequest(Model):
    ru_localization = 'Запрос от ученика'
    student_request_id = models.AutoField(primary_key=True)
    is_two_side = models.BooleanField(blank=True, null=True)
    student_surname_txt = models.CharField(max_length=50, blank=True, null=True)
    student_name_txt = models.CharField(max_length=50, blank=True, null=True)
    student_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
    student_birth_dt = models.DateField(blank=True, null=True)
    student_class = models.IntegerField(blank=True, null=True)
    student_school_name_txt = models.CharField(max_length=50, blank=True, null=True)
    student_liter = models.CharField(max_length=1, blank=True, null=True)
    student_phone_no = models.CharField(max_length=20, blank=True, null=True)
    student_document_no = models.IntegerField(blank=True, null=True)
    student_document_series = models.CharField(max_length=10, blank=True, null=True)
    student_document_type_txt = models.CharField(max_length=20, blank=True, null=True)
    student_authority_no = models.CharField(max_length=20, blank=True, null=True)
    student_authority_txt = models.CharField(max_length=150, blank=True, null=True)
    student_issue_dt = models.DateField(blank=True, null=True)
    student_region_cd = models.IntegerField(blank=True, null=True)
    student_city_txt = models.CharField(max_length=50, blank=True, null=True)
    student_street_txt = models.CharField(max_length=50, blank=True, null=True)
    student_house_txt = models.CharField(max_length=10, blank=True, null=True)
    student_building_no = models.CharField(max_length=10, blank=True, null=True)
    student_structure_no = models.CharField(max_length=10, blank=True, null=True)
    student_flat_nm = models.IntegerField(blank=True, null=True)
    payer_surname_txt = models.CharField(max_length=50)
    payer_name_txt = models.CharField(max_length=50)
    payer_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
    payer_phone_no = models.CharField(max_length=20, blank=True, null=True)
    payer_inn_no = models.CharField(max_length=12)
    payer_document_no = models.IntegerField()
    payer_document_series = models.CharField(max_length=10, blank=True, null=True)
    payer_document_type_txt = models.CharField(max_length=20)
    payer_authority_no = models.CharField(max_length=20)
    payer_authority_txt = models.CharField(max_length=150)
    payer_issue_dt = models.DateField()
    payer_region_cd = models.IntegerField()
    payer_city_txt = models.CharField(max_length=50)
    payer_street_txt = models.CharField(max_length=50)
    payer_house_txt = models.CharField(max_length=10)
    payer_building_no = models.CharField(max_length=10, blank=True, null=True)
    payer_structure_no = models.CharField(max_length=10, blank=True, null=True)
    payer_flat_nm = models.IntegerField(blank=True, null=True)
    courses = models.CharField(max_length=1024, blank=True, null=True)
    student_area_txt = models.CharField(max_length=50, blank=True, null=True)
    payer_area_txt = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student_request'

    @property
    def get_course_elements(self):
        for i in self.courses.split(' '):
            yield CourseElement.objects.get(pk=int(i))


# view models

class StudentsOverviewView(Model):
    person = models.OneToOneField(Person, models.DO_NOTHING, primary_key=True)
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

class StudentsOverviewFunction(Model):
    person = models.OneToOneField(StudentPerson, models.DO_NOTHING, primary_key=True)
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

    @property
    def contracts(self):
        return Contract.objects.filter(student_person=self.person)

    class Meta:
        managed = False
