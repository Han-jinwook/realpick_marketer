"""
YouTube 크롤링 테스트 스크립트
자동 생성 자막(Auto-generated) 수집 기능을 대폭 강화했습니다.
"""

import os
import requests
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional
from youtube_transcript_api import YouTubeTranscriptApi

class SimpleYouTubeCrawler:
    """YouTube 크롤러 (자동 자막 수집 강화 버전)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    def extract_email(self, text: str) -> Optional[str]:
        if not text: return "N/A"
        import re
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else "N/A"

    def check_subtitle_availability(self, video_id: str) -> bool:
        """영상에 자막(수동 또는 자동 생성)이 있는지 확인"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            # 1. 한국어 자막(수동/자동)이 있는지 확인
            try:
                transcript_list.find_transcript(['ko'])
                return True
            except:
                # 2. 영어 등 다른 언어라도 자동 생성 자막이 있는지 확인
                return any(t.is_generated or t.language_code.startswith('ko') for t in transcript_list)
        except:
            return False

    def get_transcript(self, video_id: str) -> Optional[str]:
        """자동 생성 자막을 포함하여 가능한 모든 자막 텍스트 추출"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 우선순위: 수동 한국어 -> 자동 한국어 -> 자동 영어 -> 번역된 한국어
            try:
                # 한국어 자막 시도
                transcript = transcript_list.find_transcript(['ko']).fetch()
            except:
                try:
                    # 한국어가 없으면 영어를 가져와서 한국어로 번역 시도
                    transcript = transcript_list.find_transcript(['en']).translate('ko').fetch()
                except:
                    # 그것도 안되면 그냥 존재하는 첫 번째 자막 가져오기
                    transcript = next(iter(transcript_list)).fetch()
            
            return " ".join([t['text'] for t in transcript])
        except Exception as e:
            print(f"자막 추출 실패 ({video_id}): {e}")
            return None

    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        url = f"{self.base_url}/channels"
        params = {'part': 'snippet,statistics', 'id': channel_id, 'key': self.api_key}
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                item = data['items'][0]
                return {
                    'subscriber_count': item['statistics'].get('subscriberCount', '0'),
                    'email': self.extract_email(item['snippet'].get('description', ''))
                }
            return None
        except: return None

    def get_video_statistics(self, video_id: str) -> Optional[Dict]:
        url = f"{self.base_url}/videos"
        params = {'part': 'statistics', 'id': video_id, 'key': self.api_key}
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                return {'view_count': data['items'][0]['statistics'].get('viewCount', '0')}
            return None
        except: return None
    
    def search_videos_by_keyword(self, keyword: str, max_results: int = 5, days_back: int = 7) -> List[Dict]:
        url = f"{self.base_url}/search"
        after_date = (datetime.now() - timedelta(days=days_back)).isoformat() + 'Z'
        params = {
            'part': 'snippet', 'q': keyword, 'type': 'video', 
            'order': 'relevance', 'maxResults': max_results, 
            'key': self.api_key, 'publishedAfter': after_date
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            videos = []
            if 'items' in data:
                for item in data['items']:
                    video_id = item['id']['videoId']
                    v_stats = self.get_video_statistics(video_id)
                    c_info = self.get_channel_info(item['snippet']['channelId'])
                    has_subtitle = self.check_subtitle_availability(video_id)
                    
                    videos.append({
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'video_url': f"https://www.youtube.com/watch?v={video_id}",
                        'view_count': v_stats.get('view_count', '0') if v_stats else '0',
                        'channel_title': item['snippet']['channelTitle'],
                        'subscriber_count': c_info.get('subscriber_count', '0') if c_info else '0',
                        'email': c_info.get('email', 'N/A') if c_info else 'N/A',
                        'has_subtitle': has_subtitle,
                        'published_at': item['snippet']['publishedAt']
                    })
            return videos
        except Exception as e:
            print(f"검색 오류: {e}")
            return []
    
    def test_crawl(self, keywords: List[str], max_results: int = 5, days_back: int = 7) -> Dict:
        results = {'crawl_time': datetime.now().isoformat(), 'total_videos': 0, 'channels': {}}
        for keyword in keywords:
            if not keyword: continue
            videos = self.search_videos_by_keyword(keyword, max_results=max_results, days_back=days_back)
            if videos:
                results['channels'][keyword] = {'status': 'success', 'videos': videos, 'video_count': len(videos)}
                results['total_videos'] += len(videos)
        return results
    
    def save_results(self, results: Dict):
        os.makedirs('data', exist_ok=True)
        filename = f"data/test_crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
