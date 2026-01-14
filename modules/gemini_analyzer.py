"""
Gemini AI 분석 모듈
유튜브 영상 내용(제목, 설명, 자막)을 분석하여 투표 미션을 생성합니다.
"""

import os
import google.generativeai as genai
from typing import Dict, List, Optional
import json
import re

class GeminiAnalyzer:
    """Gemini AI를 사용한 콘텐츠 분석 클래스"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash') # 성능과 속도를 위해 flash 모델 권장
    
    def analyze_with_transcript(self, video_info: Dict, transcript: str) -> Optional[Dict]:
        """영상 자막을 포함하여 정밀 분석 및 미션 생성"""
        
        prompt = f"""
        다음 유튜브 영상의 자막과 정보를 분석하여 '리얼픽' 앱(투표/미션 플랫폼)에 적합한 흥미로운 투표 미션을 3개 생성해주세요.

        영상 정보:
        - 제목: {video_info['title']}
        - 설명: {video_info.get('description', '')[:300]}
        
        영상 자막 내용 (일부):
        {transcript[:3000]} 

        미션 생성 가이드라인:
        1. 시청자들이 영상 내용 중 가장 논란이 되거나 의견이 갈릴만한 포인트를 짚어주세요.
        2. 리얼픽 앱의 주요 사용자(MZ세대, 방송 시청자)가 흥미를 느낄만한 주제여야 합니다.
        3. 각 미션은 제목, 상세 설명, 그리고 2~4개의 선택지로 구성해주세요.
        4. 영상의 핵심 갈등이나 이슈를 잘 반영해야 합니다.

        응답은 반드시 아래 JSON 형식으로만 해주세요:
        {{
            "missions": [
                {{
                    "title": "미션 제목",
                    "description": "미션 상세 설명 (왜 이 미션이 재미있는지)",
                    "options": ["선택지1", "선택지2"],
                    "category": "연애/이슈/정치/라이프 등"
                }},
                ...
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # JSON 추출
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None
        except Exception as e:
            print(f"Gemini 자막 분석 오류: {e}")
            return None

    def analyze_video_content(self, video_info: Dict) -> Optional[Dict]:
        """제목과 설명만으로 간단 분석 (자막 없을 때)"""
        prompt = f"""
        다음 유튜브 영상 정보를 분석하여 '리얼픽' 앱용 투표 미션을 1개 생성해주세요.

        영상 정보:
        - 제목: {video_info['title']}
        - 설명: {video_info.get('description', '')[:500]}

        응답 형식 (JSON):
        {{
            "title": "미션 제목",
            "description": "미션 설명",
            "options": ["선택지1", "선택지2"],
            "category": "분류"
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None
        except Exception as e:
            print(f"Gemini 콘텐츠 분석 오류: {e}")
            return None
