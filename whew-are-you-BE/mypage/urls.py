from django.urls import path
from .views import *

urlpatterns = [
    path('', MyInfoAPIView.as_view()),    
    path('news/', NewsAPIView.as_view()),
    path('news/option/heart/', HeartOptionAPIView.as_view()),
    path('news/option/comment/', CommentOptionAPIView.as_view()),
    path('news/option/hue/', HueOptionAPIView.as_view()),
    path('news/option/point/', PointOptionAPIView.as_view()),
    path('news/option/not-read/', ReadOptionAPIView.as_view()),
]
