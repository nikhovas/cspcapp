from django.db import models
from django.db import connection
from django.contrib.auth.models import User
from .constants import DAYS_OF_WEEK
from django.forms.models import model_to_dict
from .utilities import rsetattr, rgetattr
import datetime


class VersionControlEditModel(models.Model):
    function_call_args = []
    is_edited = False

    def save(self, *args, **kwargs):
        print('heeeeere')
        if not self.pk:
            self.create_save(self, *args, **kwargs)
        else:
            print('wtf??')
            self.update_save(self, *args, **kwargs)

    def create_save(self, *args, **kwargs):
        return 0

    def update_save(self, *args, **kwargs):
        print('i am here')
        if self.is_edited:
            print('here')
            args = [j for (i, j) in model_to_dict(self).items()]
            args.append(int(kwargs['user_id']))
            connection.cursor().callproc(self._meta.db_table + '_update', args)
            self.is_edited = False

    def custom_delete(self, user_id: int):
        connection.cursor().execute(f"CALL {self._meta.db_table}_delete({self.pk}, {user_id})")

    class Meta:
        abstract = True


class NotVersionControlledEditModel(models.Model):
    def save(self, *args, **kwargs):
        if 'user_id' in kwargs:
            del kwargs['user_id']
        super(NotVersionControlledEditModel, self).save(*args, **kwargs)

    def custom_delete(self, user_id: int):
        super(NotVersionControlledEditModel, self).delete()

    class Meta:
        abstract = True


class Contract(VersionControlEditModel):
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

    class Meta:
        managed = False
        db_table = 'contract'


class ContractPayment(VersionControlEditModel):
    contract_payment_id = models.AutoField(primary_key=True)
    payment_dt = models.DateField()
    payment_amt = models.IntegerField()
    contract = models.ForeignKey(Contract, models.DO_NOTHING, blank=True, null=True)
    payment_type = models.SmallIntegerField()
    voucher_no = models.CharField(max_length=50, blank=True, null=True)

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


class Course(NotVersionControlledEditModel):
    course_id = models.AutoField(primary_key=True)
    sphere_txt = models.CharField(max_length=100, blank=True, null=True)
    name_txt = models.CharField(max_length=100)
    short_nm = models.CharField(max_length=20)
    price_per_hour = models.DecimalField(max_digits=65535, decimal_places=65535)
    number_of_hours = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'course'

    def save(self, *args, **kwargs):
        cur = connection.cursor()
        if not self.pk:
            cur.execute(f"insert into course(sphere_txt, name_txt, short_nm, price_per_hour, number_of_hours) "
                        f"VALUES  ('{self.sphere_txt}', '{self.name_txt}', '{self.short_nm}', "
                        f"{self.price_per_hour}, {self.number_of_hours});")
        else:
            cur.execute(f"update course "
                        f"set sphere_txt = '{self.sphere_txt}', name_txt = '{self.name_txt}', "
                        f"short_nm = '{self.short_nm}', price_per_hour = {self.price_per_hour}, "
                        f"number_of_hours = {self.number_of_hours} where course_id = {self.course_id}")

    def custom_delete(self, user_id: int):
        course_elements = CourseElement.objects.filter(course=self)
        CourseClass.objects.filter(course_element__in=course_elements).delete()
        course_elements.delete()
        super(Course, self).custom_delete(user_id)

    @property
    def total_price(self):
        return self.price_per_hour * self.number_of_hours


class CourseClass(models.Model):
    course_class_id = models.AutoField(primary_key=True)
    week_day_txt = models.CharField(max_length=1)
    start_tm = models.TimeField()
    end_tm = models.TimeField()
    course_element = models.ForeignKey('CourseElement', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course_class'


class CourseElement(NotVersionControlledEditModel):
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


class Person(VersionControlEditModel):
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

    def create_save(self, *args, **kwargs):
        cur = connection.cursor()
        cur.callproc('person_insert', (self.person_surname_txt, self.person_name_txt, self.person_father_name_txt,
                                       self.birth_dt, kwargs['user_id']))
        new_id = None
        for line in cur:
            new_id = line[0]
        self.person_id = new_id


class PersonDocument(VersionControlEditModel):
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

    class Meta:
        managed = False
        db_table = 'person_document'


class PersonHomeAddress(VersionControlEditModel):
    person_home_address_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, models.DO_NOTHING, blank=True, null=True)
    region_cd = models.SmallIntegerField()
    city_txt = models.CharField(max_length=50)
    street_txt = models.CharField(max_length=50)
    house_txt = models.CharField(max_length=10)
    building_no = models.CharField(max_length=10, blank=True, null=True)
    structure_no = models.CharField(max_length=10, blank=True, null=True)
    flat_nm = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'person_home_address'


class StudentPerson(VersionControlEditModel):
    person = models.ForeignKey(Person, models.DO_NOTHING, primary_key=True)
    education_start_year = models.DateField(blank=True, null=True)
    school_name_txt = models.CharField(max_length=50, blank=True, null=True)
    liter = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student_person'

    def update_save(self, *args, **kwargs):
        if self.is_edited:
            connection.cursor().callproc('person_update', [self.person_id, self.person.person_surname_txt,
                                                           self.person.person_name_txt,
                                                           self.person.person_father_name_txt,
                                                           self.person.birth_dt, self.education_start_year,
                                                           self.school_name_txt, self.liter, int(kwargs['user_id'])])
            self.is_edited = False


class AuthUserXPerson(NotVersionControlledEditModel):
    auth_user = models.ForeignKey(User, models.DO_NOTHING)
    person = models.ForeignKey('Person', models.DO_NOTHING, primary_key=True)

    class Meta:
        managed = False
        db_table = 'auth_user_x_person'
        unique_together = (('auth_user', 'person'),)

    def save(self, *args, **kwargs):
        if not self.pk:
            super(AuthUserXPerson, self).save(*args, **kwargs)
        else:
            print('here!!!')
            print(self.person.birth_dt)
            self.person.save(*args, **kwargs)
            del kwargs['user_id']
            self.auth_user.save(*args, **kwargs)

    def custom_delete(self, user_id: int):
        self.auth_user.delete()
        self.person.custom_delete(user_id)


class CourseElementDefiniteClass(NotVersionControlledEditModel):
    course_element_definite_class_id = models.AutoField(primary_key=True)
    course_element = models.ForeignKey('CourseElement', models.DO_NOTHING, blank=True)
    class_dt = models.DateField()
    start_tm = models.TimeField()
    end_tm = models.TimeField()

    class Meta:
        managed = False
        db_table = 'course_element_definite_class'


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
