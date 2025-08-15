from django.urls import path
# from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CategoryViewSet, ContextEntryViewSet, ai_suggest, health

from . import views

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'context', ContextEntryViewSet, basename='context')

urlpatterns = [
    path('health/', health),
    path('ai/suggest/', ai_suggest),
    path('', include(router.urls)),
    path('contexts/<int:pk>/delete/', views.delete_context, name='delete_context'),
]
