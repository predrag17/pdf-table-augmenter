import pdfplumber
import os
import yake
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

from langdetect import detect


def extract_keywords(text, max_keywords=5):
    try:
        lang = detect(text)
        lang = "mk" if lang.startswith("mk") else "en"
    except:
        lang = "en"

    kw_extractor = yake.KeywordExtractor(lan=lang, n=1, top=max_keywords)
    keywords = kw_extractor.extract_keywords(text)
    return [kw for kw, _ in keywords]


def generate_llm_description_from_keywords(title, keywords):
    keywords_text = ", ".join(keywords)
    prompt = (
        f"{f'Table title: {title}\n\n' if title else ''}"
        f"These are the most important keywords extracted from the context surrounding a table: {keywords_text}.\n"
        f"Based on these keywords, generate a short and informative description of what the table might be about."
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
        return f"[Error generating description from keywords: {e}]"


def generate_table_description_with_openai_from_data(title, preview_data):
    table_data_text = "\n".join(
        [" | ".join(cell for cell in row if cell is not None) for row in preview_data if row]
    )
    title_line = f"Table title: {title}\n\n" if title else ""
    prompt = (
        f"{title_line}"
        "This is the beginning of a table extracted from a PDF document. "
        "There is not enough surrounding context, so please generate a short and meaningful description "
        "based only on the table's structure and initial rows.\n\n"
        f"Table data:\n{table_data_text}\n\n"
        "Table description:"
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
                preview_data = table_rows if not has_enough_context else table_rows

                if has_enough_context:
                    keywords = extract_keywords(above_snippet + " " + below_snippet)
                    description = generate_llm_description_from_keywords(title_text, keywords)
                else:
                    description = generate_table_description_with_openai_from_data(title_text, preview_data)

                table_descriptions.append({
                    "page": page_number,
                    "table_index": table_index,
                    "description": description,
                    "preview_data": preview_data
                })

    return table_descriptions
