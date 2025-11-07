# document_app/urls.py  (UPDATED: API ENDPOINTS)
from django.urls import path
from . import views
from .views import *
urlpatterns = [
    # API: GET=List all docs, POST=Upload local file
    path("", DocumentListCreateView.as_view(), name="document-list-create"),
    # API: GET/PUT/DELETE single doc by ID
    path("<int:pk>/", DocumentDetailView.as_view(), name="document-detail"),
    # API Sync (OAuth callback)
    #path("sync/google/", sync_google_api, name="sync_google"),
    #path("sync/notion/", sync_notion_api, name="sync_notion"),
    path("search/", views.search_documents, name="search"),
]