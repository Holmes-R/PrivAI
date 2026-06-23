import os
import logging
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Document
from .serializers import DocumentSerializer
from .vector_store import get_embedding_model, get_user_collection
from .utils import extract_text_from_file

logger = logging.getLogger(__name__)


class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save()


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        user_id = instance.user.id
        doc_id = instance.id
        try:
            collection = get_user_collection(user_id)
            all_ids = collection.get(where={"document_id": doc_id})["ids"]
            if all_ids:
                collection.delete(ids=all_ids)
                logger.info(f"Deleted {len(all_ids)} chunks for doc {doc_id}")
        except Exception as e:
            logger.warning(f"Vector cleanup failed for doc {doc_id}: {e}")
        if instance.file and os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
        instance.delete()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def search_documents(request):
    query = request.data.get("query", "")
    if not query:
        return Response({"error": "query required"}, status=400)

    model = get_embedding_model()
    query_emb = model.encode([query]).tolist()

    collection = get_user_collection(request.user.id)
    results = collection.query(
        query_embeddings=query_emb,
        n_results=5,
        include=["documents", "metadatas", "distances"]
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        hits.append({
            "text": doc,
            "title": meta["title"],
            "document_id": meta["document_id"],
            "score": round(1 - dist, 4)
        })

    return Response({"results": hits})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ask_documents(request):
    from .rag import answer_question
    from feedback_app.models import ChatHistory

    question = request.data.get("question", "")
    n_results = request.data.get("n_results", 5)
    document_id = request.data.get("document_id", None)
    history = request.data.get("history", None)
    if not question:
        return Response({"error": "question required"}, status=400)

    result = answer_question(request.user.id, question, n_results, document_id, history)

    if document_id:
        try:
            doc = Document.objects.get(id=document_id, user=request.user)
            ChatHistory.objects.create(
                user=request.user,
                document=doc,
                question=question,
                answer=result.get("answer", ""),
                sources=result.get("sources", []),
            )
        except Document.DoesNotExist:
            pass

    return Response(result)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def preview_document(request, doc_id):
    try:
        doc = Document.objects.get(id=doc_id, user=request.user)
    except Document.DoesNotExist:
        return Response({"error": "not found"}, status=404)

    if not doc.file:
        return Response({"error": "no file"}, status=400)

    try:
        text = extract_text_from_file(doc.file.path, doc.file_type)
        collection = get_user_collection(request.user.id)
        chunks_count = len(collection.get(where={"document_id": doc_id}).get("ids", []))
        return Response({
            "title": doc.title,
            "file_type": doc.file_type,
            "content": text[:5000],
            "word_count": len(text.split()),
            "chunk_count": chunks_count,
            "indexed": chunks_count > 0,
        })
    except Exception as e:
        logger.error(f"Preview failed: {e}")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def summarize_document_view(request, doc_id):
    from .rag import summarize_document
    from .utils import extract_text_from_file
    try:
        doc = Document.objects.get(id=doc_id, user=request.user)
    except Document.DoesNotExist:
        return Response({"error": "not found"}, status=404)
    if not doc.file:
        return Response({"error": "no file"}, status=400)
    try:
        text = extract_text_from_file(doc.file.path, doc.file_type)
        summary = summarize_document(text)
        return Response({"summary": summary or "Summary unavailable."})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def suggest_global_view(request):
    from .rag import suggest_global_questions
    questions = suggest_global_questions(request.user.id)
    return Response({"questions": questions})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def suggest_questions_view(request, doc_id):
    from .rag import suggest_questions
    from .utils import extract_text_from_file
    try:
        doc = Document.objects.get(id=doc_id, user=request.user)
    except Document.DoesNotExist:
        return Response({"error": "not found"}, status=404)
    if not doc.file:
        return Response({"error": "no file"}, status=400)
    try:
        text = extract_text_from_file(doc.file.path, doc.file_type)
        questions = suggest_questions(text)
        return Response({"questions": questions})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
