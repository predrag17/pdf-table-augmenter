# pdf_table_augmenter/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from pdf_table_augmenter.management.commands.pdf_table_augmenter import extract_table_descriptions_from_file


class ExtractDescriptionAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        pdf_file = request.FILES.get("pdf")
        if not pdf_file:
            return Response({"error": "No file provided."}, status=400)

        descriptions = extract_table_descriptions_from_file(pdf_file)
        return Response(descriptions)
