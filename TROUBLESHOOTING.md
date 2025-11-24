# 🔧 Streamlit 앱 에러 해결 가이드

## 🚨 주요 에러 및 해결 방법

### 1️⃣ ImportError: kaleido 관련 에러

#### 증상
```
ImportError: This app has encountered an error...
Traceback mentions kaleido package
```

#### 원인
- `kaleido` 패키지가 Streamlit Cloud 환경에서 설치 실패
- 우리 앱은 정적 이미지 내보내기를 사용하지 않으므로 불필요

#### 해결 ✅
**requirements.txt 수정:**
```txt
# 삭제: kaleido==0.2.1

# 유지:
streamlit>=1.28.0
fredapi>=0.5.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
```

---

### 2️⃣ API 키 에러

#### 증상
```
⚠️ API 키를 찾을 수 없습니다. .streamlit/secrets.toml 파일을 확인하세요.
```

#### 원인
- Streamlit Cloud Secrets에 API 키가 설정되지 않음

#### 해결 ✅

**Streamlit Cloud에서:**
1. 앱 대시보드 → Settings → Secrets
2. 다음 내용 입력:
```toml
FRED_API_KEY = "f1137018f7bb4b4150a5c84e09fc7fc2"
```
3. Save 클릭
4. 앱 재시작 (Reboot app)

**로컬 개발에서:**
```bash
mkdir .streamlit
echo 'FRED_API_KEY = "f1137018f7bb4b4150a5c84e09fc7fc2"' > .streamlit/secrets.toml
```

---

### 3️⃣ 데이터 로딩 실패

#### 증상
```
❌ 데이터 로딩 실패: HTTPError 429 Too Many Requests
```

#### 원인
- FRED API 요청 한도 초과 (120 requests/분)
- 캐시가 제대로 작동하지 않음

#### 해결 ✅

**app.py 확인:**
```python
@st.cache_data(ttl=3600)  # 1시간 캐시 확인
def load_data(api_key, days):
    ...
```

**임시 해결:**
- 브라우저 새로고침 대신 Streamlit 앱 내 버튼 사용
- 1분 대기 후 재시도

**영구 해결:**
- FRED API 키 갱신
- 캐시 TTL을 더 길게 설정 (예: 7200초 = 2시간)

---

### 4️⃣ 패키지 버전 충돌

#### 증상
```
ERROR: Cannot install pandas==2.2.3 and numpy==1.26.4
```

#### 원인
- 특정 버전 조합이 호환되지 않음

#### 해결 ✅

**유연한 버전 사용:**
```txt
# 고정 버전 (X)
pandas==2.2.3
numpy==1.26.4

# 유연한 버전 (O)
pandas>=2.0.0
numpy>=1.24.0
```

---

### 5️⃣ Plotly 차트가 표시되지 않음

#### 증상
- 차트 영역이 비어있음
- 콘솔에 에러 없음

#### 원인
- Plotly 버전 문제
- 브라우저 JavaScript 에러

#### 해결 ✅

**1. Plotly 버전 확인:**
```txt
plotly>=5.17.0
```

**2. 브라우저 캐시 삭제:**
- Ctrl+Shift+Delete (Chrome)
- 캐시 및 쿠키 삭제

**3. 차트 렌더링 방식 변경:**
```python
# app.py에서
st.plotly_chart(fig, use_container_width=True)
```

---

### 6️⃣ Streamlit Cloud 배포 실패

#### 증상
```
Error: Could not find a version that satisfies the requirement...
```

#### 원인
- requirements.txt 오타
- 패키지 이름 잘못 입력

#### 해결 ✅

**requirements.txt 검증:**
```bash
pip install -r requirements.txt
```

**일반적인 오타:**
```txt
# 잘못된 예
streamit (X)
ploty (X)
numpyy (X)

# 올바른 예
streamlit (O)
plotly (O)
numpy (O)
```

---

### 7️⃣ 메모리 에러

#### 증상
```
MemoryError: Unable to allocate array
```

#### 원인
- 너무 많은 데이터 로드 (5년치 이상)
- 캐시가 메모리를 너무 많이 사용

#### 해결 ✅

**데이터 기간 제한:**
```python
# app.py에서
period_options = {
    "최근 1년": 365,
    "최근 2년": 365*2,
    "최근 3년": 365*3,
    # "최근 5년": 365*5,  # 메모리 부족 시 제거
}
```

---

## 🔍 로그 확인 방법

### Streamlit Cloud에서:
1. 앱 화면 우측 하단 "Manage app" 클릭
2. Logs 탭 확인
3. 에러 메시지 전체 내용 확인

### 로컬 개발에서:
```bash
streamlit run app.py

# 터미널에 출력되는 에러 메시지 확인
```

---

## 🛠️ 디버깅 팁

### 1. Streamlit Cloud 로그 다운로드
```
Manage app → Logs → Download logs
```

### 2. 로컬에서 테스트
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 앱 실행
streamlit run app.py
```

### 3. 단계별 디버깅
```python
# app.py 상단에 추가
import streamlit as st

st.write("1. 패키지 로드 완료")

try:
    FRED_API_KEY = st.secrets["FRED_API_KEY"]
    st.write("2. API 키 로드 완료")
except Exception as e:
    st.error(f"API 키 에러: {e}")
    st.stop()

# 데이터 로드 전
st.write("3. 데이터 로드 시작...")
```

---

## 📞 추가 도움말

### Streamlit 공식 포럼
- https://discuss.streamlit.io/

### FRED API 문서
- https://fred.stlouisfed.org/docs/api/

### GitHub Issues
- 문제가 계속되면 repository에 Issue 생성

---

## ✅ 빠른 체크리스트

배포 전 확인사항:

- [ ] requirements.txt에 `kaleido` 없음
- [ ] requirements.txt 버전이 `>=` 형식
- [ ] .gitignore에 `secrets.toml` 포함
- [ ] Streamlit Cloud Secrets에 API 키 설정
- [ ] 로컬에서 정상 실행 확인
- [ ] GitHub에 최신 코드 푸시
- [ ] Streamlit Cloud에서 앱 재시작

---

**모든 문제가 해결되지 않으면 로그를 공유해주세요!** 📝
