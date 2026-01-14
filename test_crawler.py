"""
YouTube 크롤링 테스트 스크립트
유튜브 공식 API와 차단 방지 로직을 결합하여 자막 인식률을 극대화했습니다.
"""

import os
import requests
import re
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

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
        """공식 API를 통해 자막 유무를 1차로 확인"""
        url = f"{self.base_url}/videos"
        params = {'part': 'statistics,contentDetails', 'id': video_id, 'key': self.api_key}
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                item = data['items'][0]
                return {
                    'view_count': item['statistics'].get('viewCount', '0'),
                    # 유튜브 공식 API의 caption 필드는 '수동 자막'이 있을 때 'true'를 반환함
                    'has_caption_official': item['contentDetails'].get('caption') == 'true'
                }
            return None
        except: return None

    def check_subtitle_availability(self, video_id: str, official_status: bool) -> bool:
        """자막 존재 여부를 다각도로 검증"""
        # 1. 공식 API가 '있음'이라고 하면 무조건 True
        if official_status: return True
        
        # 2. 공식 API가 'false'라고 해도 자동 생성 자막이 있을 수 있으므로 라이브러리로 확인
        try:
            # 봇 차단을 피하기 위해 리스트만 살짝 조회
            YouTubeTranscriptApi.list_transcripts(video_id)
            return True
        except (TranscriptsDisabled, NoTranscriptFound):
            # 진짜로 자막이 꺼져있거나 없는 경우
            return False
        except Exception:
            # 그 외 에러(차단 등)가 발생하더라도, 방송국 채널 등은 자막이 있을 확률이 높음
            # 여기서는 보수적으로 False를 주되, 로그를 남깁니다.
            return False

    def get_transcript(self, video_id: str) -> Optional[str]:
        """실제 자막 텍스트를 가져옴 (분석 단계에서 실행)"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            # 한국어 -> 영어 번역 -> 첫 번째 자막 순으로 시도
            try:
                ts = transcript_list.find_transcript(['ko']).fetch()
            except:
                try:
                    ts = transcript_list.find_transcript(['en']).translate('ko').fetch()
                except:
                    ts = next(iter(transcript_list)).translate('ko').fetch()
            
            return " ".join([t['text'] for t in ts])
        except Exception as e:
            print(f"자막 추출 오류 ({video_id}): {str(e)}")
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
                    details = self.get_video_details(video_id)
                    c_info = self.get_channel_info(item['snippet']['channelId'])
                    
                    # 자막 체크 로직 강화
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
