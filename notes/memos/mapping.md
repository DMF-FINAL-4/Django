{
  "settings": {
    "index": {
      "number_of_shards": "1",
      "number_of_replicas": "1",
      "analysis": {
        "analyzer": {
          "korean_analyzer": {
            "type": "nori",
            "decompound_mode": "mixed"
          }
        }
      }
    }
  },
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
}
