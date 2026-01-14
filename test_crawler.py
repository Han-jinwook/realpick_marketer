"""
YouTube 크롤링 테스트 스크립트
공식 API와 우회 로직을 결합하여 자막 수집 성공률을 극대화했습니다.
"""

import os
import requests
import re
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional
from youtube_transcript_api import YouTubeTranscriptApi

class SimpleYouTubeCrawler:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    def extract_email(self, text: str) -> Optional[str]:
        if not text: return "N/A"
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else "N/A"

    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """공식 API를 통해 조회수와 자막 유무를 한 번에 확인"""
        url = f"{self.base_url}/videos"
        # contentDetails 파트에서 자막 존재 여부(caption)를 공식적으로 제공함
        params = {'part': 'statistics,contentDetails', 'id': video_id, 'key': self.api_key}
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                item = data['items'][0]
                return {
                    'view_count': item['statistics'].get('viewCount', '0'),
                    'has_caption_official': item['contentDetails'].get('caption') == 'true'
                }
            return None
        except: return None

    def check_subtitle_availability(self, video_id: str, official_status: bool) -> bool:
        """공식 상태가 True면 우선 True 반환, 아니면 라이브러리로 한 번 더 체크"""
        if official_status: return True
        try:
            YouTubeTranscriptApi.list_transcripts(video_id)
            return True
        except:
            return False

    def get_transcript(self, video_id: str) -> Optional[str]:
        """모든 수단을 동원해 자막 추출 (자동 생성 포함)"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                # 1. 한국어 (수동/자동)
                transcript = transcript_list.find_transcript(['ko']).fetch()
            except:
                try:
                    # 2. 영어 -> 한국어 번역
                    transcript = transcript_list.find_transcript(['en']).translate('ko').fetch()
                except:
                    # 3. 존재하는 첫 번째 자막 -> 한국어 번역
                    transcript = next(iter(transcript_list)).translate('ko').fetch()
            
            return " ".join([t['text'] for t in transcript])
        except Exception as e:
            print(f"추출 실패 ({video_id}): {str(e)}")
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
                    # 공식 상세 정보 가져오기
                    details = self.get_video_details(video_id)
                    c_info = self.get_channel_info(item['snippet']['channelId'])
                    
                    # 자막 여부 최종 판단
                    has_sub = self.check_subtitle_availability(video_id, details['has_caption_official'] if details else False)
                    
                    videos.append({
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'video_url': f"https://www.youtube.com/watch?v={video_id}",
                        'view_count': details['view_count'] if details else '0',
                        'channel_title': item['snippet']['channelTitle'],
                        'subscriber_count': c_info.get('subscriber_count', '0') if c_info else '0',
                        'email': c_info.get('email', 'N/A') if c_info else 'N/A',
                        'has_subtitle': has_sub,
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
