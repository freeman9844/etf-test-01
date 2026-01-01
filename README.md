# Global ETF Portfolio Tracker & Dividend Calendar

[![Cloud Run Deployment](https://img.shields.io/badge/Deployed-Cloud%20Run-blue?logo=google-cloud&logoColor=white)](https://etf-tracker-904902969656.asia-northeast3.run.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)

전 세계 ETF 포트폴리오를 실시간으로 관리하고 미래 배당금을 예측하는 대시보드 애플리케이션입니다.

## 🚀 주요 기능

- **실시간 포트폴리오 대시보드**: `yfinance` API를 통한 실시간 가격 및 수익률 추적.
- **배당 캘린더**: 향후 12개월의 예상 배당금을 그리드 형태의 카드로 시각화.
- **ETF 관리**: 간편한 종목 추가/수정/삭제 및 섹터(성향)별 분류.
- **Google Sheets 연동**: 표준 CSV 형식을 통한 포트폴리오 내보내기 및 일괄 가져오기 지원.
- **반응형 다크 모드 UI**: 세련된 카드 디자인 기반의 현대적 인터페이스.

## 🛠 기술 스택

- **Frontend**: [Streamlit](https://streamlit.io/) (Python Web Framework)
- **Data Engine**: [Pandas](https://pandas.pydata.org/), [yfinance](https://github.com/ranaroussi/yfinance)
- **Database**: SQLite (Local storage)
- **Visualization**: Plotly Express
- **Deployment**: Google Cloud Run (Dockerized)

## 📦 설치 및 로컬 실행 방법

### 1. 전제 조건
- Python 3.10 이상이 설치되어 있어야 합니다.

### 2. 가상환경 설정 및 라이브러리 설치
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 필수 라이브러리 설치
pip install -r etf_tracker/requirements.txt
```

### 3. 애플리케이션 실행
```bash
streamlit run etf_tracker/app.py
```

## ☁️ 클라우드 배포 (Cloud Run)

이 프로젝트는 Docker 컨테이너를 통해 Google Cloud Run에 배포할 수 있도록 구성되어 있습니다.

```bash
# Cloud Run 배포 명령
gcloud run deploy etf-tracker --source . --platform managed --region asia-northeast3 --allow-unauthenticated
```

> [!WARNING]
> 현재 Cloud Run 버전은 로컬 SQLite를 사용하므로 컨테이너 재시작 시 데이터가 유지되지 않습니다. 영구 보존이 필요한 경우 Supabase 또는 Cloud SQL 연동이 필요합니다.

## 📄 라이선스
이 프로젝트는 교육 및 개인 용도로 제작되었습니다.
