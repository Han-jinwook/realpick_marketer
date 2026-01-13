"""
간단한 YouTube API 테스트
5개 채널만 빠르게 테스트
"""

import os
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_youtube_api():
    """YouTube API 키 테스트"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key or api_key == 'your_youtube_api_key_here':
        print("❌ YouTube API 키가 설정되지 않았습니다!")
        print("📝 .env 파일에서 YOUTUBE_API_KEY를 실제 키로 변경해주세요.")
        return False
    
    print(f"✅ API 키 확인됨: {api_key[:10]}...")
    
    # 간단한 API 테스트
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': '나는솔로',
        'type': 'channel',
        'key': api_key,
        'maxResults': 1
    }
    
    try:
        print("🔍 YouTube API 연결 테스트 중...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                channel = data['items'][0]['snippet']
                print(f"✅ API 연결 성공!")
                print(f"📺 찾은 채널: {channel['channelTitle']}")
                return True
            else:
                print("⚠️ 검색 결과가 없습니다.")
                return False
        else:
            print(f"❌ API 오류: {response.status_code}")
            print(f"오류 내용: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        return False

def quick_channel_test():
    """5개 채널 빠른 테스트"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key or api_key == 'your_youtube_api_key_here':
        print("❌ API 키를 먼저 설정해주세요!")
        return
    
    test_channels = ["나는솔로", "돌싱글즈", "하트시그널", "SBS Entertainment", "MBC Entertainment"]
    
    print(f"\n🚀 {len(test_channels)}개 채널 빠른 테스트 시작...")
    
    results = []
    
    for i, channel_name in enumerate(test_channels, 1):
        print(f"\n[{i}/{len(test_channels)}] {channel_name} 검색 중...")
        
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': channel_name,
            'type': 'channel',
            'key': api_key,
            'maxResults': 1
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and len(data['items']) > 0:
                    channel = data['items'][0]['snippet']
                    result = {
                        'name': channel_name,
                        'found': True,
                        'channel_title': channel['channelTitle'],
                        'channel_id': channel['channelId']
                    }
                    print(f"  ✅ 찾음: {channel['channelTitle']}")
                else:
                    result = {'name': channel_name, 'found': False}
                    print(f"  ❌ 못찾음")
            else:
                result = {'name': channel_name, 'found': False, 'error': response.status_code}
                print(f"  ❌ 오류: {response.status_code}")
                
        except Exception as e:
            result = {'name': channel_name, 'found': False, 'error': str(e)}
            print(f"  ❌ 오류: {e}")
        
        results.append(result)
    
    # 결과 요약
    found_count = sum(1 for r in results if r.get('found', False))
    print(f"\n📊 테스트 완료!")
    print(f"성공: {found_count}/{len(test_channels)} 채널")
    
    for result in results:
        status = "✅" if result.get('found') else "❌"
        title = result.get('channel_title', '찾을 수 없음')
        print(f"  {status} {result['name']}: {title}")

if __name__ == "__main__":
    print("🎯 YouTube API 빠른 테스트")
    print("=" * 40)
    
    # 1단계: API 키 테스트
    if test_youtube_api():
        # 2단계: 채널 검색 테스트
        quick_channel_test()
    else:
        print("\n💡 API 키를 설정한 후 다시 실행해주세요!")
        print("1. .env 파일을 열어주세요")
        print("2. YOUTUBE_API_KEY=your_youtube_api_key_here")
        print("3. 'your_youtube_api_key_here'를 실제 API 키로 변경")
        print("4. 파일 저장 후 다시 실행")

