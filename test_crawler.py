"""
YouTube 크롤링 테스트 스크립트
키워드 기반 검색 기능을 강화하고 이메일 추출 로직을 추가했습니다.
"""

import os
import requests
import re
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional

class SimpleYouTubeCrawler:
    """YouTube 크롤러 (키워드 검색 및 이메일 추출 지원)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    def extract_email(self, text: str) -> Optional[str]:
        """텍스트에서 이메일 주소 추출 (정규식 사용)"""
        if not text: return None
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else "N/A"

    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """채널의 상세 정보(설명, 구독자 수 등) 가져오기"""
        url = f"{self.base_url}/channels"
        params = {
            'part': 'snippet,statistics',
            'id': channel_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data and len(data['items']) > 0:
                item = data['items'][0]
                snippet = item['snippet']
                stats = item['statistics']
                
                description = snippet.get('description', '')
                email = self.extract_email(description)
                
                return {
                    'subscriber_count': stats.get('subscriberCount', '0'),
                    'description': description,
                    'email': email,
                    'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url', '')
                }
            return None
        except Exception:
            return None

    def get_video_statistics(self, video_id: str) -> Optional[Dict]:
        """영상의 통계 정보 가져오기"""
        url = f"{self.base_url}/videos"
        params = {
            'part': 'statistics',
            'id': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data and len(data['items']) > 0:
                stats = data['items'][0]['statistics']
                return {
                    'view_count': stats.get('viewCount', '0')
                }
            return None
        except Exception:
            return None
    
    def search_videos_by_keyword(self, keyword: str, max_results: int = 5, days_back: int = 7) -> List[Dict]:
        """키워드로 관련 영상 검색 및 상세 정보(이메일 포함) 수집"""
        print(f"🔎 키워드 검색 중: {keyword}")
        
        url = f"{self.base_url}/search"
        after_date = (datetime.now() - timedelta(days=days_back)).isoformat() + 'Z'
        
        params = {
            'part': 'snippet',
            'q': keyword,
            'type': 'video',
            'order': 'relevance',
            'maxResults': max_results,
            'key': self.api_key,
            'publishedAfter': after_date
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            videos = []
            if 'items' in data:
                for item in data['items']:
                    video_id = item['id']['videoId']
                    channel_id = item['snippet']['channelId']
                    
                    # 상세 정보 수집 (영상 통계 + 채널 정보)
                    v_stats = self.get_video_statistics(video_id)
                    c_info = self.get_channel_info(channel_id)
                    
                    video_info = {
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'published_at': item['snippet']['publishedAt'],
                        'video_url': f"https://www.youtube.com/watch?v={video_id}",
                        'view_count': v_stats.get('view_count', '0') if v_stats else '0',
                        'channel_title': item['snippet']['channelTitle'],
                        'channel_id': channel_id,
                        'subscriber_count': c_info.get('subscriber_count', '0') if c_info else '0',
                        'email': c_info.get('email', 'N/A') if c_info else 'N/A'
                    }
                    videos.append(video_info)
            return videos
        except Exception as e:
            print(f"❌ 검색 오류: {e}")
            return []
    
    def test_crawl(self, keywords: List[str], max_results: int = 5, days_back: int = 7) -> Dict:
        results = {
            'crawl_time': datetime.now().isoformat(),
            'total_videos': 0,
            'channels': {}
        }
        
        for keyword in keywords:
            if not keyword: continue
            videos = self.search_videos_by_keyword(keyword, max_results=max_results, days_back=days_back)
            if videos:
                results['channels'][keyword] = {
                    'status': 'success',
                    'videos': videos,
                    'video_count': len(videos)
                }
                results['total_videos'] += len(videos)
        
        results['total_channels'] = len(keywords)
        results['successful_channels'] = len([k for k, v in results['channels'].items() if v['status'] == 'success'])
        return results
    
    def save_results(self, results: Dict):
        os.makedirs('data', exist_ok=True)
        filename = f"data/test_crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    api_key = os.getenv('YOUTUBE_API_KEY')
    if api_key:
        crawler = SimpleYouTubeCrawler(api_key)
        res = crawler.test_crawl(["환승연애"])
        crawler.save_results(res)
