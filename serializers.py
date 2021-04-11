import random
import re

from apps.report.models import Report, ReportImage, Comment, ReportHealth
from apps.account.models import User
from api.account.serializers import UserSerializer
from api.center.serializers import CenterSerializer, ProtectorSerializer, GuardianSerializer, ElderSerializer

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from drf_extra_fields.fields import Base64ImageField


class ReportImageSerializer(serializers.ModelSerializer):
    file = Base64ImageField()
    report = serializers.PrimaryKeyRelatedField(queryset=Report.objects.all(), write_only=True, many=True)

    class Meta:
        model = ReportImage
        fields = (
            'id',
            'report',
            'file'
        )


class CommentSerializer(serializers.ModelSerializer):

    class CommentUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = (
                'id',
                'type',
            )
            read_only_fields = ('type',)

    user = CommentUserSerializer()
    report = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Report.objects.all())
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "message",
            "created_at",
            "user",
            'report',
            "is_mine"
        )

    def get_is_mine(self, obj):
        user = self.context['request'].user
        if obj.user == user:
            return True
        return False


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "message",
            'report',
        )


class CreateReportHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportHealth
        fields = (
            'report',
            'feeling',
            'health',
            'temperature',
            'meal',
            'feces',
            'sleeping'
        )


class ReportHealthSerializer(serializers.ModelSerializer):
    feeling = serializers.SerializerMethodField()
    health = serializers.SerializerMethodField()
    temperature = serializers.SerializerMethodField()
    meal = serializers.SerializerMethodField()
    feces = serializers.SerializerMethodField()
    sleeping = serializers.SerializerMethodField()

    class Meta:
        model = ReportHealth
        fields = (
            'feeling',
            'health',
            'temperature',
            'meal',
            'feces',
            'sleeping'
        )

    def get_feeling(self, obj):
        return obj.get_feeling_display()

    def get_health(self, obj):
        return obj.get_health_display()

    def get_temperature(self, obj):
        return obj.get_temperature_display()

    def get_meal(self, obj):
        return obj.get_meal_display()

    def get_feces(self, obj):
        return obj.get_feces_display()

    def get_sleeping(self, obj):
        return obj.get_sleeping_display()


class ReportSerializer(serializers.ModelSerializer):

    class ReportUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = (
                'id',
                'image',
                'type',
            )
            read_only_fields = ('image', 'type')

    images = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    health = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()
    read_people = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, write_only=True)
    elder = serializers.SerializerMethodField()
    user = ReportUserSerializer()

    class Meta:
        model = Report
        fields = (
            'id',
            'user',
            'center',
            'elder',
            'content',
            'created_at',
            'health',
            'images',
            'comments',
            'is_read',
            'is_mine',
            'read_people',
        )

    def get_elder(self, obj):
        return obj.elder.name

    def get_is_mine(self, obj):
        user = self.context['request'].user
        if obj.user == user:
            return True
        return False

    def get_is_read(self, obj):
        if self.context['request'].user in obj.read_people.all():
            return True
        else:
            return False

    def get_health(self, obj):
        if hasattr(obj, 'reporthealth'):
            return ReportHealthSerializer(obj.reporthealth).data
        return None

    def get_images(self, obj):
        images = obj.reportimage_set.all()
        return ReportImageSerializer(images, many=True).data

    def get_comments(self, obj):
        comments = obj.comment_set.all()
        return CommentSerializer(comments, context=self.context, many=True).data


class CreateReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = (
            'user',
            'center',
            'elder',
            'content',
        )