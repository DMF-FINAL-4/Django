# history/utils.py

from django.conf import settings
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch, NotFoundError, RequestError
import json
import re


def get_elasticsearch_client():
    es = settings.ELASTICSEARCH
    if not es:
        raise RuntimeError("Elasticsearch client not configured")
    return es


def process_html(html, url):
    try:
        # BeautifulSoup을 사용하여 HTML 태그 정제
        soup = BeautifulSoup(html, 'lxml')
        print('3.3')
        # 1. 파비콘 링크 추출
        favicon_link = None
        icon_link_tag = soup.find("link", rel=re.compile("icon", re.I))
        if icon_link_tag and icon_link_tag.has_attr("href"):
            favicon_link = icon_link_tag["href"]
            if favicon_link.startswith("/"):
                favicon_link = url + favicon_link
        print('3.4')
        # 2. 제목 추출
        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else "Untitled"
        print('3.5')
        # 3. 불필요한 태그 제거 (스타일, 스크립트, 광고 등)
        tags_to_remove = ['style', 'script', 'aside', 'nav', 'footer', 'header', 'iframe', 'noscript', 'form', 'advertisement', 'banner']
        for tag in tags_to_remove:
            for element in soup.find_all(tag):
                element.decompose()  # 캡션: 불필요한 HTML 요소를 제거하여 의미 있는 콘텐츠만 남깁니다.
        print('3.6')
        # 4. 불필요한 속성 제거 (스타일, 클래스 등)
        attributes_to_remove = ['style', 'class', 'id', 'onclick', 'onmouseover']
        for tag in soup.find_all(True):
            for attr in attributes_to_remove:
                if attr in tag.attrs:
                    del tag.attrs[attr]  # 캡션: HTML 태그에 포함된 불필요한 속성을 제거하여 가독성을 높입니다.
        print('3.7')
        # 5. 텍스트 추출 및 정리
        cleaned_content = soup.get_text(separator=" ").strip()
        print('3.8')
        # 6. 불필요한 문구 제거 (이용 약관, 광고 등)
        unnecessary_phrases = ["이용 약관", "쿠키 정책", "광고", "©", "모든 권리 보유"]
        for phrase in unnecessary_phrases:
            cleaned_content = cleaned_content.replace(phrase, "")  # 캡션: 일반적으로 불필요한 문구를 제거하여 유의미한 콘텐츠만 남깁니다.
        print('3.9')
        # 7. 중복된 라인 제거
        lines = cleaned_content.splitlines()
        unique_lines = []
        [unique_lines.append(line) for line in lines if line not in unique_lines]
        cleaned_content = "\n".join(unique_lines)  # 캡션: 중복된 내용을 제거하여 콘텐츠의 간결성을 유지합니다.
        print('3.10')
        # 8. 공백 및 특수 문자 정리
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content)  # 여러 개의 공백을 하나로 축소
        cleaned_content = re.sub(r'[^\w\s.,!?-]', '', cleaned_content)  # 특수 문자 제거
        print('3.11')
        # 9. 불필요한 줄바꿈 정리
        cleaned_content = re.sub(r'\n+', '\n', cleaned_content).strip()  # 여러 줄바꿈을 하나로 축소
        print('3.12')
        # 10. HTML 엔티티 디코딩
        # cleaned_content = unescape(cleaned_content)  # 캡션: HTML 엔티티(&nbsp;, &amp; 등)를 실제 문자로 변환하여 자연스러운 텍스트로 만듭니다.
        print('3.13')
        # 11. 언어 감지를 통해 유효한 콘텐츠 필터링
        # try:
        #     if detect(cleaned_content) not in ['ko', 'en']:
        #         raise ValueError("유효하지 않은 콘텐츠입니다.")
        # except Exception as e:
        #     cleaned_content = ""  # 캡션: 유효하지 않은 언어의 콘텐츠는 제거합니다.

        # # 12. 스팸 또는 광고성 문구 제거
        # spam_patterns = [r"무료.*다운로드", r"클릭하세요", r"광고 문의"]
        # for pattern in spam_patterns:
        #     cleaned_content = re.sub(pattern, "", cleaned_content, flags=re.IGNORECASE)  # 캡션: 스팸성 문구를 제거하여 신뢰성을 높입니다.
        print('4')
        return favicon_link, title, cleaned_content
    except Exception as e:
        raise RuntimeError(f"HTML 처리 중 오류 발생: {str(e)}")


def upload_to_elasticsearch_history(processed_json, index='history', pipeline='add_created_at'):
    try:
        es = get_elasticsearch_client()
        res = es.index(index=index, pipeline=pipeline, body=processed_json)
        if hasattr(res, 'to_dict'):
            res_dict = res.to_dict()
        else:
            res_dict = dict(res)
        return res_dict
    except Exception as e:
        raise RuntimeError(f"Elasticsearch 업로드 오류: {str(e)}")


def search_full_list_history(page=0, size=50):
    es = get_elasticsearch_client()
    body = {
        "_source": ["url", "favicon", "title", "created_at"],
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
        response = es.search(index='history', body=body)
        hits = response.get('hits', {}).get('hits', [])
        results = [{"id": hit.get("_id"), **hit.get("_source", {})} for hit in hits]
        return results
    except NotFoundError:
        return {'status': 'error', 'message': '인덱스를 찾을 수 없습니다.'}
    except RequestError as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': f'알 수 없는 오류 발생: {str(e)}'}


# def search_by_id_history(doc_id):
#     es = get_elasticsearch_client()
#     try:
#         response = es.get(index='history', id=doc_id)
#         id_search_results = response["_source"]
#         id_search_results["id"] = response["_id"]
#         return id_search_results
#     except NotFoundError:
#         return {"error": f"Document with ID {doc_id} not found."}
#     except RequestError as e:
#         return {"error": f"Failed to fetch document due to request error: {str(e)}"}
#     except Exception as e:
#         return {"error": f"An unexpected error occurred: {str(e)}"}

def search_by_id_history(doc_id):
    es = get_elasticsearch_client()
    try:
        response = es.get(index='history', id=doc_id)
        id_search_results = response["_source"]
        id_search_results["id"] = response["_id"]
        return id_search_results
    except NotFoundError:
        return {"error": f"Document with ID {doc_id} not found."}
    except RequestError as e:
        return {"error": f"Failed to fetch document due to request error: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def delete_by_id_history(doc_id):
    es = get_elasticsearch_client()
    try:
        # 먼저 문서를 가져와서 삭제 전의 데이터를 저장합니다.
        response = es.get(index='history', id=doc_id)
        id_search_results = response["_source"]
        id_search_results["id"] = response["_id"]
        
        # 문서를 삭제합니다.
        delete_response = es.delete(index='history', id=doc_id)
        print('삭제 요청 완료')
        
        # 삭제 결과를 확인합니다.
        if delete_response.get('result') == 'deleted':
            print('삭제 결과 확인')
            return {
                "message": f"Document with ID {doc_id} successfully deleted.",
                "deleted_document": id_search_results
            }
        else:
            return {
                "error": f"Failed to delete document with ID {doc_id}.",
                "details": delete_response
            }
    
    except NotFoundError:
        return {"error": f"Document with ID {doc_id} not found."}
    except RequestError as e:
        return {"error": f"Failed to delete document due to request error: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def search_by_text_history(query_text):
    es = get_elasticsearch_client()
    if not query_text:
        return {"error": "검색어를 입력하지 않았습니다."}
    
    # Elasticsearch 검색 쿼리 정의
    body = {
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["title", "content"]  # 검색할 필드 지정
            }
        },
        "highlight": {
            "fields": {
                "title": {},
                "content": {}  # 검색어 하이라이트 설정
            },
            "pre_tags": ["<strong>"],
            "post_tags": ["</strong>"]
        }
    }
    try:
        response = es.search(index="history", body=body)
        hits = response.get('hits', {}).get('hits', [])
        results = []
        # for hit in hits:
        #     source = hit['_source']
        #     document_id = hit['_id']
        #     highlight = hit.get('highlight', {})
        #     results.append({
        #         "id": document_id,
        #         "source": source,
        #         "highlight": highlight  # 검색 결과와 하이라이트된 부분 포함
        #     })
        # 하이라이트 제외
        results = [{"highlight": hit.get("highlight", {}) ,"id": hit.get("_id"), **hit.get("_source", {})} for hit in hits]
        
        return results  # 캡션: 검색 결과와 하이라이트된 부분을 함께 반환합니다.
    except Exception as e:
        return {"error": f"Failed to fetch documents: {str(e)}"}


def search_by_tkm_history(tag, keyword, method):
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
        response = es.search(index='history', body=body)
        hits = response.get('hits', {}).get('hits', [])
        results = [{"id": hit.get("_id"), **hit.get("_source", {})} for hit in hits]
        return results
    except NotFoundError:
        return {'status': 'error', 'message': '인덱스를 찾을 수 없습니다.'}
    except RequestError as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': f'알 수 없는 오류 발생: {str(e)}'}


def search_by_similarity_history(doc_id, index="history"):
    es = get_elasticsearch_client()
    if not doc_id:
        return {"error": "doc_id가 제공되지 않았습니다."}
    
    # Elasticsearch `more_like_this` 쿼리 정의
    body = {
        "query": {
            "more_like_this": {
                "fields":  ["title", "content", "category_keywords"],  # 유사성을 비교할 필드들
                "like": [
                    {
                        "_index": index,
                        "_id": doc_id
                    }
                ],
                "min_term_freq": 1,  # 최소 용어 빈도
                "min_doc_freq": 1  # 최소 문서 빈도
            }
        }
    }
    try:
        response = es.search(index='history', body=body)
        hits = response.get('hits', {}).get('hits', [])
        results = [{"id": hit.get("_id"), **hit.get("_source", {})} for hit in hits]
        return results  # 캡션: 유사한 문서들을 검색하여 결과를 반환합니다.
    except Exception as e:
        return {"error": f"Failed to fetch documents: {str(e)}"}