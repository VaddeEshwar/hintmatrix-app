from django.contrib import admin

from answer.models import ExamAnswer, AnswerEvent


class AnswerEventAdmin(admin.ModelAdmin):
    model = AnswerEvent
    list_display = ("user", "valid", "score", "get_qun", "get_attr",)
    search_fields = ("user__username", "qun__attribute__name", "exam__name")

    def get_qun(self, obj):
        if obj.exam:
            return obj.exam.name

    get_qun.short_description = 'Question'
    get_qun.admin_order_field = 'exam__name'

    def get_attr(self, obj):
        if obj.qun:
            return obj.qun.attribute

    get_attr.short_description = 'Attribute'
    get_attr.admin_order_field = 'qun__attribute'


admin.site.register(ExamAnswer)
admin.site.register(AnswerEvent, AnswerEventAdmin)
