import os
import tempfile
import re

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from pdf_table_augmenter.management.commands.reusable_functions import extract_caption, roman_numeral, \
    generate_image_llm_description


def extract_image_descriptions_from_file(file_obj):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_obj.read())
        tmp_path = tmp.name

    try:
        pipeline_options = PdfPipelineOptions(
            do_ocr=True,
            do_table_structure=False,
            generate_page_images=True,
            generate_picture_images=True,
        )
        converter = DocumentConverter(format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        })

        result = converter.convert(tmp_path)
        doc = result.document.export_to_dict()
        print(doc)
        print(f"Document parsed: {len(doc.get('texts', []))} texts, {len(doc.get('pictures', []))} images")

        texts = doc.get("texts", [])
        body_children = doc.get("body", {}).get("children", [])

        valid_images = []
        for image in doc.get("figures", []):
            prov = image.get("prov", [])
            if prov and isinstance(prov, list) and len(prov) > 0:
                valid_images.append(image)
            else:
                print(f"Skipping invalid image: {image.get('captions', [])}")

        for idx, image in enumerate(valid_images):
            image["index"] = idx

        outputs = []
        for idx, image in enumerate(valid_images):
            image_ref = f"#/figures/{image.get('index', idx)}"
            image_index_in_body = next(
                (i for i, child in enumerate(body_children) if child.get("$ref") == image_ref),
                None
            )

            if image_index_in_body is None:
                print(f"Image {idx + 1} not found in body.children, skipping")
                continue

            prov = image.get("prov", [])
            page_numbers = sorted(set(p.get("page_no", 1) for p in prov)) if prov else [1]
            page_display = f"Pages {min(page_numbers)}-{max(page_numbers)}" if len(
                page_numbers) > 1 else f"Page {page_numbers[0]}" if page_numbers else "Page 1"

            title = extract_caption(image, body_children, image_index_in_body, texts)
            ref_id = None
            if title:
                match = re.match(r'^(FIGURE|Figure|Fig\.?)\s*(\d+|I|II|III|IV|V|VI|VII|VIII|IX|X)', title,
                                 re.IGNORECASE)
                if match:
                    ref_id = f"{match.group(1)} {match.group(2)}"
            print(f"Image {idx + 1}: Using title: '{title}', ref_id: '{ref_id}'")

            roman_id = roman_numeral(idx + 1)
            image_ref_patterns = [
                rf"\b[Ff]igure\s*{idx + 1}\b",
                rf"\b[Ff]ig\.?\s*{idx + 1}\b",
                rf"\b[Ss]ee\s*[Ff]igure\s*{idx + 1}\b",
                rf"\b[Ss]ee\s*[Ff]ig\.?\s*{idx + 1}\b",
                rf"\b[Tt]he\s*[Ff]igure\s*{idx + 1}\b",
                rf"\b[Tt]he\s*[Ff]ig\.?\s*{idx + 1}\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Ff]igure\s*{idx + 1}\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Ff]ig\.?\s*{idx + 1}\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Ff]igure\s*{idx + 1}\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Ff]ig\.?\s*{idx + 1}\b",
                rf"\b[Ff]igure\s*{roman_id}\b",
                rf"\b[Ff]ig\.?\s*{roman_id}\b",
                rf"\b[Ss]ee\s*[Ff]igure\s*{roman_id}\b",
                rf"\b[Ss]ee\s*[Ff]ig\.?\s*{roman_id}\b",
                rf"\b[Tt]he\s*[Ff]igure\s*{roman_id}\b",
                rf"\b[Tt]he\s*[Ff]ig\.?\s*{roman_id}\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Ff]igure\s*{roman_id}\b",
                rf"\b[Aa]s\s*shown\s*in\s*[Ff]ig\.?\s*{roman_id}\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Ff]igure\s*{roman_id}\b",
                rf"\b[Aa]s\s*illustrated\s*in\s*[Ff]ig\.?\s*{roman_id}\b",
            ]

            if ref_id:
                image_ref_patterns.append(rf"\b{re.escape(ref_id)}\b")

            chunks_before = []
            chunks_after = []
            for i, child in enumerate(body_children):
                if child.get("$ref", "").startswith("#/texts/"):
                    text_idx = int(child["$ref"].split("/")[-1])
                    text_content = texts[text_idx]["text"].strip()

                    if title and text_content.strip().lower() == title.strip().lower():
                        continue

                    if any(re.search(pattern, text_content, re.IGNORECASE) for pattern in image_ref_patterns):
                        if i < image_index_in_body:
                            chunks_before.append(text_content)
                        elif i > image_index_in_body:
                            chunks_after.append(text_content)

            try:
                metadata = image.get("metadata", {})
                if metadata:
                    image_metadata = "\n".join(f"{key}: {value}" for key, value in metadata.items())
                else:
                    image_metadata = "[No image metadata available]"
            except Exception as e:
                image_metadata = f"[Error extracting image metadata: {str(e)}]"

            description = generate_image_llm_description(chunks_before, chunks_after, title, image_metadata)

            preview_data = []

            outputs.append({
                "page": page_display,
                "image_index": idx + 1,
                "description": description,
                "preview_data": preview_data
            })

        print(f"Returning {len(outputs)} image descriptions")
        return outputs

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return [{"error": f"Failed to process PDF: {str(e)}"}]

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
