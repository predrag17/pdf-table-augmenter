import os
import tempfile
import re
import yake

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

from openai import OpenAI
from langdetect import detect

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def extract_keywords(text: str, max_keywords=5):
    try:
        lang = "mk" if detect(text).startswith("mk") else "en"
    except:
        lang = "en"
    kw = yake.KeywordExtractor(lan=lang, n=1, top=max_keywords)
    return [w for w, _ in kw.extract_keywords(text)]


def generate_llm_description(chunks_before, chunks_after, title=None, keywords=None, table_data_preview=None):
    prompt_parts = []

    if title:
        prompt_parts.append(f"Table Title:\n{title}\n")

    if keywords:
        prompt_parts.append("Relevant Keywords:\n" + ", ".join(keywords) + "\n")

    if chunks_before or chunks_after:
        if chunks_before:
            prompt_parts.append("Context Before the Table:\n" + "\n".join(chunks_before) + "\n")
        if chunks_after:
            prompt_parts.append("Context After the Table:\n" + "\n".join(chunks_after) + "\n")

    if table_data_preview:
        prompt_parts.append(
            "This table data preview can help to generate a more beautiful description:\n" + table_data_preview + "\n"
        )

    prompt_parts.append(
        "Based on the provided context or table data, provide a clear and concise description "
        "of what this table represents. Focus on the purpose, contents, and insights "
        "the table might provide. Ensure the description is coherent and relevant to the provided information."
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
        pipeline_options = PdfPipelineOptions(
            do_ocr=False,
            do_table_structure=True
        )
        converter = DocumentConverter(format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        })
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

            title = None
            if table.get("captions"):
                captions = table.get("captions")
                if isinstance(captions, list) and captions and captions[0].get("$ref", "").startswith("#/texts/"):
                    text_idx = int(captions[0]["$ref"].split("/")[-1])
                    if text_idx < len(texts):
                        title = texts[text_idx]["text"]
                elif isinstance(captions, dict) and captions.get("$ref", "").startswith("#/texts/"):
                    text_idx = int(captions["$ref"].split("/")[-1])
                    if text_idx < len(texts):
                        title = texts[text_idx]["text"]

            if not title:
                title = table.get("caption")
            if not title:
                title = table.get("metadata", {}).get("caption")
            if not title and table.get("prov"):
                title = table.get("prov", [{}])[0].get("caption")

            table_id = f"Table {idx + 1}" if not title else title

            table_ref_patterns = [
                rf"\b[Tt]able\s*{idx + 1}\b",
                rf"\b[Ss]ee\s*[Tt]able\s*{idx + 1}\b",
                rf"\b[Tt]he\s*[Tt]able\s*{idx + 1}\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Tt]able\s*{idx + 1}\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Tt]able\s*{idx + 1}\b",
            ]
            if table_id and not table_id.isupper():
                table_ref_patterns.append(rf"\b{re.escape(table_id)}\b")

            chunks_before = []
            chunks_after = []

            for i, child in enumerate(body_children):
                if child.get("$ref", "").startswith("#/texts/"):
                    text_idx = int(child["$ref"].split("/")[-1])
                    text_content = texts[text_idx]["text"]

                    if table_id and text_content.strip().lower() == table_id.strip().lower():
                        continue

                    if any(re.search(pattern, text_content, re.IGNORECASE) for pattern in table_ref_patterns):
                        if i < table_index_in_body:
                            chunks_before.append(text_content)
                        elif i > table_index_in_body:
                            chunks_after.append(text_content)

            # TODO: ask for this, and delete or keep if needed
            # total_chunks = len(chunks_before) + len(chunks_after)

            # First fallback --> if there is no references to that table, we take 3 paragraphs before and after
            # if total_chunks <= 20:
            #     temp_chunks_before = []
            #     temp_chunks_after = []
            #
            #     for i in range(max(0, table_index_in_body - 3), table_index_in_body):
            #         if body_children[i].get("$ref", "").startswith("#/texts/"):
            #             text_idx = int(body_children[i]["$ref"].split("/")[-1])
            #             text_content = texts[text_idx]["text"]
            #             if table_id and text_content.strip().lower() == table_id.strip().lower():
            #                 continue
            #             chunks_before.append(text_content)
            #
            #     for i in range(table_index_in_body + 1, min(table_index_in_body + 4, len(body_children))):
            #         if body_children[i].get("$ref", "").startswith("#/texts/"):
            #             text_idx = int(body_children[i]["$ref"].split("/")[-1])
            #             text_content = texts[text_idx]["text"]
            #             if table_id and text_content.strip().lower() == table_id.strip().lower():
            #                 continue
            #             chunks_after.append(text_content)
            #
            #     table_text = table_id if table_id else ""
            #     try:
            #         grid = table["data"].get("grid", [])
            #         if grid:
            #             table_text += "\n" + "\n".join(
            #                 "\t".join(cell.get("text", "") for cell in row) for row in grid
            #             )
            #     except Exception:
            #         pass

            total_chunks = len(chunks_before) + len(chunks_after)

            # Second fallback --> if there is no paragraphs before and after the table, we take the whole data from the table
            table_data_preview = None
            if total_chunks <= 20:
                try:
                    grid = table["data"].get("grid", [])
                    if grid:
                        table_data_preview = "\n".join(
                            "\t".join(cell.get("text", "") for cell in row) for row in grid
                        )
                    else:
                        table_data_preview = "[No table data could be extracted]"
                except Exception as e:
                    table_data_preview = f"[Error extracting table data: {str(e)}]"

            context_text = "\n".join(chunks_before + chunks_after)
            keywords = extract_keywords(context_text) if context_text.strip() else None
            description = generate_llm_description(chunks_before, chunks_after, table_id, keywords, table_data_preview)

            try:
                table_data = table["data"]["grid"]
                preview_data = [[cell["text"] for cell in row] for row in table_data]
            except Exception:
                preview_data = []

            outputs.append({
                "page": table.get("prov", [{}])[0].get("page_no", 1),
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
