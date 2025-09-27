# pdf_table_augmenter/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from pdf_table_augmenter.management.commands.chatbot import answer_question
from pdf_table_augmenter.management.commands.pdf_image_augmenter import extract_image_descriptions_from_file
from pdf_table_augmenter.management.commands.pdf_table_augmenter import extract_table_descriptions_from_file


class ExtractDescriptionAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        pdf_file = request.FILES.get("pdf")
        if not pdf_file:
            return Response({"error": "No file provided."}, status=400)

        descriptions = extract_table_descriptions_from_file(pdf_file)
        return Response(descriptions)


class ExtractDescriptionForImagesAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        pdf_file = request.FILES.get("pdf")
        if not pdf_file:
            return Response({"error": "No file provided."}, status=400)

        descriptions = extract_image_descriptions_from_file(pdf_file)
        return Response(descriptions)


class AskQuestionAPIView(APIView):

    def post(self, request):
        question = request.data.get("question")
        table_description = request.data.get("table_description")

        if not question or not table_description:
            return Response({"error": "Missing question or table_data."}, status=400)

        try:
            answer = answer_question(question, table_description)
            return Response({"answer": answer}, status=200)
        except Exception as e:
            return Response({"error": f"Error answering question: {str(e)}"}, status=500)
