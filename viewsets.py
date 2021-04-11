from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView

from api.account.serializers import UserSerializer
from api.report.paginations import ReportPagination
from api.report.serializers import (
    ReportSerializer,
    ReportImageSerializer,
    ReportHealthSerializer,
    CreateReportHealthSerializer,
    CreateReportSerializer,
    CommentSerializer,
    CreateCommentSerializer,
)
from apps.report.models import Report, ReportImage, Comment
from apps.center.models import Elder

from django.db import transaction

from apps.report.filters import ReportFilter, CommentFilter
from api.firebase_push.pushAPI import send_to_firebase_cloud_messaging


class ReportViewSet(viewsets.ModelViewSet):
    pagination_class = ReportPagination
    queryset = Report.objects.select_related('reporthealth', 'user', 'elder')\
        .prefetch_related('reportimage_set', 'comment_set', 'comment_set__user', 'read_people').all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        if 'read_people' in request.data:
            instance = self.get_object()
            instance.read_people.add(request.data['read_people'])
            return Response(data={"message": "Success Check Read"}, status=status.HTTP_200_OK)
        else:
            return self.update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if request.user.is_protector:
            queryset_by_user = queryset.filter(elder__in=request.user.protector.elders.all(), center=request.GET['center'])
        elif request.user.is_guardian:
            queryset_by_user = queryset.filter(elder__in=request.user.guardian.elders.all(), center=request.GET['center'])
        else:
            queryset_by_user = queryset.filter(center=request.GET['center'])
        page = self.paginate_queryset(queryset_by_user)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        report_ids = []
        if request.user.is_guardian:
            data = request.user.guardian.elders.get(center=request.data['center'])
            request.data['elders'] = [data.id]

        for elder in request.data['elders']:
            related_people = []
            request.data['elder'] = elder
            serializer = CreateReportSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            report = serializer.save()
            report_ids.append(report.id)
            elder = Elder.objects.select_related('guardian__user', 'center__user').prefetch_related('protectors__user').get(id=elder)
            related_people.append(elder.guardian.user)
            related_people.append(elder.center.user)
            for protector in elder.protectors.all():
                related_people.append(protector.user)
            related_people.remove(request.user)
            print(related_people)
            send_to_firebase_cloud_messaging(related_people, "글이 작성되었어요^^", request.data['content'], "notedetail", report.id)

            if 'health' in request.data and request.data['health']:
                data = request.data['health']
                data['report'] = report.id
                serializer = CreateReportHealthSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        if 'images' in request.data and request.data['images']:
            for image in request.data['images']:
                data = dict()
                data['report'] = report_ids
                data['file'] = image
                serializer = ReportImageSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        headers = self.get_success_headers(report_ids)
        return Response(report_ids, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        print("delete")
        return Response(data={"message": "성공적으로 삭제됐습니다."}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('user').all()
    serializer_classes = {
        'create': CreateCommentSerializer
    }
    default_serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CommentFilter

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        related_people = []
        elder_id = Report.objects.select_related('elder').get(id=request.data['report']).elder.id
        elder = Elder.objects.select_related('guardian__user', 'center__user').prefetch_related('protectors__user').get(
            id=elder_id)
        related_people.append(elder.guardian.user)
        related_people.append(elder.center.user)
        for protector in elder.protectors.all():
            related_people.append(protector.user)
        related_people.remove(request.user)
        send_to_firebase_cloud_messaging(related_people, "댓글이 작성되었어요^^", request.data['message'], "notedetail", request.data['report'])
        headers = self.get_success_headers(serializer.data)
        return Response(CommentSerializer(instance, context=serializer.context).data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(data={"message": "성공적으로 삭제됐습니다."}, status=status.HTTP_204_NO_CONTENT)

