from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),
    path("documents/", views.documents_page, name="documents"),
    path("documents/<int:doc_id>/ask/", views.document_ask_page, name="document-ask"),
    path("ask/", views.ask_page, name="ask"),

]
