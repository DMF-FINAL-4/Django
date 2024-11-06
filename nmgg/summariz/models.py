from django.db import models

# Create your models here.

# url만 있는 단계
class Page_url(models.Model):
    url = models.URLField(max_length=200, unique=True)

    def __str__(self):
        return self.url

# url, 페이지 제목, html 을 받아온 단계
class Page_html(models.Model):
    url = models.URLField(max_length=200, unique=True)
    page_title = models.CharField(max_length=200)
    html = models.TextField() 

    def __str__(self):
        return self.page_title

# 본문과 요약정보를 생성한 단계
class Page_summarized(models.Model):
    url = models.URLField(max_length=200, unique=True)
    page_title = models.CharField(max_length=200)
    html = models.TextField()
    body = models.TextField()
    summary = models.TextField(blank=True)
 
    def __str__(self):
        return self.page_title
