import os
import tempfile
from docling.document_converter import DocumentConverter
from openai import OpenAI
from langdetect import detect
import yake

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def extract_keywords(text: str, max_keywords=5):
    try:
        lang = "mk" if detect(text).startswith("mk") else "en"
    except:
        lang = "en"
    kw = yake.KeywordExtractor(lan=lang, n=1, top=max_keywords)
    return [w for w, _ in kw.extract_keywords(text)]


def generate_llm_description(chunks_before, chunks_after, title=None, keywords=None):
    prompt_parts = []

    if title:
        prompt_parts.append(f"Table Title:\n{title}\n")

    if keywords:
        prompt_parts.append("Relevant Keywords:\n" + ", ".join(keywords) + "\n")

    if chunks_before:
        prompt_parts.append("Context Before the Table:\n" + "\n".join(chunks_before) + "\n")

    if chunks_after:
        prompt_parts.append("Context After the Table:\n" + "\n".join(chunks_after) + "\n")

    prompt_parts.append(
        "Based on the surrounding context, provide a clear and concise description "
        "of what this table represents. Focus on the purpose, contents, and insights "
        "the table might provide. Ensure the description is coherent and relevant to the provided context."
    )

    prompt = "\n---\n".join(prompt_parts)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=700
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating description: {str(e)}"


def extract_table_descriptions_from_file(file_obj):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_obj.read())
        tmp_path = tmp.name

    try:
        converter = DocumentConverter()
        result = converter.convert(tmp_path)
        doc = result.document.export_to_dict()

        texts = doc.get("texts", [])
        tables = doc.get("tables", [])
        outputs = []

        for idx, table in enumerate(tables):
            body_children = doc.get("body", {}).get("children", [])
            table_ref = f"#/tables/{idx}"
            table_index_in_body = next(
                (i for i, child in enumerate(body_children) if child.get("$ref") == table_ref),
                None
            )

            if table_index_in_body is None:
                continue

            chunks_before = []
            chunks_after = []
            for i, child in enumerate(body_children):
                if child.get("$ref") == table_ref:
                    for j in range(max(0, i - 3), i):
                        if body_children[j].get("$ref", "").startswith("#/texts/"):
                            text_idx = int(body_children[j]["$ref"].split("/")[-1])
                            chunks_before.append(texts[text_idx]["text"])

                    for j in range(i + 1, min(i + 4, len(body_children))):
                        if body_children[j].get("$ref", "").startswith("#/texts/"):
                            text_idx = int(body_children[j]["$ref"].split("/")[-1])
                            chunks_after.append(texts[text_idx]["text"])
                    break

            if not chunks_before and not chunks_after:
                try:
                    df = table["data"].export_to_dataframe()
                    preview_rows = df.head(3).to_string(index=False)
                    chunks_before = [f"Table preview data:\n{preview_rows}"]
                except Exception:
                    chunks_before = ["[No context or data could be extracted from the table]"]

            page_number = table.get("prov", [{}])[0].get("page_no", 1)

            title = table.get("captions", [{}])[0].get("text") if table.get("captions") else None
            if title and not title.isupper():
                title = None

            context_text = "\n".join(chunks_before + chunks_after)
            keywords = extract_keywords(context_text) if context_text.strip() else None

            description = generate_llm_description(chunks_before, chunks_after, title, keywords)

            try:
                table_data = table["data"]["grid"]
                preview_data = [[cell["text"] for cell in row] for row in table_data]
            except Exception:
                preview_data = []

            outputs.append({
                "page": page_number,
                "table_index": idx + 1,
                "description": description,
                "preview_data": preview_data
            })

        return outputs

    except Exception as e:
        return [{"error": f"Failed to process PDF: {str(e)}"}]

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
