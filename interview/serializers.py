from django.db import transaction, DatabaseError
from django.db.models import Prefetch
from rest_framework import serializers
from fabrica_test_task.utils import pop_user_answer, check_empty, check_correct_variant
from interview.models import Interview, Answer, Question, AnswerVariant, CompleteInterview
from users.models import AnonUser


class AnswerVariantSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnswerVariant
        fields = ['id', "text"]


class AnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    answer_variants = AnswerVariantSerializer(source='answervariant_set', many=True, required=False)

    class Meta:
        model = Question
        fields = ["id", "answer_variants", "text", "type", ]


class QuestionSerializerWithAnswer(QuestionSerializer):
    answers = AnswersSerializer(source='answer_set', many=True)

    class Meta:
        model = Question
        fields = QuestionSerializer.Meta.fields + ["answers", ]


class InterviewSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(source='question_set', many=True)
    complete = serializers.BooleanField(default=False)

    class Meta:
        model = Interview
        fields = '__all__'


class CompleteInterviewSerializer(InterviewSerializer):
    questions = QuestionSerializerWithAnswer(source='question_set', many=True)
    complete = serializers.BooleanField(default=True)


class UserAnswersSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer = serializers.CharField()


class DoneInterviewSerializer(serializers.Serializer):
    interview = serializers.IntegerField()
    user = serializers.IntegerField()
    user_answers = UserAnswersSerializer(many=True)

    def validate_interview(self, value):

        if CompleteInterview.objects.filter(interview__id=value, user__id=self.initial_data['user']).exists():
            raise serializers.ValidationError(detail='Interview already done')

        pf_queryset = Question.objects.filter().prefetch_related("answervariant_set")
        pf = Prefetch("question_set", queryset=pf_queryset)
        instance_query = Interview.objects.prefetch_related(pf).filter(pk=value)

        if not instance_query.exists():
            raise serializers.ValidationError(detail=f'Interview dont exists id={value}')
        instance = instance_query.first()

        if not instance.update_active():
            raise serializers.ValidationError(detail='Interview already inactive')

        return instance

    def validate_user(self, value):
        return AnonUser.objects.get(id=value)

    def validate(self, attrs):
        user_answers = attrs['user_answers']
        result_user_answers = list()

        for question in attrs['interview'].question_set.all():
            user_answer = pop_user_answer(question.id, user_answers)

            if not user_answer:
                raise serializers.ValidationError(detail=f'Answer for question id={question.id} is required')

            elif len(user_answer) > 1 and question.type != 'MULTI_CHOICE':
                raise serializers.ValidationError(detail=f'To many answers for question id={question.id}')

            elif check_empty(user_answer):
                for error in check_empty(user_answer):
                    raise serializers.ValidationError(detail=f'One of answer for question id={error} is empty')

            elif question.type in ["MULTI_CHOICE", 'CHOICE'] and check_correct_variant(question.answervariant_set.all(), user_answer):
                for error in check_correct_variant(question.answervariant_set.all(), user_answer):
                    raise serializers.ValidationError(detail=f'Uncorrect answer variant text {error}')

            else:
                for one_answer in user_answer:
                    result_user_answers.append({
                        "question": question,
                        "text": one_answer['answer'],
                        "user": attrs['user'],
                    })
        for extra_answers in user_answers:
            raise serializers.ValidationError(detail=f'Question id={extra_answers["question_id"]} not in this interview')

        attrs['user_answers'] = result_user_answers
        return attrs

    def create(self, validated_data):
        complete = None
        try:
            with transaction.atomic():
                complete = CompleteInterview.objects.create(user=validated_data['user'],
                                                            interview=validated_data['interview'])

                Answer.objects.bulk_create(
                    [Answer(**answer) for answer in validated_data['user_answers']]
                )

        except DatabaseError:
            pass
        return complete
