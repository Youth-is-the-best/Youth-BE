from django.urls import path
from .views import InformationAPIView, InformationDetailAPIView

urlpatterns = [
    path('', InformationAPIView.as_view()),
    path('<int:id>/', InformationDetailAPIView.as_view()),
]
