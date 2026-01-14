"""
YouTube 크롤링 테스트 스크립트
키워드 기반 검색 및 자막 여부 확인 기능을 포함합니다.
"""

import os
import requests
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional
from youtube_transcript_api import YouTubeTranscriptApi

class SimpleYouTubeCrawler:
    """YouTube 크롤러 (키워드 검색, 이메일 추출, 자막 확인 지원)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    def extract_email(self, text: str) -> Optional[str]:
        """텍스트에서 이메일 주소 추출"""
        if not text: return "N/A"
        import re
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else "N/A"

    def check_subtitle_availability(self, video_id: str) -> bool:
        """영상에 한글 자막이 있는지 확인"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            # 한국어 자막이 있는지 우선 확인
            try:
                transcript_list.find_transcript(['ko'])
                return True
            except:
                # 한국어 자막이 없으면 수동/자동 생성된 자막 중 하나라도 있는지 확인
                return any(t.language_code == 'ko' or t.is_generated for t in transcript_list)
        except:
            return False

    def get_transcript(self, video_id: str) -> Optional[str]:
        """영상 자막 텍스트 추출"""
        try:
            # 한국어 자막 시도 -> 실패시 영어 자막 -> 실패시 첫 번째 자막
            try:
                transcript = YouTubeTranscriptApi.fetch_transcript(video_id, languages=['ko'])
            except:
                try:
                    transcript = YouTubeTranscriptApi.fetch_transcript(video_id, languages=['en'])
                except:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    transcript = transcript_list.find_transcript(['ko', 'en']).fetch()
            
            return " ".join([t['text'] for t in transcript])
        except:
            return None

    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """채널 상세 정보 가져오기"""
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
                
                return {
                    'subscriber_count': stats.get('subscriberCount', '0'),
                    'email': self.extract_email(description)
                }
            return None
        except:
            return None

    def get_video_statistics(self, video_id: str) -> Optional[Dict]:
        """영상 통계 정보 가져오기"""
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
        except:
            return None
    
    def search_videos_by_keyword(self, keyword: str, max_results: int = 5, days_back: int = 7) -> List[Dict]:
        """키워드 검색 및 자막 여부 포함 수집"""
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
                    
                    v_stats = self.get_video_statistics(video_id)
                    c_info = self.get_channel_info(channel_id)
                    has_subtitle = self.check_subtitle_availability(video_id)
                    
                    video_info = {
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt'],
                        'video_url': f"https://www.youtube.com/watch?v={video_id}",
                        'view_count': v_stats.get('view_count', '0') if v_stats else '0',
                        'channel_title': item['snippet']['channelTitle'],
                        'channel_id': channel_id,
                        'subscriber_count': c_info.get('subscriber_count', '0') if c_info else '0',
                        'email': c_info.get('email', 'N/A') if c_info else 'N/A',
                        'has_subtitle': has_subtitle
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
        
        return results
    
    def save_results(self, results: Dict):
        os.makedirs('data', exist_ok=True)
        filename = f"data/test_crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
