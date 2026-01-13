# 🎯 리얼픽 마케팅 자동화 시스템

리얼픽 앱 런칭을 위한 3단계 마케팅 자동화 도구입니다.

## 📋 프로젝트 개요

### 목표
- 유튜버 '딜러' 자동 모집 및 관리
- 초기 트래픽 생성을 위한 가짜 유저 봇 운영
- 커뮤니티 바이럴 마케팅 자동화

### 현재 구현 상태
- ✅ **모듈 1**: 유튜버 딜러 모집 (구현 완료)
- ⏳ **모듈 2**: 가짜 유저 봇 (준비 중)
- ⏳ **모듈 3**: 커뮤니티 바이럴 (준비 중)

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# 이메일 설정
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password

# Supabase (리얼픽 앱과 동일)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 3. 앱 실행

```bash
streamlit run streamlit_app.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

## 📁 프로젝트 구조

```
realpick-marketing/
├── streamlit_app.py          # 메인 Streamlit 앱
├── modules/                  # 핵심 모듈들
│   ├── __init__.py
│   ├── youtube_crawler.py    # YouTube 크롤링
│   ├── gemini_analyzer.py    # AI 분석
│   ├── mission_generator.py  # 미션 생성
│   └── email_sender.py       # 이메일 발송
├── config/
│   └── settings.py           # 설정 파일
├── data/                     # 데이터 저장소
├── requirements.txt          # 의존성 목록
└── README.md                # 이 파일
```

## 🔧 모듈 1: 유튜버 딜러 모집

### 주요 기능

1. **🔍 YouTube 크롤링**
   - 타겟 채널의 최신 영상 자동 수집
   - 영상 메타데이터 및 통계 정보 추출
   - 자막 데이터 수집 (추후 구현)

2. **🤖 AI 분석**
   - Gemini AI를 통한 영상 내용 분석
   - 논쟁거리 및 투표 주제 추출
   - 미션 제목 및 선택지 자동 생성

3. **📝 미션 생성**
   - AI 분석 결과를 바탕으로 미션 객체 생성
   - 관리자 승인 워크플로우
   - 리얼픽 앱 DB 형식으로 변환

4. **📧 이메일 발송**
   - 파트너십 제안 이메일 자동 생성
   - HTML 템플릿 기반 전문적인 디자인
   - 일괄 발송 및 발송 결과 추적

### 워크플로우

```
YouTube 크롤링 → AI 분석 → 미션 생성 → 관리자 승인 → 이메일 발송
```

## 🎯 사용 방법

### 1. 크롤링 실행
- "🔍 유튜브 크롤링" 탭에서 "🚀 크롤링 시작" 버튼 클릭
- 타겟 채널들의 최신 영상 자동 수집

### 2. AI 분석
- "🤖 AI 분석" 탭에서 "🧠 AI 분석 시작" 버튼 클릭
- 수집된 영상들을 Gemini AI로 분석하여 미션 생성

### 3. 미션 승인
- "📝 미션 생성" 탭에서 생성된 미션들 검토
- 적절한 미션들을 선별하여 승인

### 4. 이메일 발송
- "📧 이메일 발송" 탭에서 승인된 미션의 유튜버들에게 파트너십 제안 이메일 발송

## ⚙️ 설정

### 타겟 채널 추가
`config/settings.py`의 `TARGET_CHANNELS` 리스트에 새로운 채널 정보를 추가하세요:

```python
{
    'name': '새로운 채널',
    'keywords': ['키워드1', '키워드2'],
    'category': 'dating',
    'show_id': 'new_show',
    'priority': 'high'
}
```

### 크롤링 설정 조정
`CRAWL_SETTINGS`에서 크롤링 주기, 영상 수 등을 조정할 수 있습니다.

### AI 분석 설정
`AI_SETTINGS`에서 최소 논쟁 점수, 미션 타입 등을 설정할 수 있습니다.

## 📊 모니터링

### 실시간 통계
- 수집된 영상 수
- 생성된 미션 수
- 발송된 이메일 수
- 성공률 및 응답률

### 로그 파일
- `data/` 폴더에 크롤링 결과, 분석 결과, 이메일 발송 로그 저장
- JSON 형식으로 구조화된 데이터 보관

## 🔮 향후 계획

### 모듈 2: 가짜 유저 봇 (다음 단계)
- 자동 투표 시스템
- 자연스러운 참여 패턴 시뮬레이션
- 관리자 대시보드

### 모듈 3: 커뮤니티 바이럴 (최종 단계)
- 커뮤니티 모니터링
- 자동 댓글 생성
- 바이럴 효과 측정

## 🛠️ 개발 정보

### 기술 스택
- **Frontend**: Streamlit
- **Backend**: Python
- **AI**: Google Gemini Pro
- **Database**: Supabase
- **APIs**: YouTube Data API v3

### 개발자
- RealPick Team

### 라이선스
- Private (내부 사용 전용)

## 📞 지원

문제가 발생하거나 기능 요청이 있으시면 개발팀에 연락해주세요.

---

**⚠️ 주의사항**
- 이 도구는 리얼픽 내부 사용 전용입니다
- API 키와 인증 정보를 안전하게 관리하세요
- 이메일 발송 시 스팸 정책을 준수하세요
