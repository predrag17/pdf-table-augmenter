import pdfplumber
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def extract_table_descriptions_from_file(file_obj):
    table_descriptions = []

    with pdfplumber.open(file_obj) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.find_tables()
            words = page.extract_words()

            for table_index, table in enumerate(tables, start=1):
                bbox = table.bbox

                above_text = [w for w in words if w['bottom'] < bbox[1]]
                below_text = [w for w in words if w['top'] > bbox[3]]

                title_line = next(
                    (w for w in reversed(above_text)
                     if "table" in w['text'].strip().lower() or "табела" in w['text'].strip().lower()),
                    None
                )
                title_text = title_line['text'].strip() if title_line else ""

                above_snippet = " ".join(
                    [w['text'] for w in sorted(above_text, key=lambda x: x['bottom'])][-30:])
                below_snippet = " ".join(
                    [w['text'] for w in sorted(below_text, key=lambda x: x['top'])][:30])

                has_enough_context = len(above_snippet.strip()) + len(below_snippet.strip()) >= 30

                table_rows = table.extract()
                preview_data = table_rows if not has_enough_context else table_rows[:3]

                if has_enough_context:
                    description = generate_table_description_with_openai(title_text, above_snippet, below_snippet)
                else:
                    description = generate_table_description_with_openai_from_data(title_text, preview_data)

                table_descriptions.append({
                    "page": page_number,
                    "table_index": table_index,
                    "description": description,
                    "preview_data": preview_data
                })

    return table_descriptions


def generate_table_description_with_openai_from_data(title, preview_data):
    table_data_text = "\n".join(
        [" | ".join(cell for cell in row if cell is not None) for row in preview_data if row]
    )
    prompt = (
        f"{f'Table title: {title}\n\n' if title else ''}"
        f"This is the beginning of a table extracted from a PDF document. "
        f"There is not enough surrounding context, so please generate a short and meaningful description "
        f"based only on the table's structure and initial rows.\n\n"
        f"Table data:\n{table_data_text}\n\n"
        f"Table description:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error while sending request to OpenAI: {e}]"


def generate_table_description_with_openai(title, above, below):
    prompt = (
        f"{f'Table title: {title}\n\n' if title else ''}"
        f"This is the text that appears before and after a table in a PDF document. "
        f"Based on this context, generate a brief and meaningful description of what the table is likely about.\n\n"
        f"Text before the table:\n{above.strip()}\n\n"
        f"Text after the table:\n{below.strip()}\n\n"
        f"Table description:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error while sending request to OpenAI: {e}]"
