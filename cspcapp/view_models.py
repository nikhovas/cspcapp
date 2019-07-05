# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Contract(models.Model):
    contract_id = models.AutoField(primary_key=True)
    contract_dt = models.DateField()
    student_person_document = models.ForeignKey('PersonDocument', models.DO_NOTHING,
                                                related_name='student_person_document')
    student_person_home_address = models.ForeignKey('PersonHomeAddress', models.DO_NOTHING,
                                                    related_name='student_person_home_address')
    payer_person_document = models.ForeignKey('PersonDocument', models.DO_NOTHING, blank=True, null=True,
                                              related_name='payer_person_document')
    payer_person_home_address = models.ForeignKey('PersonHomeAddress', models.DO_NOTHING, blank=True, null=True,
                                                  related_name='payer_person_home_address')
    course_element = models.ForeignKey('CourseElement', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contract'


class ContractPayment(models.Model):
    contract_payment_id = models.AutoField(primary_key=True)
    payment_dt = models.DateField()
    payment_amt = models.IntegerField()
    contract = models.ForeignKey(Contract, models.DO_NOTHING, blank=True, null=True)
    contract_payment_type = models.CharField(max_length=1)
    contract_payment_cash_voucher_no = models.CharField(max_length=20, blank=True, null=True)

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
    direction = models.CharField(max_length=1, blank=True, null=True)
    name_txt = models.CharField(max_length=100)
    price_per_hour = models.DecimalField(max_digits=65535, decimal_places=65535)
    number_of_hours = models.SmallIntegerField()
    course_start_dt = models.DateField()
    course_end_dt = models.DateField()

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


class Person(models.Model):
    person_id = models.AutoField(primary_key=True)
    birth_dt = models.DateField()
    inn_no = models.CharField(unique=True, max_length=12)

    class Meta:
        managed = False
        db_table = 'person'


class PersonDocument(models.Model):
    person_document_id = models.AutoField(primary_key=True)
    document_no = models.IntegerField()
    document_series = models.CharField(max_length=10, blank=True, null=True)
    document_type_txt = models.CharField(max_length=20)
    person = models.ForeignKey(Person, models.DO_NOTHING, blank=True, null=True)
    person_surname_txt = models.CharField(max_length=50)
    person_name_txt = models.CharField(max_length=50)
    person_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
    authority_no = models.CharField(max_length=20, blank=True, null=True)
    valid_from_dt = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'person_document'


class PersonDocumentArchived(models.Model):
    person_document_id = models.AutoField(primary_key=True)
    document_no = models.IntegerField()
    document_series = models.CharField(max_length=10, blank=True, null=True)
    document_type_txt = models.CharField(max_length=20)
    person = models.ForeignKey(Person, models.DO_NOTHING, blank=True, null=True)
    person_surname_txt = models.CharField(max_length=50)
    person_name_txt = models.CharField(max_length=50)
    person_father_name_txt = models.CharField(max_length=50)
    authority_no = models.CharField(max_length=20, blank=True, null=True)
    valid_from_dttm = models.DateTimeField()
    valid_to_dttm = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'person_document_archived'


class PersonEmail(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING, blank=True, null=True)
    email_txt = models.CharField(max_length=100)
    valid_from_dttm = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'person_email'


class PersonHomeAddress(models.Model):
    person_home_address_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, models.DO_NOTHING, blank=True, null=True)
    region_cd = models.SmallIntegerField()
    city_txt = models.CharField(max_length=50)
    street_txt = models.CharField(max_length=50)
    house_txt = models.CharField(max_length=10)
    flat_nm = models.SmallIntegerField(blank=True, null=True)
    valid_from_dttm = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'person_home_address'


class PersonHomeAddressArchived(models.Model):
    person_home_address_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, models.DO_NOTHING, blank=True, null=True)
    region_cd = models.SmallIntegerField()
    city_txt = models.CharField(max_length=50)
    street_txt = models.CharField(max_length=50)
    house_txt = models.CharField(max_length=10)
    flat_nm = models.SmallIntegerField(blank=True, null=True)
    valid_from_dttm = models.DateTimeField()
    valid_to_dttm = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'person_home_address_archived'


class PersonPhone(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING, blank=True, null=True)
    phone_no = models.CharField(max_length=20)
    valid_from_dttm = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'person_phone'


class PersonXPerson(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING, primary_key=True, related_name='person')
    x_person = models.ForeignKey(Person, models.DO_NOTHING, related_name='x_person')
    connection_type_txt = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'person_x_person'
        unique_together = (('person', 'x_person'),)


# view models