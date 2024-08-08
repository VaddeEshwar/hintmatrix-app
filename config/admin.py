from django.contrib import admin

from config.models import (
    TableHeader,
    TableAttribute,
    TableName,
    RuleEngine,
    Chapter,
    QuestionCategory,
    Course,
    State,
)


class RuleEngineAdmin(admin.ModelAdmin):
    model = RuleEngine
    search_fields = (
        "tbl_attribute__code", "chapter__code", "pair_attr__code",
        "tbl1__code", "tbl2__code", "tbl3__code", "tbl4__code")

    autocomplete_fields = (
        "tbl_attribute", "pair_attr", "tbl1", "tbl2", "tbl3", "tbl4", )

    list_display = (
        "attribute_name",
        "tbl_attribute_type",
        "chapter",
        "rel_name",
        "pair_att_with",
        "pair_attr_priority",
        "operation1",
        "tbl1_name",
        "header1_name",
        "help1",
        "operation2",
        "tbl2_name",
        "header2_name",
        "help2",
        "operation3",
        "tbl3",
        "header3",
        "help3",
        "c_on",
    )


class ChapterAdmin(admin.ModelAdmin):
    model = Chapter
    list_display = ("code", "course", "name", "is_active", "c_on")


class CourseAdmin(admin.ModelAdmin):
    model = Course
    list_display = ("code", "name", "is_active", "c_on")


class StateAdmin(admin.ModelAdmin):
    model = State
    list_display = ("code", "name", "is_active", "c_on")


class TableAttributeAdmin(admin.ModelAdmin):
    model = TableAttribute
    list_display = ("code", "name", "tbl_header", "short_name", )
    search_fields = ("name", )


class TableNameAdmin(admin.ModelAdmin):
    model = TableName
    list_display = ("code", "name", )
    search_fields = ("name", )


admin.site.register(Course, CourseAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(TableHeader)
admin.site.register(TableAttribute, TableAttributeAdmin)
admin.site.register(TableName, TableNameAdmin)
admin.site.register(QuestionCategory)
admin.site.register(RuleEngine, RuleEngineAdmin)
admin.site.register(State, StateAdmin)
