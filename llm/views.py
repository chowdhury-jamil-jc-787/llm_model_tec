import os
import json
import tempfile
import pandas as pd
import uuid 

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from openai import OpenAI
from llm.utils.sql_runner import run_sql_on_laravel_db  # ← your existing DB executor


def get_schema_text():
    schema_path = os.path.join(settings.BASE_DIR, "schema.txt")
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            return f.read()
    return "No schema found."


class PromptAPIView(APIView):
    def post(self, request):
        user_prompt = request.data.get("prompt")
        if not user_prompt:
            return Response({"error": "Prompt is required."}, status=400)

        try:
            client = OpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1"
            )

            schema = get_schema_text()

            # Optional few-shot examples (improves accuracy)
            example_prompt = """
Q: How many sales orders?
A: SELECT COUNT(*) FROM sales_orders;

Q: What is total order value?
A: SELECT SUM(order_value) FROM sales_orders;
            """

            full_prompt = f"""
{example_prompt}

Database Schema:
{schema}

User Question:
{user_prompt}

Return only a valid SQL query based on this schema.
"""

            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=200
            )

            raw_reply = response.choices[0].message.content.strip()

            # Basic cleaning in case of markdown or extra lines
            sql_query = raw_reply.strip("`").strip()
            if "```sql" in sql_query:
                sql_query = sql_query.split("```sql")[1].split("```")[0].strip()

            # Execute SQL
            try:
                results = run_sql_on_laravel_db(sql_query)

                if "excel" in user_prompt.lower():
                    df = pd.DataFrame(results)
                    # Make sure media folder exists
                    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

                    filename = f"tmp_{uuid.uuid4().hex[:8]}.xlsx"
                    filepath = os.path.join(settings.MEDIA_ROOT, filename)

                    df.to_excel(filepath, index=False)

                    download_url = f"http://{request.get_host()}/media/{filename}"

                    return Response({"excel_url": download_url})

                return Response({"query": sql_query, "result": results})

            except Exception as db_error:
                return Response({"error": f"SQL error: {str(db_error)}", "query": sql_query}, status=500)

        except Exception as llm_error:
            return Response({"error": f"LLM error: {str(llm_error)}"}, status=500)
