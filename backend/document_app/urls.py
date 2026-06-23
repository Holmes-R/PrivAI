# document_app/urls.py  (UPDATED: API ENDPOINTS)
from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path("", DocumentListCreateView.as_view(), name="document-list-create"),
    path("<int:pk>/", DocumentDetailView.as_view(), name="document-detail"),
    path("<int:doc_id>/preview/", views.preview_document, name="document-preview"),
    path("<int:doc_id>/summarize/", views.summarize_document_view, name="document-summarize"),
    path("<int:doc_id>/suggest/", views.suggest_questions_view, name="document-suggest"),
    path("suggest-global/", views.suggest_global_view, name="suggest-global"),
    path("search/", views.search_documents, name="search"),
    path("ask/", views.ask_documents, name="ask"),
]