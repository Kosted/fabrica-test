from rest_framework import mixins, permissions, status, viewsets, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Prefetch
from fabrica_test_task.utils import get_user_by_token
from interview.models import Interview, CompleteInterview, Question, Answer
from interview.permissions import IsAuthorized
from interview.serializers import InterviewSerializer, CompleteInterviewSerializer, DoneInterviewSerializer


class InterviewViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthorized]
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer

    def get_serializer_class(self, complete_interview=None):
        if complete_interview:
            return CompleteInterviewSerializer
        return InterviewSerializer

    def retrieve(self, request, *args, **kwargs):
        user = get_user_by_token(request)

        if CompleteInterview.objects.filter(user=user, interview__id=kwargs.get('pk')).exists():
            serializer = self.get_serializer_class(True)
            pf_queryset = Question.objects.filter().prefetch_related("answervariant_set", Prefetch('answer_set', queryset=Answer.objects.filter(user=user)))

        else:
            serializer = self.get_serializer_class()
            pf_queryset = Question.objects.filter().prefetch_related("answervariant_set")

        pf = Prefetch("question_set", queryset=pf_queryset)
        instance = Interview.objects.prefetch_related(pf).get(pk=kwargs.get('pk'))

        res = serializer(instance=instance)
        return Response(res.data)

    @action(detail=False, methods=['get'])
    def active_interviews(self, requests, *args, **kwargs):
        db_active_interviews = Interview.objects.filter(active=True)
        interviews = [interview for interview in db_active_interviews if interview.update_active()]
        serializer = self.get_serializer(interviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def complete_interviews(self, requests, *args, **kwargs):
        user = get_user_by_token(requests)

        serializer = self.get_serializer_class(True)
        pf_queryset = Question.objects.filter().prefetch_related("answervariant_set", Prefetch('answer_set', queryset=Answer.objects.filter(user=user)))

        pf = Prefetch("question_set", queryset=pf_queryset)
        instance = Interview.objects.prefetch_related(pf).filter(completeinterview__user=user)

        res = serializer(instance=instance, many=True)
        return Response(res.data)

    @action(detail=False, methods=['post'])
    def done(self, requests, *args, **kwargs):
        user = get_user_by_token(requests)

        serializer = DoneInterviewSerializer
        data = requests.data
        data['user'] = user.id
        res = serializer(data=data)
        if res.is_valid(raise_exception=True):
            res = res.save()

            return Response(CompleteInterviewSerializer(instance=res.interview).data)
