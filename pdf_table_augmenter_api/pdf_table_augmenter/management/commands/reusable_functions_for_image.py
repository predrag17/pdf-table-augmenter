import os

from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def generate_image_llm_description(chunks_before, chunks_after, title=None, image_metadata=None):
    prompt_parts = []

    if title:
        prompt_parts.append(f"Image Title:\n{title}\n")

    if chunks_before or chunks_after:
        if chunks_before:
            prompt_parts.append("Context Before the Image:\n" + "\n".join(chunks_before) + "\n")
        if chunks_after:
            prompt_parts.append("Context After the Image:\n" + "\n".join(chunks_after) + "\n")

    if image_metadata:
        prompt_parts.append(
            "Image Metadata (if available):\n" + image_metadata + "\n"
        )

    prompt_parts.append(
        "Based on the provided context or image metadata, provide a clear and concise description "
        "of what this image represents. Focus on the purpose, contents, and insights "
        "the image might provide. Ensure the description is coherent and relevant to the provided information."
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
