"""
YouTube 크롤링 모듈
유튜브 채널의 최신 영상 정보를 수집합니다.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class YouTubeCrawler:
    """YouTube API를 사용한 채널 크롤링 클래스"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    def get_channel_id(self, channel_name: str) -> Optional[str]:
        """채널명으로 채널 ID 검색"""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'q': channel_name,
            'type': 'channel',
            'key': self.api_key,
            'maxResults': 1
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'items' in data and len(data['items']) > 0:
                return data['items'][0]['snippet']['channelId']
            return None
            
        except Exception as e:
            print(f"채널 ID 검색 오류: {e}")
            return None
    
    def get_recent_videos(self, channel_id: str, max_results: int = 10) -> List[Dict]:
        """채널의 최근 영상 목록 가져오기"""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'channelId': channel_id,
            'type': 'video',
            'order': 'date',
            'maxResults': max_results,
            'key': self.api_key,
            'publishedAfter': (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            videos = []
            if 'items' in data:
                for item in data['items']:
                    video_info = {
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt'],
                        'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                        'channel_title': item['snippet']['channelTitle']
                    }
                    
                    # 영상 상세 정보 가져오기
                    video_details = self.get_video_details(video_info['video_id'])
                    if video_details:
                        video_info.update(video_details)
                    
                    videos.append(video_info)
            
            return videos
            
        except Exception as e:
            print(f"영상 목록 가져오기 오류: {e}")
            return []
    
    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """영상 상세 정보 가져오기"""
        url = f"{self.base_url}/videos"
        params = {
            'part': 'statistics,contentDetails',
            'id': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'items' in data and len(data['items']) > 0:
                item = data['items'][0]
                return {
                    'view_count': item['statistics'].get('viewCount', '0'),
                    'like_count': item['statistics'].get('likeCount', '0'),
                    'comment_count': item['statistics'].get('commentCount', '0'),
                    'duration': item['contentDetails']['duration']
                }
            return None
            
        except Exception as e:
            print(f"영상 상세 정보 오류: {e}")
            return None
    
    def get_video_transcript(self, video_id: str) -> Optional[str]:
        """영상 자막 가져오기 (YouTube API로는 제한적, 추후 youtube-transcript-api 사용)"""
        # TODO: youtube-transcript-api 라이브러리 사용하여 자막 추출
        # 현재는 플레이스홀더
        return f"영상 {video_id}의 자막 내용 (추후 구현)"
    
    def crawl_target_channels(self, channel_names: List[str]) -> Dict[str, List[Dict]]:
        """타겟 채널들의 최신 영상 크롤링"""
        results = {}
        
        for channel_name in channel_names:
            print(f"크롤링 중: {channel_name}")
            
            # 채널 ID 검색
            channel_id = self.get_channel_id(channel_name)
            if not channel_id:
                print(f"채널을 찾을 수 없습니다: {channel_name}")
                continue
            
            # 최근 영상 가져오기
            videos = self.get_recent_videos(channel_id)
            results[channel_name] = videos
            
            print(f"완료: {channel_name} - {len(videos)}개 영상")
        
        return results
    
    def save_crawl_results(self, results: Dict, filename: str = None):
        """크롤링 결과를 JSON 파일로 저장"""
        if filename is None:
            filename = f"crawl_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(f"data/{filename}", 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"결과 저장 완료: {filename}")
            
        except Exception as e:
            print(f"파일 저장 오류: {e}")


# 테스트용 타겟 채널 목록 (5개)
TARGET_CHANNELS = [
    "나는솔로",
    "돌싱글즈", 
    "하트시그널",
    "SBS Entertainment",
    "MBC Entertainment"
]

def main():
    """테스트용 메인 함수"""
    # API 키는 환경변수에서 가져오기
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("YouTube API 키가 설정되지 않았습니다.")
        return
    
    crawler = YouTubeCrawler(api_key)
    results = crawler.crawl_target_channels(TARGET_CHANNELS)
    crawler.save_crawl_results(results)

if __name__ == "__main__":
    main()
