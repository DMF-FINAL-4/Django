import requests

a = requests.get('https://n.news.naver.com/mnews/article/011/0004412785')
print(a.text)

with open("aaaaaaaaaaaaaaaaa.txt", "w", encoding="utf-8") as file:
    file.write(a.text)