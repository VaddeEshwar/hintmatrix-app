from django.contrib.auth import views
from django.urls import path
from django.views.generic import TemplateView

from website.pg_views import (
    PgReturnView,
    PgNotifyView,
    PgReturnViewV2
)
from website.secure_view import (
    QuestionCreateView,
    QuestionView,
    AnswerView,
    AnswerHistoryView,
    AnsweredView,
    BackupRuleEngine,
    AnsweredTableView,
    ChapterView,
    ChapterQuestionCreateView,
    LogsView,
    CopyQuestionView,
    ToDoView,
    SiChapterView,
    CourseSubscriptionView,
    MyCourseView,
    MyProfileView,
    MyReferenceView
)
from website.views import (
    SignUpView, SignUpDoneView, QuestionView as NsQunView,
    SignUpActivateView, ForgotPasswordView, SetForgotPasswordView
)

app_name = "website_v2"
urlpatterns = [
    # session
    path("my-app/", MyCourseView.as_view(), name="my-course"),
    path("my-app/profile/", MyProfileView.as_view(), name="my-profile"),
    path("my-app/reference/", MyReferenceView.as_view(), name="my-reference"),
    path(
        "my-app/todo/<uuid:question_slug>/",
        ToDoView.as_view(),
        name="todo-task",
    ),
    path(
        "my-app/logs/<str:chapter_code>/<uuid:slug>/<str:title>/",
        LogsView.as_view(),
        name="logs-chapter-question",
    ),
    path("my-app/logs/<str:chapter_code>/", LogsView.as_view(),
         name="logs-chapter"),
    path("my-app/logs/", LogsView.as_view(), name="logs"),
    path(
        "my-app/chapter/<str:chapter_code>/",
        ChapterView.as_view(),
        name="chapter-wise-category",
    ),
    path(
        "my-app/chapter/<str:chapter_code>/<str:qun_category>/",
        ChapterView.as_view(),
        name="chapter-wise-question",
    ),
    path("my-app/chapter/", ChapterView.as_view(), name="chapter"),
    path("my-app/si-chapter/", SiChapterView.as_view(), name="si-chapter"),
    path(
        "my-app/question/<str:chapter_code>/<uuid:q_slug>/<str:title>/",
        QuestionView.as_view(),
        name="list-question",
    ),
    path(
        "my-app/create/",
        ChapterQuestionCreateView.as_view(),
        name="chapter-create-question",
    ),
    path(
        "my-app/create/<str:chapter_code>/",
        QuestionCreateView.as_view(),
        name="create-question",
    ),
    path(
        "my-app/answer/<str:chapter_code>/<uuid:q_slug>/<str:title>/answered/",
        AnsweredView.as_view(),
        name="qun_answered",
    ),
    path(
        "my-app/answer/<str:chapter_code>/<uuid:q_slug>/<str:title>/history/",
        AnswerHistoryView.as_view(),
        name="answer_history",
    ),
    path(
        "my-app/answer/<str:chapter_code>/<uuid:q_slug>/<str:title>/",
        AnswerView.as_view(),
        name="qun_answer",
    ),
    path(
        "my-app/answer/<str:chapter_code>/<uuid:q_slug>/<str:title>/step1/",
        AnswerView.as_view(),
        name="qun_answer_step1",
    ),
    path(
        "my-app/question/<str:chapter_code>/table/",
        AnsweredTableView.as_view(),
        name="tbl-question",
    ),
    # copy question
    path(
        "my-app/copy/<str:chapter_code>/<uuid:question_slug>/",
        CopyQuestionView.as_view(),
        name="copy-question",
    ),
    # backup rule engine
    path("my-app/backup/rule-engine/", BackupRuleEngine.as_view(),
         name="bck_engine"),
    # path(
    #     "my-app/",
    #     TemplateView.as_view(template_name="v2/secure/dashboard.html"),
    #     name="dashboard",
    # ),
    # PG
    path(
        "my-app/course-subscribe/",
        CourseSubscriptionView.as_view(),
        name="course-subscribe-1",
    ),
    path(
        "my-app/course-subscribe/<uuid:course>/",
        CourseSubscriptionView.as_view(),
        name="course-subscribe-2",
    ),
    path(
        "pg/return/v2/<str:pg_name>/",
        PgReturnViewV2.as_view(),
        name="pg-return-v2",
    ),
    path(
        "pg/return/<str:order_id>/<str:order_token>/",
        PgReturnView.as_view(),
        name="pg-return",
    ),
    path("pg/notify/<str:pg_name>/", PgNotifyView.as_view(), name="pg-notify"),
    # non session
    path("question/", NsQunView.as_view(), name="n-question"),
    path(
        "question/<str:chapter_code>/<uuid:q_slug>/<str:title>/",
        NsQunView.as_view(),
        name="n-question_details",
    ),
    # auth
    path(
        "login/", views.LoginView.as_view(template_name="v2/login.html"),
        name="login"
    ),
    path(
        "logout/",
        views.LogoutView.as_view(template_name="v2/login.html"),
        name="logout",
    ),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("signup/done/", SignUpDoneView.as_view(), name="signup-done"),
    path("signup/activate/<uuid:cache_id>/", SignUpActivateView.as_view(),
         name="signup-activate"),
    path("forgot-password/", ForgotPasswordView.as_view(),
         name="forgot-password"),
    path("forgot-password/<uuid:cache_id>/", SetForgotPasswordView.as_view(),
         name="forgot-password-set"),
    # path('password-change/', views.PasswordChangeView.as_view(),
    # name='password_change'),
    # path('password-change/done/', views.PasswordChangeDoneView.as_view(),
    # name='password_change_done'),
    # path('password-reset/', views.PasswordResetView.as_view(),
    # name='password_reset'),
    # path('password-reset/done/', views.PasswordResetDoneView.as_view(),
    # name='password_reset_done'),
    # path('reset/<uidb64>/<token>/',
    # views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/',
    # views.PasswordResetCompleteView.as_view(),
    # name='password_reset_complete'),
    path("", TemplateView.as_view(template_name="v3/index.html"),
         name="index"),
]
