# document_app/views.py  (UPDATED: API-ONLY, NO TEMPLATES)
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer
# from .sync_google import sync_google_drive_file
# from .sync_notion import sync_notion_page

# API: List ALL docs (local + synced) & CREATE (upload local only)
class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # For file uploads

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save()  # user already set in serializer.create()


# Optional: Detail view for single doc (GET/PUT/DELETE)
class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)


# Sync endpoints (keep as before, but now pure API/JSON)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse  # Fallback for sync

'''@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def sync_google_api(request):
    code = request.GET.get("code")
    if not code:
        return Response({"error": "Authorization code required"}, status=400)
    synced = sync_google_drive_file(request.user, code)
    return Response({"synced_document_ids": synced})'''

'''@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def sync_notion_api(request):
    code = request.GET.get("code")
    if not code:
        return Response({"error": "Authorization code required"}, status=400)
    synced = sync_notion_page(request.user, code)
    return Response({"synced_document_ids": synced})'''