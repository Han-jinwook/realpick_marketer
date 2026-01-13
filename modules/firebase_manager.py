"""
Firebase 관리 모듈
Firestore DB 연결 및 데이터 CRUD를 담당합니다.
"""

import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# .env 로드
load_dotenv()

class FirebaseManager:
    _instance = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
            cls._initialize_firebase()
        return cls._instance

    @classmethod
    def _initialize_firebase(cls):
        """Firebase SDK 초기화"""
        try:
            # 이미 초기화되어 있는지 확인
            if not firebase_admin._apps:
                cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
                
                if cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # 환경 변수에 경로가 없거나 파일이 없으면 기본 앱으로 초기화 시도 (GCP 환경 등)
                    firebase_admin.initialize_app()
                
            cls._db = firestore.client()
            print("✅ Firebase Firestore 연결 성공")
        except Exception as e:
            print(f"❌ Firebase 초기화 오류: {e}")
            cls._db = None

    def get_db(self):
        return self._db

    # --- Channels 관련 메서드 ---
    
    def save_channel(self, channel_id: str, channel_data: Dict[str, Any]):
        """채널 정보 저장"""
        if not self._db: return
        
        channel_data['updated_at'] = datetime.now()
        self._db.collection('channels').document(channel_id).set(channel_data, merge=True)
        print(f"💾 채널 저장 완료: {channel_id}")

    def get_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """채널 정보 조회"""
        if not self._db: return None
        
        doc = self._db.collection('channels').document(channel_id).get()
        return doc.to_dict() if doc.exists else None

    # --- Videos 관련 메서드 ---

    def save_video(self, video_id: str, video_data: Dict[str, Any]):
        """영상 정보 저장"""
        if not self._db: return
        
        video_data['updated_at'] = datetime.now()
        self._db.collection('videos').document(video_id).set(video_data, merge=True)
        print(f"💾 영상 저장 완료: {video_id}")

    def get_recent_videos(self, limit: int = 20) -> List[Dict[str, Any]]:
        """최근 수집된 영상 목록 조회"""
        if not self._db: return []
        
        docs = self._db.collection('videos').order_by(
            'published_at', direction=firestore.Query.DESCENDING
        ).limit(limit).stream()
        
        return [doc.to_dict() for doc in docs]

    # --- Missions 관련 메서드 ---

    def save_mission(self, mission_id: str, mission_data: Dict[str, Any]):
        """미션 정보 저장"""
        if not self._db: return
        
        mission_data['created_at'] = datetime.now()
        self._db.collection('missions').document(mission_id).set(mission_data, merge=True)
        print(f"💾 미션 저장 완료: {mission_id}")

# 싱글톤 인스턴스 생성
firebase_db = FirebaseManager()

