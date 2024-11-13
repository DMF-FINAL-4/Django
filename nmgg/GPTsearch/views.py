from django.conf import settings
from django.http import JsonResponse
from .utils import analyze_user_question, execute_es_query, analyze_es_results
import openai


def handle_user_question(request):
    if request.method == 'POST':
        user_question = request.POST.get('question')
        if not user_question:
            return JsonResponse({'error': 'No question provided'}, status=400)

        # Step 1: Use GPT to analyze the question and generate the appropriate ES query
        analysis = analyze_user_question(user_question)

        if "error" in analysis:
            return JsonResponse(analysis, status=500)

        # Step 2: Execute the Elasticsearch query
        query = analysis.get("query")
        query_results = execute_es_query(query)

        if "error" in query_results:
            return JsonResponse(query_results, status=500)

        # Step 3: Process the Elasticsearch results based on question type
        if analysis.get("type") == "list":
            return JsonResponse({"query": query, "results": query_results}, status=200)
        elif analysis.get("type") == "info":
            # Analyze results and get the most relevant document ID
            relevant_doc_id = analyze_es_results(query_results)
            return JsonResponse({"relevant_document_id": relevant_doc_id}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
