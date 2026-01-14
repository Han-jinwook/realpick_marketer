"""
YouTube 크롤링 테스트 스크립트
유튜브의 모든 자막(수동, 자동 생성, 자동 번역)을 강제로 찾아내는 고성능 버전입니다.
"""

import os
import requests
import re
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

class SimpleYouTubeCrawler:
    """YouTube 크롤러 (자막 수집 최적화)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    def extract_email(self, text: str) -> Optional[str]:
        if not text: return "N/A"
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else "N/A"

    def check_subtitle_availability(self, video_id: str) -> bool:
        """어떤 언어든, 자동 생성이든 자막이 하나라도 있는지 끝까지 확인"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            # 리스트가 존재하면 수동/자동 자막이 있다는 뜻입니다.
            return True
        except (TranscriptsDisabled, NoTranscriptFound):
            # 자막 기능 자체가 꺼져있거나 없는 경우
            return False
        except Exception as e:
            # 그 외 차단 등의 사유로 못 가져오는 경우
            print(f"자막 체크 중 예외 발생 ({video_id}): {str(e)}")
            return False

    def get_transcript(self, video_id: str) -> Optional[str]:
        """모든 수단을 동원해 자막 내용을 텍스트로 추출"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 시도 순서:
            # 1. 한국어 (수동/자동)
            # 2. 영어 (수동/자동) -> 한국어 번역
            # 3. 그 외 존재하는 아무 자막 -> 한국어 번역
            
            try:
                # 1단계: 한국어 시도
                transcript = transcript_list.find_transcript(['ko', 'ko-KR', 'ko-Hans', 'ko-Hant']).fetch()
            except:
                try:
                    # 2단계: 영어 가져와서 한국어로 번역
                    transcript = transcript_list.find_transcript(['en']).translate('ko').fetch()
                except:
                    # 3단계: 아무거나 가져와서 한국어로 번역
                    first_ts = next(iter(transcript_list))
                    transcript = first_ts.translate('ko').fetch()
            
            return " ".join([t['text'] for t in transcript])
        except Exception as e:
            print(f"자막 최종 추출 실패 ({video_id}): {str(e)}")
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
                    
                    # 여기가 핵심: 자막 여부 체크
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
