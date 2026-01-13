"""
Gemini AI 분석 모듈
유튜브 영상 내용을 분석하여 투표 미션을 생성합니다.
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
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_video_content(self, video_info: Dict) -> Optional[Dict]:
        """영상 내용 분석하여 미션 생성"""
        
        prompt = f"""
        다음 유튜브 영상 정보를 분석하여 리얼픽 앱에 적합한 투표 미션을 생성해주세요.

        영상 정보:
        - 제목: {video_info['title']}
        - 설명: {video_info['description'][:500]}...
        - 채널: {video_info['channel_title']}
        - 조회수: {video_info.get('view_count', 'N/A')}

        다음 조건을 만족하는 미션을 생성해주세요:
        1. 논쟁이 될 만한 흥미로운 주제
        2. 명확한 2-4개의 선택지
        3. 시청자들이 참여하고 싶어할 만한 내용
        4. 연애/방송 프로그램 관련 내용

        응답 형식 (JSON):
        {{
            "mission_title": "미션 제목",
            "mission_description": "미션 설명",
            "options": ["선택지1", "선택지2", "선택지3"],
            "controversy_level": "높음/중간/낮음",
            "expected_participation": "높음/중간/낮음",
            "reasoning": "이 미션을 제안하는 이유",
            "target_audience": "타겟 사용자층"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # JSON 추출
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result['source_video'] = video_info
                return result
            else:
                print("JSON 형식의 응답을 찾을 수 없습니다.")
                return None
                
        except Exception as e:
            print(f"Gemini 분석 오류: {e}")
            return None
    
    def analyze_controversy_potential(self, content: str) -> Dict:
        """콘텐츠의 논쟁 가능성 분석"""
        
        prompt = f"""
        다음 콘텐츠를 분석하여 논쟁 가능성을 평가해주세요:

        콘텐츠: {content[:1000]}

        다음 항목들을 분석해주세요:
        1. 논쟁 키워드 추출
        2. 감정적 반응 예상도
        3. 의견 분화 가능성
        4. 참여 유도 요소

        JSON 형식으로 응답해주세요:
        {{
            "controversy_keywords": ["키워드1", "키워드2"],
            "emotional_response": "높음/중간/낮음",
            "opinion_diversity": "높음/중간/낮음",
            "engagement_factors": ["요소1", "요소2"],
            "overall_score": 1-10
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
            
        except Exception as e:
            print(f"논쟁 분석 오류: {e}")
            return {}
    
    def generate_email_content(self, mission_info: Dict, channel_info: Dict) -> str:
        """파트너십 이메일 내용 생성"""
        
        prompt = f"""
        다음 정보를 바탕으로 유튜버에게 보낼 파트너십 제안 이메일을 작성해주세요:

        미션 정보:
        - 제목: {mission_info['mission_title']}
        - 설명: {mission_info['mission_description']}
        - 예상 참여도: {mission_info['expected_participation']}

        채널 정보:
        - 채널명: {channel_info['channel_title']}
        - 원본 영상: {channel_info['title']}

        이메일 조건:
        1. 정중하고 전문적인 톤
        2. 구체적인 수익 모델 제시
        3. 리얼픽의 가치 제안 명확히
        4. 행동 유도 (CTA) 포함

        제목과 본문을 모두 작성해주세요.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"이메일 생성 오류: {e}")
            return ""
    
    def generate_youtube_comment(self, video_info: Dict, mission_info: Dict) -> str:
        """유튜브 댓글용 홍보 텍스트 생성"""
        
        prompt = f"""
        다음 유튜브 영상에 달 홍보 댓글을 자연스럽게 작성해주세요:

        영상: {video_info['title']}
        관련 미션: {mission_info['mission_title']}

        조건:
        1. 자연스럽고 스팸 같지 않게
        2. 영상 내용과 연관성 있게
        3. 리얼픽 앱 언급을 은근히
        4. 호기심 유발
        5. 50자 이내

        예시: "이 부분 진짜 궁금했는데 리얼픽에서 투표 중이네요! 결과 완전 의외임 ㅋㅋ"
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"댓글 생성 오류: {e}")
            return ""
    
    def batch_analyze_videos(self, videos_data: Dict[str, List[Dict]]) -> Dict:
        """여러 채널의 영상들을 일괄 분석"""
        
        analysis_results = {}
        
        for channel_name, videos in videos_data.items():
            print(f"분석 중: {channel_name}")
            channel_results = []
            
            for video in videos:
                print(f"  - {video['title'][:50]}...")
                
                # 영상 분석
                mission = self.analyze_video_content(video)
                if mission:
                    # 논쟁 가능성 분석
                    controversy = self.analyze_controversy_potential(
                        video['title'] + " " + video['description']
                    )
                    mission['controversy_analysis'] = controversy
                    
                    # 이메일 내용 생성
                    email_content = self.generate_email_content(mission, video)
                    mission['email_content'] = email_content
                    
                    # 댓글 생성
                    comment = self.generate_youtube_comment(video, mission)
                    mission['youtube_comment'] = comment
                    
                    channel_results.append(mission)
            
            analysis_results[channel_name] = channel_results
            print(f"완료: {channel_name} - {len(channel_results)}개 미션 생성")
        
        return analysis_results
    
    def save_analysis_results(self, results: Dict, filename: str = None):
        """분석 결과를 JSON 파일로 저장"""
        if filename is None:
            filename = f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(f"data/{filename}", 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"분석 결과 저장 완료: {filename}")
            
        except Exception as e:
            print(f"파일 저장 오류: {e}")


def main():
    """테스트용 메인 함수"""
    # API 키는 환경변수에서 가져오기
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Gemini API 키가 설정되지 않았습니다.")
        return
    
    analyzer = GeminiAnalyzer(api_key)
    
    # 샘플 영상 정보로 테스트
    sample_video = {
        'title': '나는솔로 15기 3화 - 영수와 영희의 달달한 데이트',
        'description': '이번 화에서는 영수와 영희가 첫 데이트를 나가는 모습이 그려집니다...',
        'channel_title': '나는솔로 공식',
        'view_count': '1200000'
    }
    
    result = analyzer.analyze_video_content(sample_video)
    if result:
        print("분석 결과:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
