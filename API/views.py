from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from AI_todo.models import Task, Category, ContextEntry
from .serializers import TaskSerializer, CategorySerializer, ContextEntrySerializer
from .ai_utils import get_ai_suggestions_with_gemini
from rest_framework import status
from .ai_utils import get_ai_suggestions_with_gemini
import logging
logger = logging.getLogger(__name__)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer

class ContextEntryViewSet(viewsets.ModelViewSet):
    queryset = ContextEntry.objects.all().order_by('-created_at')
    serializer_class = ContextEntrySerializer

@api_view(["GET"])
def health(_req):
    return Response({"ok": True})


@api_view(["POST"])
def ai_suggest(request):
    title = request.data.get("title", "").strip()
    description = request.data.get("description", "").strip()
    ctx_ids = request.data.get("context_ids", [])

    if ctx_ids:
        contexts = ContextEntry.objects.filter(id__in=ctx_ids).order_by('-created_at')
    else:
        # fetch most recent 1 (or a few, but util uses only most recent)
        contexts = ContextEntry.objects.all().order_by('-created_at')[:5]

    # prefer Gemini if configured, fallback to heuristic
    suggestions = get_ai_suggestions_with_gemini(title, description, list(contexts))

    return Response(suggestions)



@api_view(["DELETE"])
def delete_context(request, pk):
    try:
        ctx = ContextEntry.objects.get(pk=pk)
        ctx.delete()
        return Response({"message": "Context deleted"}, status=status.HTTP_204_NO_CONTENT)
    except ContextEntry.DoesNotExist:
        return Response({"error": "Context not found"}, status=status.HTTP_404_NOT_FOUND)
    