from django.db import models

from apps.utils import FilenameChanger
from apps.constants import CommonType, TempType, MealType, SleepingType, FecesType
# Create your models here.


class Report(models.Model):
    user = models.ForeignKey('account.User', verbose_name='작성자', on_delete=models.CASCADE,)
    center = models.ForeignKey('center.Center', verbose_name='센터', on_delete=models.CASCADE,)
    elder = models.ForeignKey('center.Elder', verbose_name='어르신', on_delete=models.CASCADE)

    read_people = models.ManyToManyField('account.User', verbose_name='읽은 사람들', related_name='read')

    content = models.TextField('내용', null=True, blank=True)

    updated_at = models.DateTimeField('수정일시', auto_now=True)
    created_at = models.DateTimeField('생성일시', auto_now_add=True)

    class Meta:
        verbose_name = '     알림장'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.id} : 알림장'


class ReportHealth(models.Model):
    report = models.OneToOneField(Report, verbose_name='알림장', on_delete=models.CASCADE)
    feeling = models.PositiveIntegerField('생활기록_기분', choices=CommonType.TYPE.value, null=True, blank=True)
    health = models.PositiveIntegerField('생활기록_건강', choices=CommonType.TYPE.value, null=True, blank=True)
    temperature = models.PositiveIntegerField('생활기록_체온', choices=TempType.TYPE.value, null=True, blank=True)
    meal = models.PositiveIntegerField('생활기록_식사', choices=MealType.TYPE.value, null=True, blank=True)
    feces = models.PositiveIntegerField('배변상태', choices=FecesType.TYPE.value, null=True, blank=True)
    sleeping = models.PositiveIntegerField('수면시간', choices=SleepingType.TYPE.value, null=True, blank=True)

    updated_at = models.DateTimeField('수정일시', auto_now=True)
    created_at = models.DateTimeField('생성일시', auto_now_add=True)

    class Meta:
        verbose_name = '     알림장 건강체크'
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.report.id} : 알림장 건강체크[{self.id}]'


class ReportImage(models.Model):
    report = models.ManyToManyField(Report, verbose_name='알림장')
    file = models.ImageField('이미지', upload_to=FilenameChanger('post'))

    class Meta:
        verbose_name = '    알림장 이미지'
        verbose_name_plural = f'{verbose_name}(들)'

    def __str__(self):
        return f'알림장 이미지[{self.id}]'


class Comment(models.Model):
    user = models.ForeignKey('account.User', verbose_name='작성자', on_delete=models.CASCADE,)
    report = models.ForeignKey(Report, verbose_name='알림장', on_delete=models.CASCADE,)
    message = models.TextField('내용')

    updated_at = models.DateTimeField('수정일시', auto_now=True)
    created_at = models.DateTimeField('생성일시', auto_now_add=True)

    class Meta:
        verbose_name = '  댓글'
        verbose_name_plural = f'{verbose_name}'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.report.id} : 알림장 댓글[{self.id}]'