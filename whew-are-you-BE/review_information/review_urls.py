from django.urls import path
from .views import ReviewAPIView, ReviewDetailAPIView, ReviewLikeAPIView, ReviewStorageAPIView, CommentAPIView, CommentDetailAPIView, FetchRelatedReviewsAPIView

urlpatterns = [
    path('', ReviewAPIView.as_view()),
    path('<int:id>/', ReviewDetailAPIView.as_view()),
    path('likes/<int:id>/', ReviewLikeAPIView.as_view()),
    path('storages/<int:id>/', ReviewStorageAPIView.as_view()),
    path('<int:review_id>/comments/', CommentAPIView.as_view()),
    path('related/<int:bingo_item_id>/', FetchRelatedReviewsAPIView.as_view()),
    path('comments/<int:comment_id>/', CommentDetailAPIView.as_view()),
]
