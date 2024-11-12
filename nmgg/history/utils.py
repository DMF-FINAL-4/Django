# utils.py for history app
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
        # Use BeautifulSoup to clean and extract content
        soup = BeautifulSoup(html, 'lxml')

        # Extract the favicon link if available
        favicon_link = None
        icon_link_tag = soup.find("link", rel=re.compile("icon", re.I))
        if icon_link_tag and icon_link_tag.has_attr("href"):
            favicon_link = icon_link_tag["href"]
            if favicon_link.startswith("/"):
                favicon_link = url + favicon_link

        # Extract the title
        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else "Untitled"

        # Remove unwanted tags and clean content
        tags_to_remove = ['style', 'script', 'aside', 'nav', 'footer', 'header', 'iframe', 'noscript', 'form']
        for tag in tags_to_remove:
            for element in soup.find_all(tag):
                element.decompose()

        cleaned_content = soup.get_text(separator=" ").strip()

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


def search_full_list_history():
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
        ]
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


def search_by_text_history(query_text):
    es = get_elasticsearch_client()
    if not query_text:
        return {"error": "검색어를 입력하지 않았습니다."}
    body = {
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["title", "content"]
            }
        },
        "highlight": {
            "fields": {
                "title": {},
                "content": {}
            },
            "pre_tags": ["<strong>"],
            "post_tags": ["</strong>"]
        }
    }
    try:
        response = es.search(index="history", body=body)
        hits = response.get('hits', {}).get('hits', [])
        results = []
        for hit in hits:
            source = hit['_source']
            document_id = hit['_id']
            highlight = hit.get('highlight', {})
            results.append({
                "id": document_id,
                "source":
