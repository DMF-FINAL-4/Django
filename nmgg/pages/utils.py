# utils.py

from django.conf import settings # import openai_api_key, ELASTICSEARCH
from dotenv import load_dotenv 

from elasticsearch import Elasticsearch, TransportError, ConnectionError, NotFoundError
from elasticsearch.exceptions import NotFoundError, RequestError

from bs4 import BeautifulSoup
import os
import argparse
import openai
import json
import re
import requests



def classify_request(request):
    if request['url'] and request['html']:
        if not request['duplicates']:
            url = request['url']  #
            es_res = search_page_by_tkm('url', url, 'term')
            # 검색결과가 있으면 결과 반환 없으면 return False
            if es_res.get('hits', {}).get('total', {}).get('value', 0) > 0:
                hits = es_res.get('hits', {}).get('hits', [])
                results = [{"id": hit.get("_id"), **hit.get("_source", {})} for hit in hits]
                return results
        return False
    else:
        raise ValueError("URL and HTML are required")  # 구체적인 예외 추가



class HTMLSummariz:

    def __init__(self):
        # API 키를 초기화합니다.
        openai_api_key = settings.OPENAI_API_KEY
        if not openai_api_key:
            raise ValueError("API key not found")

        openai.api_key = openai_api_key
        print('OPENAI_API_KEY 등록')
        print('html 정보 추출 클래스 인스턴스 생성')

    def clean_html_style_tags(self, raw_html_content):
        """
        HTML 콘텐츠를 정제하여 스타일 및 장식적인 태그와 관련 속성만 제거하고 구조적인 태그는 그대로 유지합니다.
        Args: raw_html_content (str): 정제할 HTML 콘텐츠
        Returns: str: 정제된 HTML 콘텐츠
        """
        try:
            print('태그 정돈 시작')
            # BeautifulSoup 객체 생성 (lxml 파서 사용)
            soup = BeautifulSoup(raw_html_content, 'lxml')
            # 제거할 태그 리스트 (스타일 및 장식적인 태그)
            tags_to_remove = ['style', 'script', 'aside', 'nav', 'footer', 'header', 'iframe', 'noscript', 'form']
            # 태그와 그 내용을 완전히 제거
            for tag in tags_to_remove:
                for element in soup.find_all(tag):
                    element.decompose()
            # 제거할 속성 리스트 (스타일 관련 속성)
            attributes_to_remove = ['style', 'class', 'id']
            # 모든 태그 순회
            for tag in soup.find_all(True):
                for attr in attributes_to_remove:
                    if attr in tag.attrs:
                        del tag.attrs[attr]
            # 정제된 HTML 문자열 반환
            cleaned_html = str(soup)
            print('태그 정돈 완료')
            return cleaned_html

        except Exception as e:
            raise RuntimeError(f"HTML 태그 정제 중 오류 발생: {str(e)}")

    def extract_information_with_gpt(self, cleaned_html):
        """
        정제된 HTML을 받아서 특정 정보를 GPT-4 모델로 요약 정리합니다.
        Args: cleaned_html (str): 정제된 HTML 콘텐츠
        Returns:dict: GPT가 추출한 정보
        """
        print('GPT 정돈 시작')
        # 프롬프트 정의
        prompt = f"""
        아래는 정제된 웹 페이지의 HTML입니다. 이 HTML에서 다음 정보를 추출하여 이 HTML에서 다음 정보를 꼭 **유효한 JSON 형식으로만 백틱 없이 반환하세요**. 다른 텍스트나 설명은 포함하지 마세요.:
        - 접근권한 (access_permission) : 만약 접근에 제한이 있는 페이지로 확인된다면 'HTTP 상태 코드', '없는 페이지', '로그인 필요' 등의 적절한 항목을 출력. 문제가 없다면 '정상'을 출력
        - 파비콘(favicon) : 파비콘의 호스트 도메인을 포함한 전체 경로를 저장, 민약 여러개라면 가장 큰 이미지의 것을 1개만 저장
        - 호스트 도메인 (host_domain) :
        - 호스트 이름 (host_name) : 호스트의 이름을 한글로 출력, 한글이 없다면 영어로 출력 (예시: 네이버 뉴스, 페이스북, 위키백과)
        - 대체 url (alternate_url) : Canonical URL 또는 Open Graph URL이 존재 한다면 이곳에 표시
        - 제목 (title) : 각종 정보를 종합한 제목 (예시: '동아일보｜[이철희 칼럼] 형제애로 마련한 400억…감사 전한 튀르키예')
        - 작성자 (author) : 본문의 작성자
        - 작성일 (date) : 페이지의 작성일 yyyy-MM-dd
        - 본문 (content) : 명백한 오타 수정을 제외한 텍스트 외곡이 없으며, 표 내부의 내용 등을 포함한 누락 없는 본문
        - 짧은 요약 (short_summary) : 본문을 20자에서 90자로 사이로 요약
        - 긴 요약 (long_summary) : 본문을 200자에서 400자로 요약
        - 키워드 (keywords) : 본문의 키워드들 내용이 길고 요소가 많다면 키워드들이 아주 많아져도 좋아
        - 유형 키워드 (category_keywords) : 블로그, 카페, 기사, 정보, 사연, 에세이, 영상, 사진, 리뷰, 쇼핑, sns 등 유형이라 할 수 있는 키워드들 풍부하게
        - 댓글 (comments) : 댓글이 있다면 '작성자 | 댓글내용 | 작성시간' 형식으로 저장
        - 이미지 링크 (image_links) : 주요 이미지를 모두 링크 주소 {{"이미지캡션" : "이미지링크url"}} 딕셔너리 형식으로 저장
        - 링크(links) : 본문 내에 주요한 외부 또는 내부 링크들이 있을경우 {{"캡션" : "링크url"}} 딕셔너리 형식으로 저장
        - 비디오 및 오디오(media) : 본문 내에 미디어가 있을경우 {{"캡션" : "링크url"}} 딕셔너리 형식으로 저장
        - 파일 다운로드 링크(file_download_links) : 주요한 PDF, 이미지, 문서 등의 다운로드 링크가 있을경우 {{"파일제목 | 파일 크기": "링크url"}} 딕셔너리 형식으로 저장
        - 콘텐츠의 길이(content_length) : 콘텐츠를 읽는데 걸리는 시간을 예측 1분 단위로

        HTML:
        \"\"\"
        {cleaned_html}
        \"\"\"

        JSON 형식 예시:
        {{
            "access_permission": "정상",
            "favicon" : "https://www.example.com/favicon.ico",
            "host_domain": "example.com",
            "host_name": "네이버 뉴스",
            "alternate_url": "https://www.example.com/page-url",
            "title": "제목",
            "author": "작성자",
            "date": "yyyy-MM-dd",
            "content": "본문 내용",
            "short_summary": "본문을 20자에서 90자로 요약한 내용",
            "long_summary": "본문을 200자에서 400자로 요약한 내용",
            "keywords": ["키워드1", "키워드2"],
            "category_keywords": ["블로그", "카페"],
            "comments": ["작성자1 | 댓글내용1 | yyyy-MM-dd", "작성자2 | 댓글내용2 | yyyy-MM-dd"],
            "image_links": {{"이미지캡션1": "https://example.com/image1.jpg", "이미지캡션2": "https://example.com/image2.jpg" }},
            "links": {{"캡션1": "https://example.com/image1.jpg", "캡션2": "https://example.com/image2.jpg" }},
            "media_links": {{"캡션1": "https://example.com/image1.jpg", "캡션2": "https://example.com/image2.jpg" }},
            "file_download_links": {{"캡션1 | 10MB": "https://example.com/image1.jpg", "캡션2 | 1.1GB": "https://example.com/image2.jpg" }},
            "content_length": "m"
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 정보를 추출하는 어시스턴트입니다. 규칙에 따라 유효한 JSON 형식으로만 백틱 없이 반환하세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=10000,
                timeout=30
            )
            extracted_info = response['choices'][0]['message']['content'].strip()
            print('GPT 정돈완료')
            print(extracted_info)
            return extracted_info

        except Exception as e:
            raise RuntimeError(f"GPT 요약 중 오류 발생: {str(e)}")

    def GPT_to_json(self, extracted_info):
        # 백틱 제거, JSON 로드, date 형식 검증
        try:
            if extracted_info.startswith('```') and extracted_info.endswith('```'):
                extracted_info = extracted_info[3:-3].strip()
            processed_data = json.loads(extracted_info)
            if 'date' in processed_data:
                if not re.match(r'\d{4}-\d{2}-\d{2}', processed_data['date']):
                    processed_data['date'] = '0001-01-01'
            print(processed_data)
            return processed_data

        except json.JSONDecodeError as e:
            print('GPT 응답이 유효한 JSON 형식이 아닙니다.')
            raise ValueError(f"GPT 응답이 유효한 JSON 형식이 아닙니다: {str(e)}")


    def process(self, raw_html):
        """
        정제되지 않은 HTML을 받아 클리닝하고 GPT 모델로 정보를 추출합니다.
        Args: raw_html (str): 처리할 HTML 콘텐츠
        Returns: dict: 추출된 정보
        """
        try:
            cleaned_html = self.clean_html_style_tags(raw_html)
            extracted_info = self.extract_information_with_gpt(cleaned_html)
            processed_data = self.GPT_to_json(extracted_info)
            print('process 완료')
            return processed_data
        except Exception as e:
            return {"error": "알 수 없는 오류 발생", "details": str(e)}


def upload_to_elasticsearch(processed_json,index='pages',pipeline='add_created_at'):
    # Elasticsearch에 데이터 업로드
    print("Elasticsearch에 데이터 업로드 시도")
    try:
        es = settings.ELASTICSEARCH
        if not es:
            print("Elasticsearch 클라이언트가 설정되지 않음")
            raise RuntimeError('Elasticsearch client not configured')
    
        try:
            res = es.index(index=index, pipeline=pipeline, body=processed_json)
            print('업로드 완료 res')
            # 응답을 딕셔너리 형식으로 변환
            if hasattr(res, 'to_dict'):
                res_dict = res.to_dict()  # to_dict() 메서드를 사용하여 변환
            else:
                res_dict = dict(res)  # 이미 딕셔너리인 경우 그대로 사용

            print("Elasticsearch 업로드 성공:", res_dict)
            return res_dict
        except Exception as e:
            print("Elasticsearch 업로드 중 알 수 없는 오류 발생:", str(e))
            raise RuntimeError(f"Elasticsearch 업로드 오류: {str(e)}")
    except Exception as e:
        print("Elasticsearch 설정 오류 발생:", str(e))
        raise RuntimeError(f"Elasticsearch 설정 오류 발생: {str(e)}")




def search_full_list():
    es = settings.ELASTICSEARCH
    if not es:
        return {"error": "Elasticsearch client not configured"}

    # 검색 쿼리 작성
    body = {
        "_source": ["alternate_url", "favicon", "title", "keywords", "created_at"],  # 가져오고 싶은 필드들
        "query": {
            "match_all": {}  # 모든 문서 검색
        },
        "sort": [
            {
                "created_at": {
                    "order": "desc"  # 최신순 정렬
                }
            }
        ]
    }

    try:
        # Elasticsearch에 검색 요청 전송
        response = es.search(index=index, body=body)
        hits = response.get('hits', {}).get('hits', [])

        # 검색 결과 반환 (각 문서의 ID 포함)
        results = [{"id": hit.get("_id"), **hit.get("_source", {})} for hit in hits]
        return results

    except NotFoundError:
        return {'status': 'error', 'message': '인덱스를 찾을 수 없습니다.'}
    except RequestError as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': f'알 수 없는 오류 발생: {str(e)}'}


def search_by_id(doc_id):
    es = settings.ELASTICSEARCH
    if not es:
        return {"error": "Elasticsearch client not configured"}

    try:
        # Elasticsearch에 get 요청을 보내 문서 가져오기
        response = es.get(index='pages', id=doc_id)

        id_search_results = response["_source"]
        id_search_results["id"] = response["_id"]

        return id_search_results

    except NotFoundError:
        return {"error": f"Document with ID {document_id} not found."}
    except RequestError as e:
        return {"error": f"Failed to fetch document due to request error: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


def search_by_tkm(tag, keyword, method):
    es = settings.ELASTICSEARCH
    if not es:
        return {"error": "Elasticsearch client not configured"}

    if not keyword:
        return {'error': '검색어가 제공되지 않았습니다.'}
    if not tag:
        return {'error': 'tag가 제공되지 않았습니다.'}
    if not method:
        return {'error': 'method가 제공되지 않았습니다.'}

    # 검색 쿼리 작성
    body = {
        "query": {
            method: {
                tag: keyword
            }
        }
    }

    try:
        # Elasticsearch에 검색 요청 전송
        response = es.search(index=index, body=body)
        hits = response.get('hits', {}).get('hits', [])

        # 검색 결과 반환
        results = [{"id": hit.get("_id"), **hit.get("_source", {})} for hit in hits]
        return results

    except NotFoundError:
        return {'status': 'error', 'message': '인덱스를 찾을 수 없습니다.'}
    except RequestError as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': f'알 수 없는 오류 발생: {str(e)}'}


def search_by_text(query_text):
    # Elasticsearch 클라이언트 초기화
    es = settings.ELASTICSEARCH
    if not es:
        return {"error": "Elasticsearch client not configured"}

    if not query_text:
        return {"error": "검색어를 입력하지 않았습니다."}

    # Elasticsearch 쿼리 본문 정의
    body = {
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["title", "author", "content", "short_summary", "long_summary", "keywords", "comments.author", "comments.content", "image_links.caption", "file_download_links.caption"]
            }
        },
        "highlight": {
            "fields": {
                "title": {},
                "author": {},
                "content": {},
                "short_summary": {},
                "long_summary": {},
                "keywords": {},
                "comments.author": {},
                "comments.content": {},
                "image_links.caption": {},
                "file_download_links.caption": {}
            },
            "pre_tags": ["<strong>"],
            "post_tags": ["</strong>"]
        }
    }


    try:
        # Elasticsearch에 검색 쿼리 요청
        response = es.search(index="pages", body=body)
        hits = response.get('hits', {}).get('hits', [])

        # 검색 결과 및 하이라이트 처리
        results = []
        for hit in hits:
            source = hit['_source']
            document_id = hit['_id']  # 문서의 ID 값
            highlight = hit.get('highlight', {})
            results.append({
                "id": document_id,  # 문서 ID 추가
                "source": source,
                "highlight": highlight
            })
        return results

    except Exception as e:
        return {"error": f"Failed to fetch documents: {str(e)}"}
    # 출력 예시
    # [
    #     {
    #         "id": "12345",
    #         "source": {
    #             "title": "엘라스틱서치 소개",
    #             "author": "이시운",
    #             "created_at": "2024-11-07"
    #         },
    #         "highlight": {
    #             "content": [
    #                 "<em>엘라스틱서치</em>는 분산형 검색 엔진입니다."
    #             ]
    #         }
    #     }
    # ]


def search_by_similarity(doc_id, index="pages"):
    # Elasticsearch 클라이언트 초기화
    es = settings.ELASTICSEARCH
    if not es:
        return {"error": "Elasticsearch client not configured"}

    if not doc_id:
        return {"error": "doc_id가 제공되지 않았습니다."}

    # `more_like_this` 쿼리 정의
    body = {
        "query": {
            "more_like_this": {
                "fields":  ["title", "author", "content", "short_summary", "long_summary","category_keywords""comments.author", "comments.content", "image_links.caption", "file_download_links.caption"],  # 비교할 필드들
                "like": [
                    {
                        "_index": index,
                        "_id": doc_id
                    }
                ],
                "min_term_freq": 1,
                "min_doc_freq": 1
            }
        }
    }

    try:
        # Elasticsearch에 검색 쿼리 요청
        response = es.search(index=index, body=body)
        hits = response.get('hits', {}).get('hits', [])

        # 검색 결과 반환
        results = [{"id": hit.get("_id"), **hit.get("_source", {})} for hit in hits]
        return results

    except Exception as e:
        return {"error": f"Failed to fetch documents: {str(e)}"}