# 🔐 API 키 Streamlit Secrets 설정 가이드

## 📋 목차
1. [파일 구조](#파일-구조)
2. [로컬 개발 설정](#로컬-개발-설정)
3. [Streamlit Cloud 배포](#streamlit-cloud-배포)
4. [보안 체크리스트](#보안-체크리스트)

---

## 📁 파일 구조

```
project/
├── .streamlit/
│   └── secrets.toml        # API 키 저장 (로컬 전용)
├── .gitignore              # secrets.toml 제외
├── app.py                  # Streamlit 앱
├── requirements.txt        # 의존성
├── README.md              # 프로젝트 설명
└── DEPLOYMENT_GUIDE.md    # 이 파일
```

---

## 💻 로컬 개발 설정

### 1️⃣ secrets.toml 파일 생성

프로젝트 폴더에 `.streamlit` 디렉토리를 만들고 `secrets.toml` 파일 생성:

```bash
mkdir .streamlit
touch .streamlit/secrets.toml
```

### 2️⃣ API 키 입력

`.streamlit/secrets.toml` 파일에 다음 내용 작성:

```toml
# FRED API Key
FRED_API_KEY = "f1137018f7bb4b4150a5c84e09fc7fc2"
```

### 3️⃣ .gitignore 확인

`.gitignore` 파일에 다음이 포함되어 있는지 확인:

```
# Streamlit secrets
.streamlit/secrets.toml
secrets.toml
```

### 4️⃣ 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Streamlit Cloud 배포

### 📋 체크리스트
- [ ] GitHub에 코드 업로드 (secrets.toml 제외)
- [ ] Streamlit Cloud 계정 생성
- [ ] Repository 연결
- [ ] Secrets 설정

### 1️⃣ GitHub에 업로드

```bash
# Git 초기화
git init

# 원격 저장소 추가
git remote add origin https://github.com/사용자명/repository명.git

# 파일 추가 (.gitignore가 secrets.toml 제외)
git add .

# 커밋
git commit -m "Initial commit - FRED quant dashboard"

# 푸시
git push -u origin main
```

⚠️ **중요**: `secrets.toml` 파일이 업로드되지 않았는지 확인!

### 2️⃣ Streamlit Cloud 설정

1. **Streamlit Cloud 접속**
   - https://streamlit.io/cloud 방문
   - GitHub 계정으로 로그인

2. **New app 클릭**
   - Repository: 방금 생성한 repository 선택
   - Branch: `main`
   - Main file path: `app.py`

3. **Advanced settings 클릭**

4. **Secrets 설정**
   
   "Secrets" 섹션에 다음 내용 붙여넣기:
   
   ```toml
   # FRED API Key
   FRED_API_KEY = "f1137018f7bb4b4150a5c84e09fc7fc2"
   ```

5. **Deploy! 클릭**

### 3️⃣ 배포 확인

- 배포 완료까지 2-3분 소요
- 앱 URL 자동 생성: `https://사용자명-repository명.streamlit.app`
- 로그에서 에러 확인

---

## 🔒 보안 체크리스트

### ✅ 필수 확인사항

- [ ] `.gitignore`에 `secrets.toml` 포함
- [ ] GitHub에 `secrets.toml` 업로드되지 않음
- [ ] Streamlit Cloud Secrets에 API 키 설정 완료
- [ ] 로컬 `secrets.toml` 파일 백업

### ⚠️ 보안 팁

1. **API 키 노출 방지**
   ```bash
   # GitHub에 이미 업로드된 경우
   git rm --cached .streamlit/secrets.toml
   git commit -m "Remove secrets file"
   git push
   ```

2. **Public Repository 주의**
   - Public repository는 누구나 코드 열람 가능
   - API 키는 절대 코드에 직접 입력 금지
   - Secrets 기능만 사용

3. **API 키 관리**
   - 정기적으로 키 갱신
   - 사용하지 않는 키는 삭제
   - FRED API 무료 플랜: 120 requests/min

---

## 🐛 트러블슈팅

### 문제 1: "API 키를 찾을 수 없습니다" 에러

**원인**: Secrets 설정 안 됨

**해결**:
- 로컬: `.streamlit/secrets.toml` 파일 생성
- Cloud: 앱 설정 → Secrets에서 API 키 추가

### 문제 2: GitHub에 secrets.toml이 업로드됨

**해결**:
```bash
# 파일 제거
git rm --cached .streamlit/secrets.toml

# .gitignore 확인
echo ".streamlit/secrets.toml" >> .gitignore

# 커밋 및 푸시
git commit -m "Remove secrets and update gitignore"
git push
```

### 문제 3: Streamlit Cloud에서 데이터 로딩 실패

**원인**: API 키 오타 또는 잘못된 형식

**해결**:
- Secrets 섹션에서 `FRED_API_KEY` 이름 정확히 입력
- 따옴표 확인: `FRED_API_KEY = "키값"`
- 앱 재시작 (Reboot app)

---

## 📞 추가 도움말

### FRED API 키 발급
1. https://fred.stlouisfed.org/ 접속
2. "My Account" → "API Keys" → "Request API Key"
3. 무료 키 발급 (즉시 사용 가능)

### Streamlit 공식 문서
- Secrets 관리: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
- 배포 가이드: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app

---

## ✅ 최종 점검

배포 전 마지막 체크:

```bash
# 1. secrets.toml이 .gitignore에 있는지 확인
cat .gitignore | grep secrets

# 2. GitHub에 secrets.toml이 없는지 확인
git ls-files | grep secrets

# 3. 로컬 테스트
streamlit run app.py

# 4. 모두 정상이면 배포!
```

---

**🎉 배포 완료 후**
- 앱 URL 공유 가능
- API 키는 안전하게 숨겨짐
- 실시간 데이터 업데이트 확인

**문제가 있다면 Streamlit Cloud 로그를 확인하세요!**
