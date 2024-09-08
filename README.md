# Azure_API

2024 HackerGround in 의성에서 개발한 API 코드
- Azure를 이용해 DB 구축 및 API 개발
- API는 3가지로 구성

# Location
kakao map
- DB : 의성군 경로당 데이터 불러오기 ➡️ JSON

# Review_Rating
Azure_AI_SERVICE : text analytics
- kakao map api에서 해당 경로명 마커 클릭시, 경로당명과 경로당 주소 조회
- 해당 경로당에 대한 최근 10개의 리뷰 query(request)
- text analytics를 통해 감정 분석
- 분석 결과 : Postive 값(respone)을 5점 만점 Scoring 수식을 통해 최종 respone  

![Review_Rating](https://github.com/user-attachments/assets/c9426b2b-5e5a-43a2-ba03-ec3912020a29)

# Review_Solution
Azure_OpenAI : Prompt
- kakao map api에서 해당 경로명 마커 클릭시, 경로당명과 경로당 주소 조회
- 해당 경로당에 대한 최근 10개의 리뷰 query(request)
- 리뷰에 대해 OpenAPI Prompt 솔루션 요청 ➡️ 좋은점 AND 나쁜점 출력
- 나쁜점에 대한 AI Solution 제공(respone)  

![Review_Solution](https://github.com/user-attachments/assets/496671e1-971d-4287-8141-4a90f74655f2)
