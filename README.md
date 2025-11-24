# 📊 FRED API 퀀트 3콤보 분석 대시보드

## 🎯 개요
Fed 유동성(Net Liquidity), 달러 인덱스, HY Spread를 통해 Bitcoin, NASDAQ, S&P 500의 움직임을 분석하는 인터랙티브 대시보드입니다.

## 🚀 로컬 실행 방법

### 1. 환경 설정
```bash
pip install -r requirements.txt
```

### 2. API 키 설정 (중요! 🔐)

프로젝트 폴더에 `.streamlit/secrets.toml` 파일 생성:

```bash
mkdir .streamlit
```

`.streamlit/secrets.toml` 파일에 다음 내용 입력:

```toml
# FRED API Key
FRED_API_KEY = "여기에_본인의_API_키_입력"
```

⚠️ **주의**: 이 파일은 `.gitignore`에 포함되어 GitHub에 업로드되지 않습니다.

### 3. 앱 실행
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
   - `.gitignore`
   - `README.md`
   - `DEPLOYMENT_GUIDE.md`

⚠️ **중요**: `.streamlit/secrets.toml` 파일은 업로드하지 마세요!

### 2. Streamlit Cloud 배포
1. [streamlit.io/cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 레포지토리 선택
5. Main file path: `app.py`
6. **Advanced settings** → **Secrets** 클릭

### 3. Secrets 설정 (필수! 🔐)

Secrets 섹션에 다음 내용 붙여넣기:

```toml
FRED_API_KEY = "여기에_본인의_API_키_입력"
```

7. Deploy 클릭

📖 **자세한 가이드**: `DEPLOYMENT_GUIDE.md` 파일 참조

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
├── .streamlit/
│   └── secrets.toml    # API 키 (로컬 전용, GitHub에 업로드 금지)
├── .gitignore          # secrets.toml 제외 설정
├── app.py              # Streamlit 메인 앱
├── requirements.txt    # 의존성 패키지
├── README.md          # 프로젝트 문서
└── DEPLOYMENT_GUIDE.md # 배포 상세 가이드
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
