import openai
import json
from django.conf import settings


def analyze_user_question(user_question):
    prompt = f"""
    사용자가 Elasticsearch에 저장된 페이지에 대한 질문을 했습니다. 질문은 다음과 같습니다: "{user_question}"
    
    Elasticsearch 맵핑 구조는 다음과 같습니다:
    - `title` (문서 제목)
    - `author` (작성자)
    - `content` (본문)
    - `keywords` (키워드 리스트)
    - `created_at` (작성 날짜)
    
    이 질문이 문서 리스트 요청인지, 특정 정보에 대한 답변인지 구분하세요.
    1. 문서 리스트 요청이라면 적절한 Elasticsearch 쿼리를 생성하세요.
    2. 특정 정보 요청이라면 질문과 관련된 내용을 찾기 위해 Elasticsearch에 적절한 쿼리를 작성하고, 상위 5개의 결과를 분석하여 가장 관련성 있는 문서의 ID를 반환하는 형태로 응답을 작성하세요.
    """
    try:
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=500,
            temperature=0.5
        )
        return json.loads(response.choices[0].text.strip())
    except Exception as e:
        return {"error": f"Failed to get response from OpenAI: {str(e)}"}


def execute_es_query(query):
    es = settings.ELASTICSEARCH
    if not es:
        return {"error": "Elasticsearch client not configured"}

    try:
        response = es.search(index="pages", body=query)
        hits = response.get('hits', {}).get('hits', [])
        return hits
    except Exception as e:
        return {"error": f"Elasticsearch query failed: {str(e)}"}


def analyze_es_results(hits):
    # 상위 5개의 결과 분석
    top_hits = hits[:5]
    documents = [hit["_source"] for hit in top_hits]

    # GPT에게 가장 관련성 높은 문서를 찾도록 요청
    prompt = f"""
    사용자의 질문에 가장 관련이 있는 문서를 찾고 있습니다.
    질문: "{user_question}"
    
    다음은 5개의 관련 문서입니다:
    {json.dumps(documents, ensure_ascii=False, indent=4)}
    
    이 중에서 질문에 가장 관련성 높은 문서의 ID를 반환해주세요.
    """
    try:
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=50,
            temperature=0.5
        )
        document_id = response.choices[0].text.strip()
        return document_id
    except Exception as e:
        return {"error": f"Failed to analyze ES results: {str(e)}"}
