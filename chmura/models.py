from django.db import models


class Settings(models.Model):
    gpid = models.CharField(max_length=10, default='7729755')
    gsh = models.CharField(max_length=10, default='c1b41215')
    phpsessid = models.CharField(max_length=50,
                                 default='deb4ph6ahmglbssqqqfclrrlj5')
    timetableVersion = models.CharField(max_length=20, default='154')


class Subject(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=10)


class Alias(models.Model):
    selector = models.CharField(max_length=20)
    orig = models.CharField(max_length=200)
    alias = models.CharField(max_length=200)


class PriorityClass(models.Model):
    name = models.CharField(max_length=100)
    is_priority = models.BooleanField()


class SubstitutionType(models.Model):
    name = models.CharField(max_length=100)
