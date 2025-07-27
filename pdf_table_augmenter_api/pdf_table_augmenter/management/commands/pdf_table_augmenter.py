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


def get_cell_text(cell):
    return cell.get("text", "").strip() if isinstance(cell, dict) else str(cell).strip()


def extract_caption(table):
    captions = table.get("captions", [])
    if isinstance(captions, list) and captions:
        return captions[0].get("text", "") or str(captions[0].get("$ref", ""))
    return table.get("caption", "") or table.get("metadata", {}).get("caption", "")


def caption_similarity(c1, c2):
    if not c1 or not c2:
        return True

    c1_words = set(c1.lower().split())
    c2_words = set(c2.lower().split())
    if not c1_words or not c2_words:
        return True

    return len(c1_words.intersection(c2_words)) / len(c1_words.union(c2_words)) >= 0.3


def extract_headers(grid):
    if not grid:
        return []

    first_row = grid[0]
    headers = [get_cell_text(cell) for cell in first_row if
               isinstance(cell, dict) and cell.get("column_header", False)]
    if not headers:
        headers = [get_cell_text(cell) for cell in first_row]
    return [h for h in headers if h]


def extract_ids(data):
    return sorted([text for text in data if re.match(r'^\d+$|^[A-Za-z]+\d+$', text)])


def are_tables_related(table1, table2, header_similarity_threshold=0.5, data_similarity_threshold=0.3):
    pages1 = sorted(set(p.get("page_no", 1) for p in table1.get("prov", []))) if table1.get("prov") else [1]
    pages2 = sorted(set(p.get("page_no", 1) for p in table2.get("prov", []))) if table2.get("prov") else [1]

    page_proximity = abs(max(pages1) - min(pages2)) <= 1

    caption1 = extract_caption(table1)
    caption2 = extract_caption(table2)

    caption_check = caption_similarity(caption1, caption2)

    grid1 = table1["data"]["grid"]
    grid2 = table2["data"]["grid"]
    if not grid1 or not grid2:
        print("Missing grid data in one or both tables")
        return False

    header1 = extract_headers(grid1)
    header2 = extract_headers(grid2)

    if header1 and header2:
        common_headers = set(header1).intersection(set(header2))
        header_similarity = len(common_headers) / max(len(set(header1)), len(set(header2)))
        header_check = header_similarity >= header_similarity_threshold
    else:
        header_check = False
        print("Header check skipped due to missing or empty headers")

    data1 = [get_cell_text(cell) for row in grid1[1:] for cell in row if row] if len(grid1) > 1 else []
    data2 = [get_cell_text(cell) for row in grid2[1:] for cell in row if row] if len(grid2) > 1 else []

    if data1 and data2:
        data_set1 = set(data1)
        data_set2 = set(data2)
        common_data = data_set1.intersection(data_set2)
        data_similarity = len(common_data) / len(data_set1.union(data_set2))
        data_check = data_similarity >= data_similarity_threshold
    else:
        data_check = False
        print("Data check skipped due to missing data")

    ids1 = extract_ids(data1)
    ids2 = extract_ids(data2)

    id_continuity = False
    if ids1 and ids2:
        try:
            nums1 = [int(re.search(r'\d+', id).group()) for id in ids1 if re.search(r'\d+', id)]
            nums2 = [int(re.search(r'\d+', id).group()) for id in ids2 if re.search(r'\d+', id)]
            if nums1 and nums2:
                id_continuity = max(nums1) + 1 >= min(nums2) or set(nums1).intersection(set(nums2))
        except (AttributeError, ValueError):
            print("ID continuity check skipped due to non-numeric IDs")

    related = (header_check or data_check or id_continuity) and (page_proximity or caption_check)
    print(f"Final decision: Tables are {'related' if related else 'not related'}")
    return related


def merge_tables(table1, table2):
    merged = table1.copy()
    merged["prov"] = table1.get("prov", []) + table2.get("prov", [])

    grid1 = table1["data"]["grid"]
    grid2 = table2["data"]["grid"]

    merged_grid = []

    if grid1 and grid2:
        merged_grid = grid1 + grid2
    elif grid1:
        merged_grid = grid1
    elif grid2:
        merged_grid = grid2

    merged["data"]["grid"] = merged_grid
    print(f"Merged table has {len(merged['data']['grid'])} rows")
    return merged


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
        print(f"Document parsed: {len(doc.get('texts', []))} texts, {len(doc.get('tables', []))} tables")

        texts = doc.get("texts", [])
        tables = doc.get("tables", [])

        for idx, table in enumerate(tables):
            table["index"] = idx

        merged_tables = []
        i = 0
        while i < len(tables):
            current_table = tables[i]
            if i + 1 < len(tables) and are_tables_related(current_table, tables[i + 1]):
                print(f"Merging Table {i + 1} and Table {i + 2} as a multi-page table")
                current_table = merge_tables(current_table, tables[i + 1])
                i += 2
            else:
                i += 1

            merged_tables.append(current_table)

        outputs = []
        for idx, table in enumerate(merged_tables):
            body_children = doc.get("body", {}).get("children", [])
            table_ref = f"#/tables/{table.get('index', idx)}"
            table_index_in_body = next(
                (i for i, child in enumerate(body_children) if child.get("$ref") == table_ref),
                None
            )

            if table_index_in_body is None:
                print(f"Table {idx + 1} not found in body.children, skipping")
                continue

            prov = table.get("prop", [])
            page_numbers = sorted(set(p.get("page_no", 1) for p in prov)) if prov else [1]
            page_display = f"Pages {min(page_numbers)}-{max(page_numbers)}" if len(
                page_numbers) > 1 else f"Page {page_numbers[0]}" if page_numbers else "Page 1"

            title = None
            captions = table.get("captions", [])
            if captions:
                if isinstance(captions, list) and len(captions) > 0 and captions[0].get("$ref", "").startswith(
                        "#/texts/"):
                    text_idx = int(captions[0]["$ref"].split("/")[-1])
                    if text_idx < len(texts):
                        title = texts[text_idx]["text"]
                elif isinstance(captions, dict) and captions.get("$ref", "").startswith("#/texts/"):
                    text_idx = int(captions["$ref"].split("/")[-1])
                    if text_idx < len(texts):
                        title = texts[text_idx]["text"]

            if not title:
                title = table.get("caption", "")
            if not title:
                title = table.get("metadata", {}).get("caption", "")
            if not title and prov:
                title = prov[0].get("caption", "")

            table_id = f"Table {idx + 1}" if not title else title
            print(f"Table {idx + 1}: Using table_id: '{table_id}'")

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
                    text_page = texts[text_idx].get("prov", [{}])[0].get("page_no", 1) if texts[text_idx].get(
                        "prov") else 1

                    if table_id and text_content.strip().lower() == table_id.strip().lower():
                        continue

                    if any(re.search(pattern, text_content, re.IGNORECASE) for pattern in table_ref_patterns):
                        if i < table_index_in_body:
                            chunks_before.append(text_content)
                        elif i > table_index_in_body:
                            chunks_after.append(text_content)

            total_chunks = len(chunks_before) + len(chunks_after)

            # First fallback --> if there is no paragraphs before and after the table, we take the whole data from the table
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
                "page": page_display,
                "table_index": idx + 1,
                "description": description,
                "preview_data": preview_data
            })

        print(f"Returning {len(outputs)} table descriptions")
        return outputs

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return [{"error": f"Failed to process PDF: {str(e)}"}]

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
