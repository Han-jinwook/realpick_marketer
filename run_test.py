"""
YouTube 크롤링 테스트 실행 스크립트
API 키 없이도 기본적인 구조를 테스트할 수 있습니다.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def check_environment():
    """환경 설정 확인"""
    print("환경 설정 확인 중...")
    
    # 필요한 폴더 확인
    folders = ['data', 'modules', 'config']
    for folder in folders:
        if not os.path.exists(folder):
            print(f"폴더 생성: {folder}")
            os.makedirs(folder)
        else:
            print(f"폴더 존재: {folder}")
    
    # API 키 확인
    youtube_api = os.getenv('YOUTUBE_API_KEY')
    gemini_api = os.getenv('GEMINI_API_KEY')
    
    print(f"\nAPI 키 상태:")
    print(f"  YouTube API: {'설정됨' if youtube_api else '미설정'}")
    print(f"  Gemini API: {'설정됨' if gemini_api else '미설정'}")
    
    return youtube_api, gemini_api

def run_mock_test():
    """모의 테스트 실행 (API 키 없이)"""
    print("\n모의 크롤링 테스트 실행...")
    
    # 가짜 결과 생성
    mock_results = {
        'crawl_time': datetime.now().isoformat(),
        'total_channels': 5,
        'successful_channels': 5,
        'total_videos': 12,
        'channels': {
            '나는솔로': {
                'status': 'success',
                'channel_info': {
                    'channel_id': 'mock_channel_1',
                    'channel_title': '나는솔로 공식',
                    'description': '나는솔로 공식 채널입니다...'
                },
                'videos': [
                    {
                        'video_id': 'mock_video_1',
                        'title': '나솔 15기 3화 - 영수와 영희의 달달한 데이트',
                        'description': '이번 화에서는 영수와 영희가...',
                        'published_at': '2024-01-08T10:00:00Z',
                        'video_url': 'https://youtube.com/watch?v=mock_video_1'
                    },
                    {
                        'video_id': 'mock_video_2', 
                        'title': '나솔 15기 4화 미리보기',
                        'description': '다음 화 예고편...',
                        'published_at': '2024-01-09T15:00:00Z',
                        'video_url': 'https://youtube.com/watch?v=mock_video_2'
                    }
                ],
                'video_count': 2
            },
            '돌싱글즈': {
                'status': 'success',
                'channel_info': {
                    'channel_id': 'mock_channel_2',
                    'channel_title': '돌싱글즈 공식',
                    'description': '돌싱글즈 공식 채널입니다...'
                },
                'videos': [
                    {
                        'video_id': 'mock_video_3',
                        'title': '돌싱글즈 시즌3 하이라이트',
                        'description': '시즌3의 명장면들을...',
                        'published_at': '2024-01-07T20:00:00Z',
                        'video_url': 'https://youtube.com/watch?v=mock_video_3'
                    }
                ],
                'video_count': 1
            }
        }
    }
    
    # 결과 저장
    import json
    filename = f"data/mock_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(mock_results, f, ensure_ascii=False, indent=2)
    
    print(f"모의 테스트 완료!")
    print(f"결과: {mock_results['successful_channels']}/{mock_results['total_channels']} 채널, {mock_results['total_videos']}개 영상")
    print(f"결과 저장: {filename}")
    
    return mock_results

def run_real_test():
    """실제 API 테스트 실행"""
    print("\n실제 YouTube API 테스트 실행...")
    
    try:
        from test_crawler import SimpleYouTubeCrawler
        
        api_key = os.getenv('YOUTUBE_API_KEY')
        test_channels = ["나는솔로", "돌싱글즈", "하트시그널", "SBS Entertainment", "MBC Entertainment"]
        
        crawler = SimpleYouTubeCrawler(api_key)
        results = crawler.test_crawl(test_channels)
        crawler.save_results(results)
        
        return results
        
    except Exception as e:
        print(f"실제 테스트 오류: {e}")
        return None

def main():
    """메인 실행 함수"""
    print("리얼픽 YouTube 크롤링 테스트")
    print("=" * 50)
    
    # 환경 확인
    youtube_api, gemini_api = check_environment()
    
    # 테스트 선택
    if youtube_api:
        print("\n📋 테스트 옵션:")
        print("1. 실제 API 테스트")
        print("2. 모의 테스트")
        
        choice = input("\n선택하세요 (1 또는 2, 기본값: 1): ").strip()
        
        if choice == "2":
            results = run_mock_test()
        else:
            results = run_real_test()
    else:
        print("\nYouTube API 키가 없어서 모의 테스트를 실행합니다.")
        results = run_mock_test()
    
    if results:
        print(f"\n테스트 완료!")
        print(f"성공률: {results['successful_channels']}/{results['total_channels']} ({results['successful_channels']/results['total_channels']*100:.1f}%)")
        
        # Streamlit 앱 실행 안내
        print(f"\n웹 인터페이스 실행:")
        print(f"  streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
