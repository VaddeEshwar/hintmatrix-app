from django.contrib import admin

from question.models import Exam, ExamQuestion

admin.site.register(Exam)
admin.site.register(ExamQuestion)
