from django.db import models
from django.utils import timezone

from users.models import AnonUser

TYPECHOICES = (
    ("TEXT", "text"),
    ("CHOICE", "choice"),
    ("MULTI_CHOICE", "multi_choice")
)


class Interview(models.Model):

    name = models.CharField(max_length=50)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    description = models.CharField(max_length=200)
    active = models.BooleanField(default=True)

    def update_active(self, save=True):
        new_active = self.end_time > timezone.now()
        if self.active != new_active:
            self.active = new_active
            if save:
                self.save(update_fields=['active'])
        return self.active

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, *args, **kwargs):
        self.active = self.update_active(save=False)
        super(Interview, self).save(*args, **kwargs)


class Question(models.Model):

    text = models.CharField(max_length=200)
    type = models.CharField(max_length=12, choices=TYPECHOICES, default=TYPECHOICES)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, *args, **kwargs):
        self.answer_set.all().delete()
        if self.type == 'TEXT':
            self.answervariant_set.all().delete()

        super(Question, self).save(*args, **kwargs)

    def __str__(self):
        return self.text


class AnswerVariant(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, *args, **kwargs):
        self.question.answer_set.all().delete()
        if self.question.type != 'TEXT':
            super(AnswerVariant, self).save(*args, **kwargs)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    user = models.ForeignKey(AnonUser, on_delete=models.CASCADE)


class CompleteInterview(models.Model):
    user = models.ForeignKey(AnonUser, on_delete=models.CASCADE)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)

    def delete(self, using=None, keep_parents=False):
        Answer.objects.filter(user=self.user, question__interview=self.interview).delete()
        super(CompleteInterview, self).delete(using, keep_parents)




