import argparse
import os
import sys
from dotenv import load_dotenv
from pipeline import AutomationPipeline

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="🚀 Antigravity eBay Automation CLI")
    
    # 주요 명령어 그룹
    subparsers = parser.add_subparsers(dest="command", help="실행할 명령어를 선택하세요")

    # 1. Sourcing 명령어
    source_parser = subparsers.add_parser("source", help="상품 정보 수집")
    source_parser.add_argument("--url", required=True, help="수집할 상품 URL (무신사 등)")

    # 2. AI Processing 명령어
    process_parser = subparsers.add_parser("process", help="AI 이미지 정제 및 분석")
    process_parser.add_argument("--path", required=True, help="이미지 파일 경로 또는 상품 ID")

    # 3. Full Pipeline 명령어 (수집 + AI + 리스팅)
    full_parser = subparsers.add_parser("auto", help="수집부터 리스팅까지 자동 실행")
    full_parser.add_argument("--url", required=True, help="시작할 상품 URL")
    full_parser.add_argument("--list", action="store_true", help="실제 eBay 등록까지 진행")

    args = parser.parse_args()

    # 파이프라인 초기화
    pipeline = AutomationPipeline()

    if args.command == "source":
        print(f"🔍 상품 수집 시작: {args.url}")
        result = pipeline.sourcing_engine.scrape_product(args.url)
        if result:
            print(f"✅ 수집 완료: {result['title']} ({result['price']}원)")
        else:
            print("❌ 수집 실패")

    elif args.command == "process":
        print(f"🎨 AI 이미지 처리 시작: {args.path}")
        # pipeline.ai_studio 를 통한 처리 로직 실행
        pass

    elif args.command == "auto":
        print(f"🚀 전체 자동화 파이프라인 가동: {args.url}")
        pipeline.run_full_pipeline(args.url)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
