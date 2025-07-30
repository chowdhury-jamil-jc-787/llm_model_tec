from django.urls import path
from .views import PromptAPIView

urlpatterns = [
    path('prompt/', PromptAPIView.as_view(), name='prompt'),
]