# 🚀 eBay & Shopify AI Automation SaaS (Project DOBI)

AI를 활용하여 한국의 인기 상품(K-Goods)을 수집하고, 고품질 이미지를 생성하여 글로벌 마켓(eBay, Shopify 등)에 자동으로 리스팅하는 SaaS 솔루션입니다.

## 📅 최신 업데이트 (2026-04-27)

### 🌟 주요 성과
1.  **Antigravity CLI 구현**: 터미널 명령어를 통해 수집(`source`), AI 처리(`process`), 자동화(`auto`)를 제어할 수 있는 인터페이스 구축.
2.  **보안 및 인프라 강화**: `.gitignore`를 통한 API 키 유출 방지 및 `.env` 기반의 환경 변수 관리 체계 도입.
3.  **eBay API Sandbox 연동**: OAuth 2.0 인증 흐름 및 Inventory API 리스팅 파이프라인 기초 공사 완료.
4.  **AI 이미지 엔진 최적화**: `rembg`를 활용한 배경 제거 및 `Alpha Matting` 적용으로 전문 스튜디오급 제품 이미지 자동 생성.

### 🛠 기술 스택
- **Language**: Python 3.9+
- **AI**: rembg (ISNet general use), GPT-4/Gemini (Planned)
- **Database**: SQLite3
- **Automation**: eBay RESTful Inventory API, Scrapy/BS4

---

## 🚀 향후 로드맵 (Roadmap)

### Phase 1: 멀티 소싱 엔진 확장 (진행 중)
- [x] 무신사 (Musinsa)
- [ ] KREAM, 솔드아웃 (Limited Edition)
- [ ] 에이블리, 올리브영 (Fashion & Beauty)
- [ ] 포이즌 (Poison/Dewu - Global Sourcing)
- [ ] 쿠팡, 네이버 스마트스토어

### Phase 2: AI 비전 및 SEO 최적화
- **GPT-4 Integration**: 수집된 상품 정보를 바탕으로 검색 최적화(SEO)된 영문 제목 및 상세 설명 자동 생성.
- **Image Enhancement**: 저화질 원본 이미지를 고화질로 업스케일링.

### Phase 3: 멀티 채널 리스팅
- **Shopify Admin API**: 자사몰(Shopify) 동시 등록 기능.
- **국내 마켓 연동**: 쿠팡, 스마트스토어, 11번가 등 국내외 통합 관리 시스템 구축.

---

## 💻 실행 방법
```bash
# 상품 자동화 파이프라인 실행
python3 main.py auto --url "상품_상세_URL"
```

## 🛡 보안 공지
- API 키와 개인정보는 `.env` 파일에 보관하며, 절대 버전 관리 시스템(Git)에 포함되지 않습니다.

## 📌 최근 작업 로그

- **Bulk registration**: `main.py`에 `--file` 옵션을 추가해 텍스트 파일에 있는 URL들을 한 번에 처리하도록 구현했습니다.
- **Desktop GUI**: `gui_tkinter.py` (standard `tkinter`) 로 macOS 12 이하에서도 동작하는 그래픽 인터페이스를 제공했습니다.
- **Title 길이 보정**: eBay API 요구사항에 맞춰 상품 제목을 자동 정제하도록 `pipeline.py`를 개선했습니다.
- **Git 자동 커밋 & 푸시**: 현재 작업을 커밋하고 원격 저장소(GitHub)로 푸시했습니다.

---

> 이 프로젝트는 오픈소스이며, 자유롭게 포크·기여 가능합니다.
