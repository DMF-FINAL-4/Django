// 질문 제출 함수
function submitQuestion() {
    const question = document.getElementById('questionInput').value;

    fetch('https://your-backend-server.com/api/ask/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: question })
    })
    .then(response => response.json())
    .then(data => {
        // 결과 표시
        displayResult(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}



다음은 Elasticsearch 인덱스의 매핑 구조입니다:
[매핑 구조 JSON]

사용자의 질문: "[사용자 질문]"

위의 매핑 구조를 기반으로, 사용자의 질문에 답하기 위한 적절한 Elasticsearch 쿼리를 JSON 형식으로 생성해줘.


Elasticsearch 인덱스의 매핑 구조는 다음과 같습니다:
{
  "mappings": {
    "properties": {
      "title": { "type": "text" },
      "content": { "type": "text" },
      "url": { "type": "keyword" },
      "created_at": { "type": "date" }
    }
  }
}

사용자의 질문: "파이썬 관련 문서를 모두 보여줘."

위의 매핑 구조를 기반으로, 사용자의 질문에 답하기 위한 Elasticsearch 쿼리를 JSON 형식으로 생성해줘.
