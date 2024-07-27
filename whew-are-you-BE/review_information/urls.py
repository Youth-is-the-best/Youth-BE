from django.urls import path
from .views import InformationAPIView

urlpatterns = [
    path('', InformationAPIView.as_view()),
]
