# pages/utils.py

from django.conf import settings
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

def validate_required_fields(data, required_fields):
    for field in required_fields:
        if field not in data:
            return JsonResponse({"error": f"{field} is required"}, status=400)
    return None

def get_elasticsearch_client():
    es = settings.ELASTICSEARCH
    if not es:
        raise RuntimeError("Elasticsearch client not configured")
    return es

def classify_request(request):
    if request['url'] and request['html']:
        if not request['duplicates']:
            url = request['url']
            es_res = search_page_by_tkm('url', url, 'term')
            if es_res.get('hits', {}).get('total', {}).get('value', 0) > 0:
                hits = es_res.get('hits', {}).get('hits', [])
                results = [{"id": hit.get("_id"), **hit.get("_source", {})} for hit in hits]
                return results
        return False
    else:
        raise ValueError("URL and HTML are required")

class HTMLSummariz:

    def __init__(self):
        openai_api_key = settings.OPENAI_API_KEY
        if not openai_api_key:
            raise ValueError("API key not found")
        openai.api_key = openai_api_key
        print('OPENAI_API_KEY 등록')
        print('html 정보 추출 클래스 인스턴스 생성')

    def clean_html_style_tags(self, raw_html_content):
        try:
            print('태그 정돈 시작')
            soup = BeautifulSoup(raw_html_content, 'lxml')
            tags_to_remove = ['style', 'script', 'aside', 'nav', 'footer', 'header', 'iframe', 'noscript', 'form']
            for tag in tags_to_remove:
                for element in soup.find_all(tag):
                    element.decompose()
            attributes_to_remove = ['style', 'class', 'id']
            for tag in soup.find_all(True):
                for attr in attributes_to_remove:
                    if attr in tag.attrs:
                        del tag.attrs[attr]
            cleaned_html = str(soup)
            print('태그 정돈 완료')
            return cleaned_html

        except Exception as e:
            raise RuntimeError(f"HTML 태그 정제 중 오류 발생: {str(e)}")

    def extract_information_with_gpt(self, cleaned_html):
        prompt = f"""
        아래는 정제된 웹 페이지의 HTML입니다. 이 HTML에서 다음 정보를 추출하여 **유효한 JSON 형식으로만** 반환하세요. 다른 텍스트나 설명은 포함하지 마세요.:

        - 접근권한 (access_permission): 만약 접근에 제한이 있는 페이지로 확인된다면 'HTTP 상태 코드', '없는 페이지', '로그인 필요' 등의 적절한 항목을 출력하고, 문제가 없다면 '정상'을 출력합니다.
        - 파비콘 (favicon): 파비콘의 호스트 도메인을 포함한 전체 경로를 저장하며, 만약 여러 개라면 가장 큰 이미지의 것 한 개만 저장합니다.
        - 호스트 도메인 (host_domain): 페이지의 호스트 도메인을 저장합니다.
        - 호스트 이름 (host_name): 호스트의 이름을 한글로 출력하고, 한글이 없다면 영어로 출력합니다. (예시: 네이버 뉴스, 페이스북, 위키백과)
        - 대체 URL (alternate_url): Canonical URL 또는 Open Graph URL이 존재한다면 이곳에 표시합니다.
        - 제목 (title): 각종 정보를 종합한 제목을 출력합니다. (예시: '동아일보｜[이철희 칼럼] 형제애로 마련한 400억…감사 전한 튀르키예')
        - 작성자 (author): 본문의 작성자를 출력합니다.
        - 작성일 (date): 페이지의 작성일을 `yyyy-MM-dd` 형식으로 출력합니다.
        - 본문 (content): 명백한 오타 수정을 제외한 텍스트 왜곡이 없으며, 표 내부의 내용 등을 포함한 누락 없는 본문을 출력합니다.
        - 짧은 요약 (short_summary): 본문을 20자에서 90자 사이로 요약합니다.
        - 긴 요약 (long_summary): 본문을 200자에서 400자 사이로 요약합니다.
        - 키워드 (keywords): 본문의 키워드들을 출력합니다. 내용이 많고 주제가 폭넓다면 키워드가 많아져도 좋습니다.
        - 유형 키워드 (category_keywords): 블로그, 카페, 기사, 정보, 사연, 에세이, 영상, 사진, 리뷰, 쇼핑, SNS 등 유형이라 할 수 있는 키워드들을 풍부하게 출력합니다.
        - 댓글 (comments): 댓글이 있다면 예시의 형식에 따라 모두 저장합니다.
        - 이미지 링크 (image_links): 본문 이미지를 예시의 형식에 따라 모두 저장합니다.
        - 링크 (links): 본문 내에 주요한 외부 또는 내부 링크들이 있을 경우 예시의 형식에 따라 모두 저장합니다.
        - 미디어 링크 (media_links): 본문 내에 비디오 및 오디오 등의 미디어가 있을 경우 예시의 형식에 따라 모두 저장합니다.
        - 파일 다운로드 링크 (file_download_links): 주요한 PDF, 이미지, 문서 등의 다운로드 링크가 있을 경우 예시의 형식에 따라 모두 저장합니다.
        - 콘텐츠의 길이 (content_length): 콘텐츠를 읽는 데 걸리는 시간을 예측하여 분 단위로 출력합니다. (예시: "2")

        HTML:
        \"\"\"
        {cleaned_html}
        \"\"\"

        JSON 형식 예시:
        {{
            "access_permission": "정상",
            "favicon": "https://www.example.com/favicon.ico",
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
            "comments": [
                {
                    "author": "작성자1",
                    "content": "댓글내용1",
                    "date": "yyyy-MM-dd"
                },
                {
                    "author": "작성자2",
                    "content": "댓글내용2",
                    "date": "yyyy-MM-dd"
                }
            ],
            "image_links": [
                {
                    "caption": "이미지캡션1",
                    "url": "https://example.com/image1.jpg"
                },
                {
                    "caption": "이미지캡션2",
                    "url": "https://example.com/image2.jpg"
                }
            ],
            "links": [
                {
                    "caption": "캡션1",
                    "url": "https://example.com/link1.html"
                },
                {
                    "caption": "캡션2",
                    "url": "https://example.com/link2.html"
                }
            ],
            "media": [
                {
                    "caption": "캡션1",
                    "url": "https://example.com/video1.mp4"
                },
                {
                    "caption": "캡션2",
                    "url": "https://example.com/audio1.mp3"
                }
            ],
            "file_download_links": [
                {
                    "caption": "파일제목1",
                    "size": "10MB",
                    "url": "https://example.com/file1.pdf"
                },
                {
                    "caption": "파일제목2",
                    "size": "1.1GB",
                    "url": "https://example.com/file2.zip"
                }
            ],
            "content_length": m
        }}
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 정보를 추출하는 어시스턴트입니다. 규칙에 따라 유효한 JSON 형식으로만 반환하세요."},
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
            raise ValueError(f"GPT 응답이 유효한 JSON 형식이 아닙니다: {str(e)}")

    def process(self, raw_html):
        try:
            cleaned_html = self.clean_html_style_tags(raw_html)
            extracted_info = self.extract_information_with_gpt(cleaned_html)
            processed_data = self.GPT_to_json(extracted_info)
            print('process 완료')
            return processed_data
        except Exception as e:
            return {"error": "알 수 없는 오류 발생", "details": str(e)}

def upload_to_elasticsearch(processed_json, index='pages', pipeline='add_created_at'):
    print("Elasticsearch에 데이터 업로드 시도")
    try:
        es = get_elasticsearch_client()
        res = es.index(index=index, pipeline=pipeline, body=processed_json)
        if hasattr(res, 'to_dict'):
            res_dict = res.to_dict()
        else:
            res_dict = dict(res)
        print("Elasticsearch 업로드 성공:", res_dict)
        return res_dict
    except Exception as e:
        raise RuntimeError(f"Elasticsearch 업로드 오류: {str(e)}")

def search_full_list(page=0, size=10):
    """
    전체 목록을 페이징하여 검색합니다.
    :param page: 페이지 번호 (0부터 시작)
    :param size: 한 페이지에 포함될 문서 수
    :return: 검색된 문서 리스트
    """
    es = get_elasticsearch_client()
    body = {
        "_source": ["alternate_url", "favicon", "title", "keywords", "created_at"],
        "query": {
            "match_all": {}
        },
        "sort": [
            {
                "created_at": {
                    "order": "desc"
                }
            }
        ],
        "from": page * size,  # 시작 지점 설정
        "size": size  # 페이지당 결과 수 설정
    }
    try:
        response = es.search(index='pages', body=body)
        hits = response.get('hits', {}).get('hits', [])
        results = [{"id": hit.get("_id"), **hit.get("_source", {})} for hit in hits]
        return results
    except NotFoundError:
        return {'status': 'error', 'message': '인덱스를 찾을 수 없습니다.'}
    except RequestError as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': f'알 수 없는 오류 발생: {str(e)}'}

def search_by_id(doc_id):
    es = get_elasticsearch_client()
    try:
        response = es.get(index='pages', id=doc_id)
        id_search_results = response["_source"]
        id_search_results["id"] = response["_id"]
        return id_search_results
    except NotFoundError:
        return {"error": f"Document with ID {doc_id} not found."}
    except RequestError as e:
        return {"error": f"Failed to fetch document due to request error: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def search_by_tkm(tag, keyword, method):
    es = get_elasticsearch_client()
    if not keyword:
        return {'error': '검색어가 제공되지 않았습니다.'}
    if not tag:
        return {'error': 'tag가 제공되지 않았습니다.'}
    if not method:
        return {'error': 'method가 제공되지 않았습니다.'}
    body = {
        "query": {
            method: {
                tag: keyword
            }
        }
    }
    try:
        response = es.search(index='pages', body=body)
        hits = response.get('hits', {}).get('hits', [])
        results = [{"id": hit.get("_id"), **hit.get("_source", {})} for hit in hits]
        return results
    except NotFoundError:
        return {'status': 'error', 'message': '인덱스를 찾을 수 없습니다.'}
    except RequestError as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': f'알 수 없는 오류 발생: {str(e)}'}

def search_by_text(query_text):
    es = get_elasticsearch_client()
    if not query_text:
        return {"error": "검색어를 입력하지 않았습니다."}
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
        response = es.search(index="pages", body=body)
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
        return {"error": f"Failed to fetch documents: {str(e)}"}

def search_by_similarity(doc_id, index="pages"):
    es = get_elasticsearch_client()
    if not doc_id:
        return {"error": "doc_id가 제공되지 않았습니다."}
    body = {
        "query": {
            "more_like_this": {
                "fields":  ["title", "author", "content", "short_summary", "long_summary", "category_keywords", "comments.author", "comments.content", "image_links.caption", "file_download_links.caption"],
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
        response = es.search(index='pages', body=body)
        hits = response.get('hits', {}).get('hits', [])
        results = [{"id": hit.get("_id"), **hit.get("_source", {})} for hit in hits]
        return results
    except Exception as e:
        return {"error": f"Failed to fetch documents: {str(e)}"}
