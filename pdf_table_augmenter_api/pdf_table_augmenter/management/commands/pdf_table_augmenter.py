import os
import tempfile
import re

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from pdf_table_augmenter.management.commands.reusable_functions import extract_caption, roman_numeral, get_cell_text, \
    generate_table_llm_description


def extract_table_descriptions_from_file(file_obj):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_obj.read())
        tmp_path = tmp.name

    try:
        pipeline_options = PdfPipelineOptions(
            do_ocr=False,
            do_table_structure=True,
            generate_picture_images=False,
            do_picture_description=False
        )
        converter = DocumentConverter(format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        })

        result = converter.convert(tmp_path)
        doc = result.document.export_to_dict()
        print(f"Document parsed: {len(doc.get('texts', []))} texts, {len(doc.get('tables', []))} tables")

        texts = doc.get("texts", [])
        body_children = doc.get("body", {}).get("children", [])

        valid_tables = []
        for table in doc.get("tables", []):
            grid = table.get("data", {}).get("grid", [])
            if grid and isinstance(grid, list) and len(grid) > 0 and any(len(row) > 0 for row in grid):
                valid_tables.append(table)
            else:
                print(f"Skipping non-table item: {table.get('captions', [])}")

        for idx, table in enumerate(valid_tables):
            table["index"] = idx

        outputs = []
        for idx, table in enumerate(valid_tables):
            table_ref = f"#/tables/{table.get('index', idx)}"
            table_index_in_body = next(
                (i for i, child in enumerate(body_children) if child.get("$ref") == table_ref),
                None
            )

            if table_index_in_body is None:
                print(f"Table {idx + 1} not found in body.children, skipping")
                continue

            prov = table.get("prov", [])
            page_numbers = sorted(set(p.get("page_no", 1) for p in prov)) if prov else [1]
            page_display = f"Pages {min(page_numbers)}-{max(page_numbers)}" if len(
                page_numbers) > 1 else f"Page {page_numbers[0]}" if page_numbers else "Page 1"

            title = extract_caption(table, body_children, table_index_in_body, texts)
            ref_id = None
            if title:
                match = re.match(r'^(TABLE|Table)\s*(\d+|I|II|III|IV|V|VI|VII|VIII|IX|X)', title, re.IGNORECASE)
                if match:
                    ref_id = f"{match.group(1)} {match.group(2)}"
            print(f"Table {idx + 1}: Using title: '{title}', ref_id: '{ref_id}'")

            roman_id = roman_numeral(idx + 1)
            table_ref_patterns = [
                rf"\b[Tt]able\s*{idx + 1}\b",
                rf"\b[Ss]ee\s*[Tt]able\s*{idx + 1}\b",
                rf"\b[Tt]he\s*[Tt]able\s*{idx + 1}\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Tt]able\s*{idx + 1}\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Tt]able\s*{idx + 1}\b",
                rf"\b[Tt]able\s*{roman_id}\b",
                rf"\b[Ss]ee\s*[Tt]able\s*{roman_id}\b",
                rf"\b[Tt]he\s*[Tt]able\s*{roman_id}\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Tt]able\s*{roman_id}\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Tt]able\s*{roman_id}\b",
            ]

            if ref_id:
                table_ref_patterns.append(rf"\b{re.escape(ref_id)}\b")

            chunks_before = []
            chunks_after = []
            for i, child in enumerate(body_children):
                if child.get("$ref", "").startswith("#/texts/"):
                    text_idx = int(child["$ref"].split("/")[-1])
                    text_content = texts[text_idx]["text"].strip()

                    if title and text_content.strip().lower() == title.strip().lower():
                        continue

                    if any(re.search(pattern, text_content, re.IGNORECASE) for pattern in table_ref_patterns):
                        if i < table_index_in_body:
                            chunks_before.append(text_content)
                        elif i > table_index_in_body:
                            chunks_after.append(text_content)

            try:
                grid = table["data"].get("grid", [])
                if grid:
                    table_data_preview = "\n".join(
                        "\t".join(get_cell_text(cell) for cell in row) for row in grid
                    )
                else:
                    table_data_preview = "[No table data could be extracted]"
            except Exception as e:
                table_data_preview = f"[Error extracting table data: {str(e)}]"

            description = generate_table_llm_description(chunks_before, chunks_after, title, table_data_preview)

            try:
                table_data = table["data"]["grid"]
                preview_data = [[get_cell_text(cell) for cell in row] for row in table_data]
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
