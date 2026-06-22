from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from document_app.models import Document


def index(request):
    return render(request, "index.html")


def login_page(request):
    return render(request, "login.html")


def register_page(request):
    return render(request, "register.html")


def documents_page(request):
    return render(request, "documents.html")


def ask_page(request):
    return render(request, "ask.html")


def document_ask_page(request, doc_id):
    return render(request, "document_ask.html", {"doc_id": doc_id})



