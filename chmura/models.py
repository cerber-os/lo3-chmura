from django.db import models


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


class PriorityClassroom(models.Model):
    name = models.CharField(max_length=100)
    priority = models.IntegerField()


class SubstitutionType(models.Model):
    name = models.CharField(max_length=100)


class Journal(models.Model):
    date = models.DateTimeField(auto_now=True)
    level = models.CharField(max_length=15, blank=True)
    message = models.CharField(max_length=251, blank=True)
    additional_info = models.CharField(max_length=1001, blank=True)
    module = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, blank=True)
