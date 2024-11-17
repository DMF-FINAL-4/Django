#GPTsearch/utils.py

import openai
from elasticsearch import Elasticsearch
from django.conf import settings
from django.http import JsonResponse
import json

# GPT를 사용해 질문을 분석하고 적절한 ES 쿼리를 생성하는 함수
def analyze_user_question(user_question, index_name):
    try:
        openai.api_key = settings.OPENAI_API_KEY

        if index_name == "pages":
            index_mapping = """
                "mappings": {
                    "properties": {
                    "access_permission": {
                        "type": "keyword"
                    },
                    "favicon": {
                        "type": "keyword"
                    },
                    "host_domain": {
                        "type": "keyword"
                    },
                    "host_name": {
                        "type": "text",
                        "analyzer": "korean_analyzer",
                        "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                        }
                    },
                    "alternate_url": {
                        "type": "keyword"
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "korean_analyzer",
                        "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                        }
                    },
                    "author": {
                        "type": "text",
                        "analyzer": "korean_analyzer",
                        "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                        }
                    },
                    "date": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "korean_analyzer"
                    },
                    "short_summary": {
                        "type": "text",
                        "analyzer": "korean_analyzer"
                    },
                    "long_summary": {
                        "type": "text",
                        "analyzer": "korean_analyzer"
                    },
                    "keywords": {
                        "type": "keyword"
                    },
                    "category_keywords": {
                        "type": "keyword"
                    },
                    "comments": {
                        "type": "nested",
                        "properties": {
                        "author": {
                            "type": "text",
                            "analyzer": "korean_analyzer",
                            "fields": {
                            "raw": {
                                "type": "keyword"
                            }
                            }
                        },
                        "content": {
                            "type": "text",
                            "analyzer": "korean_analyzer"
                        },
                        "date": {
                            "type": "date",
                            "format": "yyyy-MM-dd"
                        }
                        }
                    },
                    "image_links": {
                        "type": "nested",
                        "properties": {
                        "caption": {
                            "type": "text",
                            "analyzer": "korean_analyzer"
                        },
                        "url": {
                            "type": "keyword"
                        }
                        }
                    },
                    "links": {
                        "type": "nested",
                        "properties": {
                        "caption": {
                            "type": "text",
                            "analyzer": "korean_analyzer"
                        },
                        "url": {
                            "type": "keyword"
                        }
                        }
                    },
                    "media": {
                        "type": "nested",
                        "properties": {
                        "caption": {
                            "type": "text",
                            "analyzer": "korean_analyzer"
                        },
                        "url": {
                            "type": "keyword"
                        }
                        }
                    },
                    "file_download_links": {
                        "type": "nested",
                        "properties": {
                        "caption": {
                            "type": "text",
                            "analyzer": "korean_analyzer"
                        },
                        "size": {
                            "type": "keyword"
                        },
                        "url": {
                            "type": "keyword"
                        }
                        }
                    },
                    "content_length": {
                        "type": "integer"
                    }
                    }
                }
            """
        elif index_name == "history":
            index_mapping = """
                "mappings": {
                    "properties": {
                    "url": {
                        "type": "keyword"
                    },
                    "favicon": {
                        "type": "keyword"
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "korean-analyzer"
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "korean-analyzer"
                    }
                    }
                }
            """
        else:
            return JsonResponse({'error': 'Invalid index type provided.'}, status=400)
        # 'list'일 경우 사용자 요청에 '인덱스의 mapping'에 적합한 query를 생성하세요.
        # 'info'일 경우 쿼리를 통해 Elasticsearch에 검색한 후 상위 5개 결과를 다시 분석할 예정이니 이후 절차를 고려하여 사용자의 요청에 응답하기 적절하도록 query를 구성하시오.
        prompt = f"""
        사용자가 저장한 페이지들이 있는 Elasticsearch 인덱스에서 사용자의 요청에 따라 관련 웹페이지 문서 항목을 찾으려고 합니다.
        다음의 안내에 따라 **유효한 JSON 형식으로만 반환하세요**
        사용자 요청을 분석하여 사용자가 요구하는것이 '요청에 응답이나 대답을 요청 하는것'('info')인지, '요청 관련 문서의 목록을 보고싶은것'('list')인지 분류합니다.
        검색결과가 최대한 많이 나올수 있도록 사용자의 요청을 분석하여 검색어를 최대한 풍부하게 확장 합니다.(확장 예시: '도람뿌 인가 로날드 인가 하는 사람' -> 도날드 트럼프, Donald John Trump, 미국 대통령. '프로그래밍 언어 관련' -> 파이썬, python, 자바스크립트, javascript, js, java, 등. '노란과일' -> 배, 바나나, 두리안, 골든키위 등.)**
        
        
        사용자 요청: "{user_question}"
        인덱스의 mapping: {index_mapping}


        반드시 지켜야 할 유효한 JSON 응답 형식:
        {{
            "question_type": "list"또는"info",
            "query": json형식의 엘라스틱 서치 query
        }}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 Elasticsearch query 생성기 입니다. 프롬프트의 안내에 따라 유효한 JSON 형식으로 반환하세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=10000,
            timeout=30
        )
        response_body = response['choices'][0]['message']['content'].strip()
        return response_body

    except Exception as e:
        return {"error": f"Failed to analyze question: {str(e)}"}

# Elasticsearch에서 쿼리를 실행하는 함수
def execute_es_query(query, index_name):
    try:
        es = settings.ELASTICSEARCH
        if not es.ping():
            raise ValueError("Elasticsearch connection failed")

        response = es.search(index=index_name, body=query)
        hits = response.get('hits', {}).get('hits', [])
        results = []
        for hit in hits:
            source = hit['_source']
            document_id = hit['_id']
            highlight = hit.get('highlight', {})
            results.append({
                "id": document_id,
                "source": source,
                "highlight": highlight
            })
        return results

    except Exception as e:
        return {"error": f"Failed to execute Elasticsearch query: {str(e)}"}

# Elasticsearch 결과를 분석하여 가장 관련성 있는 문서 ID를 찾는 함수
def analyze_es_results(query_results, user_question):
    try:
        openai.api_key = settings.OPENAI_API_KEY

        # 검색 결과 상위 5개 추출
        top_5_query_results = query_results[:5]

        prompt = f"""
        사용자 요청에 대해 Elasticsearch 검색결과 상위 5개를 분석하고 적절한 답변을 제공합니다.
        사용자 요청에 적절한 답변을 자료검색 서포터로서 답변하시오
        예를 들어 '물어보신 무엇무엇은 무엇무엇입니다, 찾으시는 내용은 무엇무엇에 관한 내용인것 같습니다, 문서 무엇무엇(문서의 제목)에 이러이러한 내용이 있습니다, 요청하신 요약은 이러이러합니다' 와 같이 간결하고 명확하게 서포팅해. 너무 그대로 따라하지는 말고. 가급적 짧게 답변하고 긴 답변이 필요하더라도 최대 400자 이내로
        그리고 요청과 가장 관련있는 검색결과의 id를 한개를 출력하세요. 만약 질문과 매우 밀접한 관련항목이 여러개라면 id 최대 3개를 출력하세요.
        
        사용자 요청: "{user_question}"
        검색 결과: ```{json.dumps(top_5_query_results, ensure_ascii=False, indent=4)}```
        
        반드시 지켜야 할 최종 응답 형식:
        {{
            "answer": "사용자 요청에 대한 답변 문자열",
            "rel_ids": [ "id1", "id2", "id3" ]
        }}
        """

        response = openai.Completion.create(
            engine="gpt-4o-mini",
            prompt=prompt,
            max_tokens=500,
            temperature=0.5
        )
        response_body = response.choices[0].text.strip()
        return json.loads(response_body)

    except Exception as e:
        return {"error": f"Failed to analyze question: {str(e)}"}



def GPT_to_json(extracted_info):
    try:

        start = extracted_info.find('{')
        end = extracted_info.rfind('}')

        # '{'와 '}'가 모두 존재하고, '{'가 '}'보다 앞에 있을 때
        if start != -1 and end != -1 and start < end:
            extracted_info = extracted_info[start:end+1]
            processed_data = json.loads(extracted_info)
        else:
            raise ValueError(f"GPT 응답이 유효한 JSON 형식이 아닙니다: {str(e)}")
        print('백틱 점검완료')
        # if extracted_info.startswith('```') and extracted_info.endswith('```'):
        #     extracted_info = extracted_info[3:-3].strip()
        # processed_data = json.loads(extracted_info)
        if 'date' in processed_data:
            if not re.match(r'\d{4}-\d{2}-\d{2}', processed_data['date']):
                processed_data['date'] = '0001-01-01'
        return processed_data

    except json.JSONDecodeError as e:
        raise ValueError(f"GPT 응답이 유효한 JSON 형식이 아닙니다: {str(e)}")



def transform_data(original_data):
    transformed_data = []
    for item in original_data:
        new_item = {
            'id': item['id'],
            **item['source']  # source 딕셔너리의 모든 키-값 쌍을 새 딕셔너리에 추가
        }
        transformed_data.append(new_item)
    return transformed_data