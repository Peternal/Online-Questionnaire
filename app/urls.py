from django.contrib import admin
from django.urls import path, include

from app import views

urlpatterns = [
    path("", views.index_view),
    path("login", views.login_view),
    path("logout", views.logout_view),
    path("register", views.register_view),

    path("design", views.design_view),
    path("papers/<int:id>", views.paper_view),
    path("share/<int:id>", views.share_view),
    path("papers/<int:id>/dashboard", views.paper_detail_view),
    path("questionnaires/<int:id>", views.questionnaire_dashboard_view),
    path("questionnaires/<int:id>/delete", views.questionnaire_delete_view),
]
