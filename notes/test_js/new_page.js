fetch('http://127.0.0.1:8000/page_save/new_page/', {
    method: 'POST',
    headers: {
        'Content-Type': 'text/html',
    },
    body: `<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>기술 혁신: AI가 의료 진단의 정확도를 높인다</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            max-width: 800px;
            margin: auto;
        }
        header {
            background-color: #f4f4f4;
            padding: 10px;
            margin-bottom: 20px;
        }
        h1 {
            color: #333;
        }
        .author, .date {
            color: #666;
            font-style: italic;
        }
        img {
            max-width: 100%;
            height: auto;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <header>
        <h1>기술 혁신: AI가 의료 진단의 정확도를 높인다</h1>
        <p class="author">작성자: 김기자</p>
        <p class="date">발행일: 2024년 11월 6일</p>
    </header>

    <main>
        <img src="https://example.com/ai-medical-image.jpg" alt="AI 의료 진단 이미지">

        <p>인공지능(AI) 기술이 의료 분야에 혁명을 일으키고 있습니다. 최근 연구에 따르면, AI를 활용한 의료 진단 시스템이 인간 의사의 진단 정확도를 크게 향상시키는 것으로 나타났습니다.</p>

        <p>서울대학교병원의 연구팀은 지난 1년간 AI 진단 시스템을 활용한 결과, 암 진단의 정확도가 15% 향상되었다고 발표했습니다. 이는 조기 진단과 치료 계획 수립에 큰 도움이 될 것으로 기대됩니다.</p>

        <p>연구를 이끈 박사무엘 교수는 "AI는 인간 의사를 대체하는 것이 아니라, 의사의 판단을 보조하고 더 정확한 진단을 내리는 데 도움을 줍니다"라고 설명했습니다.</p>

        <p>이번 연구 결과는 의료계에 큰 반향을 일으키고 있으며, 앞으로 AI 기술이 의료 현장에서 더 광범위하게 활용될 것으로 전망됩니다.</p>
    </main>

    <footer>
        <p>© 2024 테크뉴스. 모든 권리 보유.</p>
    </footer>
</body>
</html>`,
})
.then(response => response.json())
.then(data => {
    if (data.status === 'success') {
        console.log('데이터 업로드 성공:', data);
    } else {
        console.error('에러 발생:', data.message);
    }
})
.catch((error) => {
    console.error('요청 실패:', error);
});

