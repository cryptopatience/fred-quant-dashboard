# 📊 FRED API 퀀트 3콤보 분석 대시보드

## 🎯 개요
Fed 유동성(Net Liquidity), 달러 인덱스, HY Spread를 통해 Bitcoin, NASDAQ, S&P 500의 움직임을 분석하는 인터랙티브 대시보드입니다.

## 🚀 로컬 실행 방법

### 1. 환경 설정
```bash
pip install -r requirements.txt
```

### 2. 앱 실행
```bash
streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501` 열림

## 🌐 Streamlit Cloud 배포

### 1. GitHub 레포지토리 생성
1. GitHub에서 새 레포지토리 생성
2. 다음 파일들을 업로드:
   - `app.py`
   - `requirements.txt`
   - `README.md`

### 2. Streamlit Cloud 배포
1. [streamlit.io/cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 레포지토리 선택
5. Main file path: `app.py`
6. Deploy 클릭

⚠️ **중요**: API 키는 Streamlit Cloud의 Secrets 기능을 사용하여 안전하게 관리하세요!

### 3. API 키 보안 설정 (선택사항)

**app.py에서 수정:**
```python
# 기존 코드
FRED_API_KEY = "f1137018f7bb4b4150a5c84e09fc7fc2"

# 보안 강화 코드
import streamlit as st
FRED_API_KEY = st.secrets["FRED_API_KEY"]
```

**Streamlit Cloud에서 설정:**
1. 앱 설정 → Secrets
2. 다음 내용 추가:
```toml
FRED_API_KEY = "f1137018f7bb4b4150a5c84e09fc7fc2"
```

## 📊 주요 기능

### 5개 탭 구성
1. **콤보 1: Net Liquidity** - Fed 유동성과 리스크 자산의 관계
2. **콤보 2: Dollar Index** - 달러 강세와 비트코인 역상관
3. **콤보 3: HY Spread** - 신용 위험과 주식 시장
4. **종합 대시보드** - 전체 지표 한눈에 보기
5. **트레이딩 시그널** - 매매 신호 및 종합 점수

### 인터랙티브 기능
- 📅 분석 기간 선택 (1년/2년/3년/5년)
- 📈 롤링 윈도우 조정 (30~180일)
- 🔍 Plotly 줌/팬/호버 기능
- 📊 실시간 상관계수 추적
- 🎯 자동 트레이딩 시그널 생성

## 📁 파일 구조
```
project/
├── app.py              # Streamlit 메인 앱
├── requirements.txt    # 의존성 패키지
└── README.md          # 프로젝트 문서
```

## 🔧 기술 스택
- **Frontend**: Streamlit
- **Data**: FRED API (Federal Reserve Economic Data)
- **Visualization**: Plotly
- **Analysis**: Pandas, NumPy

## 📌 주요 지표 설명

### Net Liquidity
```
Net Liquidity = Fed Total Assets - Treasury General Account - Reverse Repo
```
- Fed의 실제 시장 유동성 공급량
- 상승 = 리스크 자산 강세 (BTC, 주식)
- 하락 = 리스크 자산 약세

### Dollar Index (DXY)
- 주요 통화 대비 달러 강도
- DXY 상승 = 글로벌 유동성 축소 = BTC 약세
- DXY 하락 = 글로벌 유동성 확대 = BTC 강세

### High Yield Spread
- 정크본드와 국채 수익률 차이
- 5% 이상 = 신용 경색, 경기 침체 신호
- 낮을수록 = 신용 시장 안정

## ⚠️ 면책 조항
본 대시보드는 교육 및 분석 목적으로 제작되었습니다. 투자 권유가 아니며, 모든 투자 결정은 사용자의 책임입니다.

## 📝 라이선스
MIT License

## 👨‍💻 개발자
Bomi - Quantitative Finance Enthusiast

## 🔗 참고 자료
- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/fred/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
