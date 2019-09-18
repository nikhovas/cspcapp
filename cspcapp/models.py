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
from django.template.loader import get_template
from cspcapp.constants import REGIONS_DICT


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

    def __setattr__(self, item: str, value):
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



    @property
    def version_history(self):
        cur = connection.cursor()
        pk_name: str = self._meta.pk.name
        if not pk_name.endswith('_id'):
            pk_name += '_id'
        cur.execute(f"SELECT * FROM {self._meta.db_table}_log WHERE {pk_name} = {self.pk}")
        columns = [column[0] for column in cur.description]
        for row in cur:
            args = dict(zip(columns, row))
            change_timestamp = args['change_timestamp']
            del args['change_timestamp']
            obj = self.__class__(**args)
            obj.change_timestamp = change_timestamp
            yield obj

    def delete(self, using=None, keep_parents=False, user=None):
        if hasattr(self, 'VersionInfo'):
            for i, j in self.VersionInfo.check_if_deleted.items():
                setattr(self, i, j)
            self.change_user = user
            self.save()
        else:
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
                rel_class = i.related_model
                related_objects = rel_class.objects.filter(**{i.field_name: self.pk})
                if related_objects.count() is not 0:
                    connections.add((i.related_model, i.model))
                    if deep and hasattr(i.related_model, 'get_related_connections'):
                        for j in related_objects:
                            connections |= j.get_related_connections(deep=deep, ignore_options=ignore_options)
        return connections

    def simple_version_history_html_table(self):
        for i in self.__class__._meta.get_fields():
            pass

    @property
    def version_history_html_table(self) -> str:
        return get_template(f"versions/details/{self._meta.db_table}_versions.html").render({'object': self})

    @property
    def html(self) -> str:
        return get_template(f"models/{self._meta.db_table}/main.html").render({
            'object': self,
            'REGIONS_DICT': REGIONS_DICT
        })

    @property
    def html_main_url(self):
        return 'models/' + self._meta.db_table + '/main.html'

    @property
    def add_button(self):
        return get_template('buttons/add.html').render({'object': self, 'db_table': self._meta.db_table})

    @property
    def edit_button(self):
        return get_template('buttons/edit.html').render({'object': self, 'db_table': self._meta.db_table})

    @property
    def expand_button(self):
        return get_template('buttons/expand.html').render({'object': self, 'db_table': self._meta.db_table})

    @property
    def remove_button(self):
        return get_template('buttons/remove.html').render({'object': self, 'db_table': self._meta.db_table})

    @property
    def versions_button(self):
        return get_template('buttons/versions.html').render({'object': self, 'db_table': self._meta.db_table})

    @property
    def print_button(self):
        return get_template('buttons/print.html').render({'object': self, 'db_table': self._meta.db_table})

    @property
    def goto_button(self):
        return get_template('buttons/goto.html').render({'object': self, 'db_table': self._meta.db_table})

    @property
    def get_db_table(self):
        return self._meta.db_table

    @property
    def deleted(self) -> bool:
        for i, j in self.VersionInfo.check_if_deleted.items():
            if getattr(self, i) != j:
                return False
        return True

    class Meta:
        abstract = True

    def delete_connections(self) -> set:
        connections = set()
        for i in self.__class__._meta.get_fields():
            if i.auto_created and not i.concrete:
                rel_class = i.related_model
                rel_objects = rel_class.objects.filter(**{i.field_name: self.pk})
                if i.on_delete == models.CASCADE:
                    if hasattr(i.related_model, 'delete_connections'):
                        for j in rel_objects:
                            connections |= j.delete_connections()
                else:
                    if rel_objects.count() != 0:
                        connections.add((i.related_model, i.model))
        return connections

    @property
    def deep_json(self):
        result_dict = {}
        for i in self.__class__._meta.get_fields():
            try:
                if type(i) is models.OneToOneField:
                    name: str = i.name
                    if name.endswith('_id'):
                        name = name[:-3]
                    result_dict[name] = getattr(self, name).deep_json
                else:
                    val = getattr(self, i.name)
                    if type(val) is datetime.date:
                        result_dict[i.name + '_year'] = val.year
                        result_dict[i.name + '_month'] = val.month
                        result_dict[i.name + '_day'] = val.day
                    elif type(val) is datetime.time:
                        result_dict[i.name + '_hour'] = val.hour
                        result_dict[i.name + '_minute'] = val.minute
                    elif type(val) in (str, int):
                        result_dict[i.name] = val
            except Exception:
                pass
        return result_dict

    @property
    def first_version(self):
        return next(self.version_history)


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

    class VersionInfo:
        version_control_visible_fields = ('student_phone_no', 'payer_phone_no', 'payer_inn_no',)
        check_if_deleted = {'student_document': None, 'student_address': None, 'payer_document': None,
                            'payer_address': None}

    @property
    def payment_details(self):
        payed = ContractPayment.objects.filter(contract=self).aggregate(Sum('payment_amt'))['payment_amt__sum'] or 0
        full_price = self.course_element.course.total_price
        return {
            'payed_sum': payed,
            'full_price': full_price,
            'need_to_pay': full_price - payed
        }

    # def delete(self, using=None, keep_parents=False, user=None, __date=datetime.datetime.now().date, reason=''):
    #     if __date == '':
    #         __date = str(datetime.datetime.now().date())
    #     ContractTermination.objects.create(contract=self, termination_dt=__date, termination_reason_txt=reason)
    #     for i, j in self.VersionInfo.check_if_deleted.items():
    #         setattr(self, i, j)
    #     self.change_user = user
    #     self.save()


class ContractPayment(Model):
    ru_localization = 'Оплата контракта'
    contract_payment_id = models.AutoField(primary_key=True)
    payment_dt = models.DateField()
    payment_amt = models.IntegerField()
    contract = models.ForeignKey(Contract, models.CASCADE, blank=True, null=True)
    payment_type = models.SmallIntegerField()
    voucher_no = models.CharField(max_length=50, blank=True, null=True)
    change_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class VersionInfo:
        version_control_visible_fields = ('payment_dt', 'payment_amt', 'payment_type', 'voucher_no',)
        codes_dict = {'region_cd': REGIONS_DICT}
        check_if_deleted = {'payment_type': None, 'payment_amt': None}

    class Meta:
        managed = False
        db_table = 'contract_payment'


class ContractTermination(models.Model):
    ru_localization = 'Расторжение контракта'
    contract = models.OneToOneField(Contract, models.CASCADE)
    termination_dt = models.DateField(blank=True, null=True)
    termination_reason_txt = models.CharField(max_length=100, blank=True, null=True)
    course_name_txt = models.CharField(max_length=128, default='')
    contract_termination_id = models.AutoField(primary_key=True)

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
    deleted_flg = models.BooleanField(null=False, blank=False, default=False)

    class Meta:
        managed = False
        db_table = 'course'

    @property
    def total_price(self):
        if type(self.price_per_hour) is str:
            self.price_per_hour = int(self.price_per_hour)
        if type(self.number_of_hours) is str:
            self.number_of_hours = int(self.number_of_hours)
        return self.price_per_hour * self.number_of_hours

    @property
    def half_price(self):
        return self.price_per_hour * self.number_of_hours / 2

    def delete(self, using=None, keep_parents=False, user=None):
        self.deleted_flg = True
        self.save()

    @property
    def deleted(self) -> bool:
        return self.deleted_flg


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
    deleted_flg = models.BooleanField(null=False, blank=False, default=False)

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

    def delete(self, using=None, keep_parents=False, user=None):
        self.deleted_flg = True
        self.save()

    course_class = property(get_course_class, set_course_class)

    @property
    def get_course_classes(self):
        for k in range(0, 7):
            on_current_day = CourseClass.objects.filter(course_element=self).filter(week_day_txt=str(k))
            yield on_current_day[0] if len(on_current_day) != 0 else None

    @property
    def deep_json(self):
        result_dict = super().deep_json
        result_dict['get_course_classes'] = [i.deep_json if i is not None else {} for i in self.get_course_classes]
        return result_dict

    @property
    def deleted(self) -> bool:
        return self.deleted_flg


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

    class VersionInfo:
        version_control_visible_fields = ('person_surname_txt', 'person_name_txt', 'person_father_name_txt',
                                          'birth_dt',)
        codes_dict = {'region_cd': REGIONS_DICT}
        check_if_deleted = {'person_surname_txt': None, 'person_name_txt': None, 'person_father_name_txt': None}

    @property
    def get_surname_and_initials(self) -> str:
        res = str(self.person_surname_txt) + " " + str(self.person_name_txt)[0] + "."
        if self.person_father_name_txt is not None:
            res += " " + str(self.person_father_name_txt)[0] + "."
        return res

    def delete(self, using=None, keep_parents=False, user=None):
        if hasattr(self, 'studentperson'):
            self.studentperson.delete(user=user)
        if hasattr(self, 'authuserxperson'):
            self.authuserxperson.delete(user=user)
        super().delete(using, keep_parents, user=user)


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

    @property
    def version_history_html_table(self) -> str:
        return get_template('versions/details/person_document_versions.html').render({'object': self})

    class Meta:
        managed = False
        db_table = 'person_document'

    class VersionInfo:
        version_control_visible_fields = ('document_no', 'document_series', 'city_txt', 'street_txt', 'house_txt',
                                          'building_no', 'structure_no', 'flat_nm', )
        check_if_deleted = {'document_type_txt': None}


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

    @property
    def version_history_html_table(self) -> str:
        return get_template('versions/details/person_home_address_versions.html').render({'object': self,
                                                                                          'REGIONS_DICT': REGIONS_DICT})

    class Meta:
        managed = False
        db_table = 'person_home_address'

    class VersionInfo:
        version_control_visible_fields = ('region_cd', 'area_txt', 'city_txt', 'street_txt', 'house_txt',
                                          'building_no', 'structure_no', 'flat_nm', )
        codes_dict = {'region_cd': REGIONS_DICT}
        check_if_deleted = {'region_cd': None}


class StudentPerson(Model):
    ru_localization = 'Личность студента'
    also_save = ('person',)
    person = models.OneToOneField(Person, models.CASCADE, primary_key=True)
    education_start_year = models.DateField(blank=True, null=True)
    school_name_txt = models.CharField(max_length=50, blank=True, null=True)
    liter = models.CharField(max_length=1, blank=True, null=True)
    change_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'student_person'

    class VersionInfo:
        version_control_visible_fields = ('education_start_year', 'school_name_txt', 'liter',)
        check_if_deleted = {'education_start_year': None, 'school_name_txt': None, 'liter': None}

    @property
    def version_history_html_table(self) -> str:
        return get_template('versions/details/student_person_versions.html').render({'object': self})

    def has_contract_with_teacher(self, teacher_user: Person):
        return len(CourseElement.objects.filter(contract__student_person=self, teacher_person=teacher_user)) != 0


class AuthUserXPerson(Model):
    ru_localization = ''
    also_save = ('auth_user', 'person')
    auth_user_x_person_id = models.AutoField(primary_key=True)
    auth_user = models.OneToOneField(User, models.CASCADE)
    person = models.OneToOneField('Person', models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_user_x_person'


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


# profiles


class PostRequestInfo:
    def __init__(self, _type_name, _to_date: list = (), _date_to_timestamp: list = (), _to_time: list = (),
                 _additional_save: list = ()):
        self.type_name = _type_name
        self.to_date = _to_date
        self.date_to_timestamp = _date_to_timestamp
        self.to_time = _to_time
        self.additional_save = _additional_save


RELINKS_FOR_EDIT = {
    'contract_student_phone': Contract._meta.db_table,
    'contract_payer_phone': Contract._meta.db_table,
    'contract_payer_inn': Contract._meta.db_table,
    'contract_course_element': Contract._meta.db_table
}


MODEL_TYPES_DICT = {
        PersonDocument._meta.db_table: PostRequestInfo(_type_name=PersonDocument, _to_date=['issue_dt']),
        PersonHomeAddress._meta.db_table: PostRequestInfo(_type_name=PersonHomeAddress),
        Contract._meta.db_table: PostRequestInfo(_type_name=Contract),
        ContractPayment._meta.db_table: PostRequestInfo(_type_name=ContractPayment, _date_to_timestamp=['payment_dt']),
        'person': PostRequestInfo(_type_name=Person, _to_date=['education_start_year', 'birth_dt']),
        # 'contract_student_phone': PostRequestInfo(_type_name=Contract),
        'student_person': PostRequestInfo(_type_name=StudentPerson, _to_date=['education_start_year', 'person.birth_dt']),
        'course': PostRequestInfo(_type_name=Course),
        'course_element': PostRequestInfo(_type_name=CourseElement),
        'course_class': PostRequestInfo(_type_name=CourseClass),
        'auth_user_x_person': PostRequestInfo(_type_name=AuthUserXPerson, _to_date=['person.birth_dt'],),
        'course_detail': PostRequestInfo(_type_name=CourseElementDefiniteClass, _to_date=['class_dt'],
                                         _to_time=['start_tm', 'end_tm']),
        'reg_form': PostRequestInfo(_type_name=RegistrationRequest, _to_date=['birth_dt']),
        'student_request': PostRequestInfo(_type_name=StudentRequest)
}