# 📅 타이칸 일정 대시보드 — 설치 & 설정 가이드

---

## 📁 폴더 구조

```
schedule-dashboard/          ← 프로젝트 루트 (GitHub 저장소)
├── index.html               ← 대시보드 웹페이지 (GitHub Pages로 배포)
├── schedule.json            ← 일정 데이터 (Python이 자동 갱신)
├── main.py                  ← 관리자 도구 (VS Code에서 실행)
├── requirements.txt         ← Python 의존성
├── .gitignore               ← 민감 정보 제외 설정
└── README.md                ← 이 파일
```

---

## 🚀 단계별 설정

### STEP 1 — GitHub 저장소 생성

1. https://github.com/new 접속
2. Repository name: `taycan-schedule` (원하는 이름)
3. **Public** 선택 (GitHub Pages 무료 플랜은 Public 필요)
4. **Create repository** 클릭

---

### STEP 2 — Personal Access Token 발급

> ⚠️ 토큰은 발급 시 한 번만 보입니다. 반드시 복사해 두세요.

1. GitHub 우측 상단 프로필 → **Settings**
2. 좌측 하단 **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. **Generate new token (classic)** 클릭
5. Note: `taycan-dashboard`
6. Expiration: `No expiration` (또는 원하는 기간)
7. Scope: ☑ **repo** (전체 체크)
8. **Generate token** → 토큰 복사 (`ghp_xxxxxxxxxxxx`)

---

### STEP 3 — 로컬 Git 설정 (VS Code 터미널)

```bash
# 프로젝트 폴더로 이동
cd schedule-dashboard

# Git 초기화 및 원격 저장소 연결
git init
git remote add origin https://github.com/YOUR_USERNAME/taycan-schedule.git

# 토큰을 사용한 인증 URL 설정 (토큰을 URL에 포함)
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/taycan-schedule.git
```

> 💡 `YOUR_TOKEN`과 `YOUR_USERNAME`을 실제 값으로 교체하세요.

---

### STEP 4 — 최초 Push

```bash
# VS Code 터미널에서
git add .
git commit -m "🚀 초기 설정"
git branch -M main
git push -u origin main
```

---

### STEP 5 — GitHub Pages 활성화

1. 저장소 페이지 → **Settings** 탭
2. 좌측 **Pages** 메뉴
3. Source: **Deploy from a branch**
4. Branch: **main** / **/ (root)**
5. **Save** 클릭
6. 약 1~2분 후 URL 생성:  
   `https://YOUR_USERNAME.github.io/taycan-schedule/`

---

### STEP 6 — Python 환경 설정

```bash
# VS Code 터미널에서
pip install gitpython

# 또는 가상환경 사용 시
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

---

### STEP 7 — 관리자 도구 실행

```bash
python main.py
```

GUI 창이 열리면:
1. 날짜, 시간, 제목, 장소, 비고 입력
2. **✚ 일정 추가** 클릭
3. 원하는 만큼 추가 후 **⬆ 저장 & GitHub Push** 클릭
4. 약 1~2분 후 대시보드에 반영됨

---

## 🔐 보안 체크리스트

- [ ] `.gitignore`에 `.env` 포함 확인
- [ ] 토큰을 코드에 직접 하드코딩하지 않음
- [ ] Git remote URL에 토큰 포함 방식 사용 (로컬 only)
- [ ] 저장소를 Private으로 운영할 경우 → GitHub Pages를 GitHub Pro에서 사용하거나 Cloudflare Pages 대안 고려

---

## 🖥️ 대시보드 접속

| 디바이스 | URL |
|---------|-----|
| 태블릿 | `https://YOUR_USERNAME.github.io/taycan-schedule/` |
| 타이칸 RSE | 동일 URL (브라우저 입력) |

> 대시보드는 **매 1분마다** 자동으로 최신 일정을 불러옵니다.

---

## ❓ 문제 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| Push 오류 `403` | 토큰 만료 또는 scope 부족 | 새 토큰 발급 후 remote URL 재설정 |
| 대시보드 업데이트 안 됨 | GitHub Pages 캐시 | 강제 새로고침 `Ctrl+Shift+R` |
| `GitPython` 오류 | 라이브러리 미설치 | `pip install gitpython` |
| GUI 창 안 열림 | tkinter 없음 | `python -m tkinter` 으로 확인 |
