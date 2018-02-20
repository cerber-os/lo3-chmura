from django.db import models


class Settings(models.Model):
    gpid = models.CharField(max_length=10, default='7745755')
    gsh = models.CharField(max_length=10, default='c1b73915')
    phpsessid = models.CharField(max_length=50,
                                 default='deb4ph6ahmglb36qqqfclrrlj5')


class Subject(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=10)
