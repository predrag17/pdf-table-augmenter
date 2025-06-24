from django.core.management.base import BaseCommand
import pdfplumber
import json
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


class Command(BaseCommand):
    help = 'Extracts descriptions of tables from a PDF document using OpenAI.'

    def add_arguments(self, parser):
        parser.add_argument('pdf_path', type=str, help='Path to the PDF file.')

    def handle(self, *args, **kwargs):
        pdf_path = kwargs['pdf_path']

        if not os.path.exists(pdf_path):
            self.stderr.write(self.style.ERROR(f"File not found: {pdf_path}"))
            return

        descriptions = self.extract_table_descriptions(pdf_path)
        self.stdout.write(json.dumps(descriptions, indent=2, ensure_ascii=False))

    def extract_table_descriptions(self, pdf_path):
        table_descriptions = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                tables = page.find_tables()
                words = page.extract_words()

                for table_index, table in enumerate(tables, start=1):
                    bbox = table.bbox

                    above_text = [w for w in words if w['bottom'] < bbox[1]]
                    below_text = [w for w in words if w['top'] > bbox[3]]

                    above_snippet = " ".join([w['text'] for w in sorted(above_text, key=lambda x: x['bottom'])][-20:])
                    below_snippet = " ".join([w['text'] for w in sorted(below_text, key=lambda x: x['top'])][:20])

                    description = self.generate_table_description_with_openai(above_snippet, below_snippet)

                    table_descriptions.append({
                        "page": page_number,
                        "table_index": table_index,
                        "description": description,
                        "preview_data": table.extract()[:3]
                    })

        return table_descriptions

    def generate_table_description_with_openai(self, above, below):
        prompt = (
            f"This is the text that appears before and after a table in a PDF document. "
            f"Based on this context, generate a brief and meaningful description of what the table is likely about.\n\n"
            f"Text before the table:\n{above.strip()}\n\n"
            f"Text after the table:\n{below.strip()}\n\n"
            f"Table description:"
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"[Грешка при повик до OpenAI: {e}]"
