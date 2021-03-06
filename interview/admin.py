from django.contrib import admin

# Register your models here.
from interview.models import Interview, Question, Answer, AnswerVariant, CompleteInterview


class AnswerVariantInline(admin.StackedInline):
    model = AnswerVariant
    min_num = 0
    show_change_link = True
    extra = 0


class QuestionInstanceInline(admin.StackedInline):
    model = Question
    show_change_link = True
    min_num = 1
    extra = 0


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'questions_count', 'time_to_end', 'active', 'complete_count')
    readonly_fields = ('start_time',)
    fields = ['active', 'name', 'description', ('start_time', 'end_time'), ]
    inlines = [QuestionInstanceInline]
    list_select_related = True

    @staticmethod
    def questions_count(obj):
        return obj.question_set.count()

    @staticmethod
    def time_to_end(obj):
        return obj.end_time - obj.start_time

    @staticmethod
    def complete_count(obj):
        return CompleteInterview.objects.filter(interview=obj).count()


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'variants_count')
    inlines = [AnswerVariantInline]

    @staticmethod
    def variants_count(obj):
        return obj.answervariant_set.count()


admin.site.register(Answer)
admin.site.register(AnswerVariant)
admin.site.register(CompleteInterview)
