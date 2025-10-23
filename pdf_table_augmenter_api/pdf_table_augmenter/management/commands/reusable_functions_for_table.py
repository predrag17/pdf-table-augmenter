import os
import re
import roman

from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def roman_numeral(n):
    try:
        return roman.toRoman(n).upper()
    except:
        return str(n)


def generate_table_llm_description(chunks_before, chunks_after, title=None, table_data_preview=None):
    prompt_parts = []

    if title:
        prompt_parts.append(f"Table Title:\n{title}\n")

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
            temperature=0.2,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating description: {str(e)}"


def get_cell_text(cell):
    return cell.get("text", "").strip() if isinstance(cell, dict) else str(cell).strip()


def extract_caption(table, body_children, table_index_in_body, texts):
    if table_index_in_body is None:
        return None

    caption = None
    captions = table.get("captions", [])

    if captions:
        if isinstance(captions, list) and captions:
            caption_item = captions[0]
            caption = caption_item.get("text", "").strip()
            if not caption and caption_item.get("$ref", "").startswith("#/texts/"):
                try:
                    text_idx = int(caption_item["$ref"].split("/")[-1])
                    if text_idx < len(texts):
                        caption = texts[text_idx]["text"].strip()
                except (ValueError, IndexError):
                    caption = None
        elif isinstance(captions, dict):
            caption = captions.get("text", "").strip()
            if not caption and captions.get("$ref", "").startswith("#/texts/"):
                try:
                    text_idx = int(captions["$ref"].split("/")[-1])
                    if text_idx < len(texts):
                        caption = texts[text_idx]["text"].strip()
                except (ValueError, IndexError):
                    caption = None

    if not caption:
        caption = table.get("caption", "").strip() or table.get("metadata", {}).get("caption", "").strip()

    if not caption and table_index_in_body is not None:
        search_range = 3
        for i in range(max(0, table_index_in_body - search_range),
                       min(len(body_children), table_index_in_body + search_range + 1)):
            if i == table_index_in_body:
                continue
            child = body_children[i]
            if child.get("$ref", "").startswith("#/texts/"):
                try:
                    text_idx = int(child["$ref"].split("/")[-1])
                    if text_idx < len(texts):
                        text_content = texts[text_idx]["text"].strip()
                        if re.match(r'^(TABLE|Table)\s*(\d+|I|II|III|IV|V|VI|VII|VIII|IX|X)', text_content,
                                    re.IGNORECASE):
                            caption = text_content
                            break
                except (ValueError, IndexError):
                    continue

    return caption


def generate_table_only_description(table_data_preview: str) -> str:
    cleaned_preview = "\n".join(line.strip() for line in table_data_preview.splitlines() if line.strip())

    if not cleaned_preview:
        return "No table data provided."

    prompt = f"""Describe the following table in 2–4 clear sentences based ONLY on the visible data.

        Table (tab-separated):
        {cleaned_preview}
        
        INSTRUCTIONS:
        - If the table has clear headers and meaningful rows → explain:
          • What the table shows
          • Key columns and their likely meaning
          • Main patterns or insights
          • Possible purpose
        
        - If the table is unclear, missing headers, has OCR errors, or lacks meaning → respond:
          "The table is unclear or incomplete. I cannot provide a reliable description without headers or context."
        
        Do NOT guess, invent, or assume missing information. Be honest and concise.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[LLM ERROR] {str(e)}"


def generate_table_with_context_description(
        before_text,
        after_text
):
    before_lines = [line.strip() for line in before_text.splitlines() if line.strip()]
    after_lines = [line.strip() for line in after_text.splitlines() if line.strip()]

    before_context = "\n".join(before_lines[-3:])
    after_context = "\n".join(after_lines[:3])

    if not before_context and not after_context:
        return "No surrounding text context available."

    prompt = f"""Describe the table below using the surrounding text for context. Use ONLY what is provided.
                
                TEXT BEFORE TABLE (up to 3 sentences):
                {before_context or "None"}
                
                TEXT AFTER TABLE (up to 3 sentences):
                {after_context or "None"}
                
                INSTRUCTIONS:
                - Write 2–4 clear sentences that:
                  • Explain what the table shows
                  • Use context to clarify column meanings or purpose
                  • Highlight key insights or trends
                  • State the table's role in the document
                
                - If context is vague, generic, or irrelevant → respond:
                  "The surrounding text does not provide meaningful context. Table description is limited to visible data only."
                
                - NEVER guess, invent, or assume. Be precise and honest.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[LLM ERROR] {str(e)}"
