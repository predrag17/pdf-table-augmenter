from django.urls import path

from pdf_table_augmenter.views import ExtractDescriptionAPIView, AskQuestionAPIView, ExtractDescriptionForImagesAPIView, \
    ExtractDescriptionForFormulasAPIView

urlpatterns = [
    path("extract-description/tables", ExtractDescriptionAPIView.as_view(), name="extract_description_tables"),
    path("extract-description/images", ExtractDescriptionForImagesAPIView.as_view(), name="extract_description_images"),
    path("extract-description/formulas", ExtractDescriptionForFormulasAPIView.as_view(),
         name="extract_description_equations"),
    path("ask-question", AskQuestionAPIView.as_view(), name="ask-question"),
]
