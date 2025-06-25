from django.urls import path

from pdf_table_augmenter.views import ExtractDescriptionAPIView

urlpatterns = [
    path("extract-description", ExtractDescriptionAPIView.as_view(), name="extract_description"),
]
