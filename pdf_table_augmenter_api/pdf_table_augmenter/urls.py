from django.urls import path

from pdf_table_augmenter.views import ExtractDescriptionAPIView, AskQuestionAPIView

urlpatterns = [
    path("extract-description", ExtractDescriptionAPIView.as_view(), name="extract_description"),
    path("ask-question", AskQuestionAPIView.as_view(), name="ask-question"),
]
