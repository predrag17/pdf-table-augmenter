import os
import tempfile

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from pdf_table_augmenter.management.commands.reusable_functions_for_table import (
    get_cell_text,
    generate_table_with_context_description
)


def extract_table_with_context_descriptions_from_file(file_obj):
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
        tables = doc.get("tables", [])

        valid_tables = []
        for table in tables:
            grid = table.get("data", {}).get("grid", [])
            if grid and isinstance(grid, list) and len(grid) > 0 and any(len(row) > 0 for row in grid):
                valid_tables.append(table)

        for idx, table in enumerate(valid_tables):
            table["index"] = idx

        outputs = []

        for idx, table in enumerate(valid_tables):
            table_ref = f"#/tables/{table['index']}"
            table_index_in_body = next(
                (i for i, child in enumerate(body_children) if child.get("$ref") == table_ref),
                None
            )
            if table_index_in_body is None:
                print(f"Table {idx + 1} not in body, skipping")
                continue

            chunks_before = []
            for j in range(table_index_in_body - 1, max(table_index_in_body - 4, -1), -1):
                child = body_children[j]
                if child.get("$ref", "").startswith("#/texts/"):
                    try:
                        text_idx = int(child["$ref"].split("/")[-1])
                        text = texts[text_idx]["text"].strip()
                        if text:
                            chunks_before.append(text)
                            if len(chunks_before) >= 3:
                                break
                    except (IndexError, ValueError):
                        continue
            chunks_before = chunks_before[-3:]

            chunks_after = []
            for j in range(table_index_in_body + 1, min(table_index_in_body + 4, len(body_children))):
                child = body_children[j]
                if child.get("$ref", "").startswith("#/texts/"):
                    try:
                        text_idx = int(child["$ref"].split("/")[-1])
                        text = texts[text_idx]["text"].strip()
                        if text:
                            chunks_after.append(text)
                            if len(chunks_after) >= 3:
                                break
                    except (IndexError, ValueError):
                        continue
            chunks_after = chunks_after[:3]

            if not chunks_before and not chunks_after:
                try:
                    df = table["data"].export_to_dataframe()
                    preview_rows = df.head(3).to_string(index=False)
                    chunks_before = [f"Table preview:\n{preview_rows}"]
                except Exception:
                    chunks_before = ["[No context or preview available]"]

            prov = table.get("prov", [])
            page_numbers = sorted(set(p.get("page_no", 1) for p in prov)) if prov else [1]
            page_display = (
                f"Pages {min(page_numbers)}-{max(page_numbers)}"
                if len(page_numbers) > 1
                else f"Page {page_numbers[0]}"
            )

            try:
                grid = table["data"]["grid"]
                preview_data = [[get_cell_text(cell) for cell in row] for row in grid]
            except Exception:
                preview_data = []

            description = generate_table_with_context_description(
                before_text="\n".join(chunks_before),
                after_text="\n".join(chunks_after)
            )

            outputs.append({
                "page": page_display,
                "table_index": idx + 1,
                "description": description,
                "preview_data": preview_data
            })

        print(f"Returning {len(outputs)} table descriptions (3 before + 3 after)")
        return outputs

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return [{"error": f"Failed to process PDF: {str(e)}"}]

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
