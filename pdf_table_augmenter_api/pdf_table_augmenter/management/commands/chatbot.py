from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def answer_question(question, table_description):
    prompt = f"""
            Based on the following table description:
            
            {table_description}
            
            Answer the question: {question}
            Provide a clear, concise response focused on insights from the table. If no relevant data, say so.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error answering question: {str(e)}"
