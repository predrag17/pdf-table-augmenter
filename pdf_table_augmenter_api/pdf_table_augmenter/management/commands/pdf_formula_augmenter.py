import os
import tempfile
import re

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

from pdf_table_augmenter.management.commands.reusable_functions_for_formula import extract_formula_caption, \
    generate_formula_llm_description, sanitize_latex
from pdf_table_augmenter.management.commands.reusable_functions_for_table import roman_numeral


def extract_formula_descriptions_from_file(file_obj):
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
        print(
            f"Document parsed: {len(doc.get('texts', []))} texts, {len(doc.get('body', {}).get('children', []))} body children")

        texts = doc.get("texts", [])
        body_children = doc.get("body", {}).get("children", [])

        valid_formulas = []
        for text_idx, text_item in enumerate(texts):
            label = text_item.get("label", "")

            if label == "formula":
                prov = text_item.get("prov", [])
                orig = text_item.get("orig", "").strip()
                latex = text_item.get("latex", "").strip()
                mathml = text_item.get("mathml", "").strip()
                text_content = text_item.get("text", "").strip()
                data = text_item.get("data", "").strip()

                is_valid = False
                if orig or latex or mathml:
                    is_valid = True
                elif text_content:
                    math_pattern = re.compile(r'[=\+\-\*/\\]\w|\{.*\}|\$.*\$|\\frac|\\sum|\\int|\\sqrt')
                    if math_pattern.search(text_content):
                        is_valid = True
                elif data:
                    math_pattern = re.compile(r'[=\+\-\*/\\]\w|\{.*\}|\$.*\$|\\frac|\\sum|\\int|\\sqrt')
                    if math_pattern.search(data):
                        is_valid = True

                if is_valid and prov and isinstance(prov, list) and len(prov) > 0:
                    text_item["text_idx"] = text_idx
                    valid_formulas.append(text_item)
                else:
                    print(f"Skipping invalid formula from text {text_idx + 1}: is_valid={is_valid}, prov={prov}")

        outputs = []
        for idx, formula in enumerate(valid_formulas):
            formula_ref = f"#/texts/{formula['text_idx']}"
            formula_index_in_body = next(
                (i for i, child in enumerate(body_children) if child.get("$ref") == formula_ref),
                None
            )

            if formula_index_in_body is None:
                continue

            prov = formula.get("prov", [])
            page_numbers = sorted(set(p.get("page_no", 1) for p in prov)) if prov else [1]
            page_display = f"Pages {min(page_numbers)}-{max(page_numbers)}" if len(
                page_numbers) > 1 else f"Page {page_numbers[0]}" if page_numbers else "Page 1"

            title = extract_formula_caption(formula, body_children, formula_index_in_body, texts)
            ref_id = None
            if title:
                match = re.match(
                    r'^(EQUATION|Equation|Eq\.?|FORMULA|Formula)\s*(\d+|I|II|III|IV|V|VI|VII|VIII|IX|X|\(\d+\))', title,
                    re.IGNORECASE)
                if match:
                    ref_id = f"{match.group(1)} {match.group(2)}".replace('(', '').replace(')', '')

            roman_id = roman_numeral(idx + 1)
            formula_ref_patterns = [
                rf"\b[Ee]quation\s*{idx + 1}\b",
                rf"\b[Ff]ormula\s*{idx + 1}\b",
                rf"\b[Ss]ee\s*[Ee]quation\s*{idx + 1}\b",
                rf"\b[Ss]ee\s*[Ff]ormula\s*{idx + 1}\b",
                rf"\b[Tt]he\s*[Ee]quation\s*{idx + 1}\b",
                rf"\b[Tt]he\s*[Ff]ormula\s*{idx + 1}\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Ee]quation\s*{idx + 1}\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Ff]ormula\s*{idx + 1}\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Ee]quation\s*{idx + 1}\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Ff]ormula\s*{idx + 1}\b",
                rf"\b[Ee]q\.?\s*{idx + 1}\b",
                rf"\b[Ee]q\.?\s*\({idx + 1}\)\b",
                rf"\b[Ff]ormula\s*\({idx + 1}\)\b",
                rf"\b[Ss]ee\s*[Ee]q\.?\s*{idx + 1}\b",
                rf"\b[Ss]ee\s*[Ff]ormula\s*\({idx + 1}\)\b",
                rf"\b[Tt]he\s*[Ee]q\.?\s*{idx + 1}\b",
                rf"\b[Tt]he\s*[Ff]ormula\s*\({idx + 1}\)\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Ee]q\.?\s*{idx + 1}\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Ff]ormula\s*\({idx + 1}\)\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Ee]q\.?\s*{idx + 1}\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Ff]ormula\s*\({idx + 1}\)\b",
                rf"\b[Ee]quation\s*{roman_id}\b",
                rf"\b[Ff]ormula\s*{roman_id}\b",
                rf"\b[Ss]ee\s*[Ee]quation\s*{roman_id}\b",
                rf"\b[Ss]ee\s*[Ff]ormula\s*{roman_id}\b",
                rf"\b[Tt]he\s*[Ee]quation\s*{roman_id}\b",
                rf"\b[Tt]he\s*[Ff]ormula\s*{roman_id}\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Ee]quation\s*{roman_id}\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Ff]ormula\s*{roman_id}\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Ee]quation\s*{roman_id}\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Ff]ormula\s*{roman_id}\b",
                rf"\b[Ee]q\.?\s*{roman_id}\b",
                rf"\b[Ee]q\.?\s*\({roman_id}\)\b",
                rf"\b[Ff]ormula\s*\({roman_id}\)\b",
                rf"\b[Ss]ee\s*[Ee]q\.?\s*{roman_id}\b",
                rf"\b[Ss]ee\s*[Ff]ormula\s*\({roman_id}\)\b",
                rf"\b[Tt]he\s*[Ee]q\.?\s*{roman_id}\b",
                rf"\b[Tt]he\s*[Ff]ormula\s*\({roman_id}\)\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Ee]q\.?\s*{roman_id}\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Ff]ormula\s*\({roman_id}\)\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Ee]q\.?\s*{roman_id}\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Ff]ormula\s*\({roman_id}\)\b",
            ]

            if ref_id:
                formula_ref_patterns.append(rf"\b{re.escape(ref_id)}\b")

            chunks_before = []
            chunks_after = []
            for i, child in enumerate(body_children):
                if child.get("$ref", "").startswith("#/texts/") and child.get("label") != "formula":
                    text_idx = int(child["$ref"].split("/")[-1])
                    text_content = texts[text_idx]["text"].strip()

                    if title and text_content.strip().lower() == title.strip().lower():
                        continue

                    if any(re.search(pattern, text_content, re.IGNORECASE) for pattern in formula_ref_patterns):
                        if i < formula_index_in_body:
                            chunks_before.append(text_content)
                        elif i > formula_index_in_body:
                            chunks_after.append(text_content)

            try:
                formula_preview = sanitize_latex(
                    formula.get("orig") or
                    formula.get("latex") or
                    formula.get("mathml") or
                    formula.get("text") or
                    formula.get("data") or
                    "\\text{No formula data}"
                )
            except Exception as e:
                formula_preview = f"\\text{{Error extracting formula data: {str(e)}}}"

            description = generate_formula_llm_description(chunks_before, chunks_after, title, formula_preview)

            outputs.append({
                "page": page_display,
                "equation_index": idx + 1,
                "description": description,
                "preview_data": formula_preview
            })

        print(f"Returning {len(outputs)} formula descriptions")
        return outputs

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return [{"error": f"Failed to process PDF: {str(e)}"}]

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
