import os
import tempfile

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from pdf_table_augmenter.management.commands.reusable_functions_for_table import (
    get_cell_text,
    generate_table_only_description
)


def extract_table_data_only_descriptions_from_file(file_obj):
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

            description = generate_table_only_description(table_data_preview)

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

        print(f"Returning {len(outputs)} table descriptions (CASE 1: Table-Only)")
        return outputs

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return [{"error": f"Failed to process PDF: {str(e)}"}]

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
