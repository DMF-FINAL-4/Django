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

        pre_prompt = """
        아래는 정제된 웹 페이지의 HTML입니다. 이 HTML에서 다음 정보를 추출하여 **유효한 JSON 형식으로만 반환**하세요. 그 외 다른 텍스트나 설명은 포함하지 마세요.:
        - 접근권한 (access_permission): 만약 접근에 제한이 있는 페이지로 확인된다면 'HTTP 상태 코드', '없는 페이지', '로그인 필요' 등의 적절한 항목을 출력하고, 문제가 없다면 '정상'을 출력.
        - 파비콘 (favicon): 파비콘이 있다면 경로를 저장한다. png파일을 우선으로 한 개만 저장.
        - 호스트 도메인 (host_domain): 페이지의 호스트 도메인을 저장.
        - 호스트 이름 (host_name): 호스트의 이름을 한글로 출력하고, 한글이 없다면 영어로 출력. (예시: 네이버 뉴스, 페이스북, 위키백과)
        - 대체 URL (alternate_url): Canonical URL 또는 Open Graph URL이 존재한다면 이곳에 표시.
        - 제목 (title): 각종 정보를 종합한 제목을 출력. (예시: '동아일보｜[이철희 칼럼] 형제애로 마련한 400억…감사 전한 튀르키예')
        - 작성자 (author): 본문의 작성자를 출력. 찾을수 없다면 공란으로 남겨둡니다.
        - 작성일 (date): 페이지의 작성일을 `yyyy-MM-dd` 형식으로 출력.
        - 본문 (content): 본문 내용 전체를 가급적 그대로 출력.줄 바꿈은 \\n 으로 나타냄. 연속 줄바꿈은 최대 2번씩만. 만일 너무 길어서 줄여야한다면 반드시 (중략),(후략) 등의 생략 표기를 할것.
        - 짧은 요약 (short_summary): 본문을 한글로 20자에서 90자 사이로 요약.
        - 긴 요약 (long_summary): 본문을 한글로 200자에서 400자 사이로 요약.
        - 키워드 (keywords): 본문의 키워드들을 출력. 내용이 많고 주제가 폭넓다면 키워드가 많아짐. 키워드는 가급적 한단어로 나눠서 구성.
        - 유형 키워드 (category_keywords): 블로그, 카페, 기사, 정보, 사연, 에세이, 영상, 사진, 리뷰, 쇼핑, SNS, 커뮤니티, 자료실 등 그외 유형이라 할 수 있는 키워드들을 출력.
        - 댓글 (comments): 댓글을 찾아 예시의 형식에 따라 모두 저장.
        - 이미지 링크 (image_links): 본문 이미지를 예시의 형식에 따라 모두 저장.
        - 링크 (links): 본문 내에 주요한 외부 또는 내부 링크들이 있을 경우 예시의 형식에 따라 모두 저장.
        - 미디어 링크 (media_links): 본문 내에 비디오 및 오디오 등의 미디어가 있을 경우 예시의 형식에 따라 모두 저장.
        - 파일 다운로드 링크 (file_download_links): PDF, 이미지, 문서 등의 다운로드 링크가 있을 경우 예시의 형식에 따라 모두 저장.
        - 콘텐츠의 길이 (content_length): 본문을 읽는 데 걸리는 대략적인 시간을 분 단위로 출력. (예시: "2")

        유효한 JSON 형식:
        {{
            "access_permission": "정상",
            "favicon": "https://www.example.com/favicon.ico",
            "host_domain": "example.com",
            "host_name": "",
            "alternate_url": "https://www.example.com/page-url",
            "title": "제목",
            "author": "",
            "date": "yyyy-MM-dd",
            "content": "",
            "short_summary": "",
            "long_summary": "",
            "keywords": ["키워드1", "키워드2"],
            "category_keywords": ["블로그", "카페"],
            "comments": [
                {{
                    "author": "작성자1",
                    "content": "댓글내용1",
                    "date": "yyyy-MM-dd"
                }},
                {{
                    "author": "작성자2",
                    "content": "댓글내용2",
                    "date": "yyyy-MM-dd"
                }}
            ],
            "image_links": [
                {{
                    "caption": "이미지캡션1",
                    "url": "https://example.com/image1.jpg"
                }},
                {{
                    "caption": "이미지캡션2",
                    "url": "https://example.com/image2.jpg"
                }}
            ],
            "links": [
                {{
                    "caption": "캡션1",
                    "url": "https://example.com/link1.html"
                }},
                {{
                    "caption": "캡션2",
                    "url": "https://example.com/link2.html"
                }}
            ],
            "media": [
                {{
                    "caption": "캡션1",
                    "url": "https://example.com/video1.mp4"
                }},
                {{
                    "caption": "캡션2",
                    "url": "https://example.com/audio1.mp3"
                }}
            ],
            "file_download_links": [
                {{
                    "caption": "파일제목1",
                    "size": "10MB",
                    "url": "https://example.com/file1.pdf"
                }},
                {{
                    "caption": "파일제목2",
                    "size": "1.1GB",
                    "url": "https://example.com/file2.zip"
                }}
            ],
            "content_length": m
        }}

        정보를 추출할 HTML:
        \"\"\"
        html전문
        \"\"\"

        """



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
        사용자가 저장한 페이지들이 있는 Elasticsearch 5.3.3의 인덱스에서 사용자의 요청에 따라 관련 웹페이지 문서 항목을 찾으려고 합니다.
        다음의 안내에 따라 **유효한 JSON 형식으로만 반환하세요**
        사용자 요청을 분석하여 사용자가 요구하는것이 '요청에 응답이나 대답을 요청 하는것'('info')인지, '요청 관련 문서의 목록을 보고싶은것'('list')인지 분류합니다.
        검색결과가 최대한 많이 나올수 있도록 사용자의 요청을 분석하여 검색어를 최대한 풍부하게 확장 합니다.(확장 예시: '도람뿌 인가 로날드 인가 하는 사람' -> 도날드 트럼프, Donald John Trump, 미국 대통령. '프로그래밍 언어 관련' -> 파이썬, python, 자바스크립트, javascript, js, java, 등. '노란과일' -> 배, 바나나, 두리안, 골든키위 등.)**
        

        참고사항:
        Write a valid Elasticsearch query to match documents:
        1. Avoid common errors like adding unexpected keys inside the `bool` query or omitting arrays for `must` and `filter`.
        2. Validate the query structure to ensure it is properly formatted for Elasticsearch.
        3. Provide an explanation if specific parts of the query could cause errors.
        4. The output should follow the JSON format without any syntax errors.
        Generate a valid Elasticsearch query and validate it against the following checks:
        1. All keys inside the `bool` query (`must`, `should`, `filter`) should be arrays.
        2. Ensure there are no unexpected keys inside `bool`.
        3. Use only valid Elasticsearch Query DSL syntax for version 7.x.


        
        사용자 요청: "{user_question}"
        인덱스의 mapping: {index_mapping}
        이것은 Elasticsearch에 문서가 저장될때 분석하기 위해 사용된 프롬프트 입니다. 이것을 참고하여 적확한 쿼리를 만들어주세요: {pre_prompt}


        반드시 지켜야 할 유효한 JSON 응답 형식:
        {{
            "question_type": "list"또는"info",
            "query": Elasticsearch 5.3.3 버전에서 올바르게 작동하는 엘라스틱 서치 query
        }}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o",
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