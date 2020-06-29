from django.contrib.auth.models import User
from django.db import models


class Questionnaire(models.Model):
    title = models.CharField(max_length=1024)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    share = models.CharField(max_length=32, default="authorized")
    deadline = models.DateTimeField(null=True, blank=True)
    limit = models.IntegerField(default=0)
    create_date = models.DateTimeField(auto_now_add=True)


# kind -> radio, checkbox, text, textarea, integer, float, rate
class Question(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    text = models.TextField()
    kind = models.CharField(max_length=32)
    max_rate = models.IntegerField(default=0, blank=True, null=True)
    conditional = models.BooleanField(default=False, null=True)
    condition_question = models.IntegerField(blank=True, null=True)
    condition_value = models.TextField(blank=True, null=True)


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()


class Paper(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    ip = models.CharField(max_length=32)
    ua = models.TextField()


class Answer(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
