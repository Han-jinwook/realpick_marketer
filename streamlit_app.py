"""
리얼픽 마케팅 자동화 시스템
모듈 1: 유튜버 딜러 모집 및 관리 시스템
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import json
import glob
from dotenv import load_dotenv

# 로컬 환경이라면 .env 파일 로드
if os.path.exists(".env"):
    load_dotenv()

def get_api_key(key_name):
    if key_name in st.secrets:
        return st.secrets[key_name]
    return os.getenv(key_name)

# 페이지 설정
st.set_page_config(
    page_title="리얼픽 마케팅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS (연하고 심플한 대시보드 스타일)
st.markdown("""
    <style>
    .main { background-color: #f9fafb; font-family: 'Pretendard', sans-serif; }
    .metric-container { display: flex; gap: 20px; margin-bottom: 25px; }
    .metric-card {
        background: white; padding: 25px; border-radius: 12px; flex: 1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e5e7eb;
        text-align: center;
    }
    .metric-label { font-size: 0.85rem; color: #6b7280; margin-bottom: 8px; font-weight: 500; }
    .metric-value { font-size: 1.6rem; font-weight: 700; color: #374151; }
    .section-card {
        background: white; padding: 30px; border-radius: 12px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); margin-bottom: 30px;
        border: 1px solid #e5e7eb;
    }
    .keyword-badge {
        background-color: #f3f4f6; color: #4b5563; padding: 4px 10px;
        border-radius: 6px; font-size: 0.75rem; font-weight: 600;
        display: inline-block;
    }
    .custom-table {
        width: 100%; border-collapse: separate; border-spacing: 0;
        margin-top: 15px; border-radius: 8px; overflow: hidden;
    }
    .custom-table th {
        background-color: #f9fafb; color: #374151; padding: 14px 16px;
        text-align: left; font-weight: 600; font-size: 0.9rem;
        border-bottom: 2px solid #e5e7eb;
    }
    .custom-table td {
        padding: 14px 16px; border-bottom: 1px solid #f3f4f6;
        font-size: 0.85rem; color: #4b5563; background: white;
    }
    .custom-table tr:hover td { background-color: #f9fafb; }
    .video-link { color: #4f46e5; text-decoration: none; font-weight: 600; }
    .video-link:hover { text-decoration: underline; }
    .stButton>button {
        border-radius: 8px; font-weight: 600; padding: 0.5rem 1.2rem;
        background-color: #ffffff; color: #374151; border: 1px solid #d1d5db;
        transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #f3f4f6; border-color: #9ca3af; }
    .stButton>button[kind="primary"] {
        background-color: #374151; color: white; border: none;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #1f2937;
    }
    .status-badge {
        padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;
    }
    .status-available { background-color: #d1fae5; color: #065f46; }
    .status-unavailable { background-color: #fee2e2; color: #991b1b; }
    </style>
    """, unsafe_allow_html=True)

def get_latest_results():
    list_of_files = glob.glob('data/*.json')
    if not list_of_files: return None
    latest_file = max(list_of_files, key=os.path.getctime)
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception: return None

latest_results = get_latest_results()

st.title("리얼픽 마케팅 대시보드")
st.markdown("---")

st.sidebar.title("내비게이션")
module = st.sidebar.selectbox("모듈 선택", ["유튜버 모집", "가짜 유저 봇", "커뮤니티 바이럴"])

if "유튜버 모집" in module:
    tab1, tab2, tab3 = st.tabs(["크롤링 및 분석", "미션 승인", "이메일 관리"])
    
    with tab1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("수집 설정")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            today = datetime.now().date()
            date_range = st.date_input("날짜 범위", value=(today - timedelta(days=7), today), max_value=today)
            days_back = (today - date_range[0]).days if isinstance(date_range, tuple) and len(date_range) == 2 else 7
        with col_s2:
            max_vids = st.number_input("키워드당 수집 영상 수", min_value=1, max_value=50, value=5)

        raw_input = st.text_area("수집 키워드 (쉼표로 구분)", placeholder="예: 환승연애, 솔로지옥, 나는솔로")
        target_keywords = [x.strip() for x in raw_input.split(',')] if raw_input else []
        
        btn_c1, btn_c2 = st.columns([1, 4])
        with btn_c1:
            start_crawl = st.button("크롤링 시작", type="primary")
        with btn_c2:
            show_stats = st.button("상세 항목 보기")
        st.markdown('</div>', unsafe_allow_html=True)

        if start_crawl:
            if not target_keywords: st.warning("키워드를 입력해주세요.")
            else:
                api_key = get_api_key('YOUTUBE_API_KEY')
                with st.spinner("유튜브에서 데이터를 수집 중입니다..."):
                    try:
                        from test_crawler import SimpleYouTubeCrawler
                        crawler = SimpleYouTubeCrawler(api_key)
                        results = crawler.test_crawl(target_keywords, max_results=max_vids, days_back=days_back)
                        crawler.save_results(results)
                        st.success("데이터 수집이 완료되었습니다.")
                        st.rerun()
                    except Exception as e: st.error(f"오류: {str(e)}")

        if show_stats:
            if latest_results and 'channels' in latest_results:
                video_list = []
                channel_map = {}
                
                for kw, data in latest_results['channels'].items():
                    if data['status'] == 'success':
                        for v in data.get('videos', []):
                            v_count = int(v.get('view_count', 0))
                            s_count = int(v.get('subscriber_count', '0'))
                            
                            view_str = f"{v_count/10000:.1f}만" if v_count >= 10000 else (f"{v_count/1000:.1f}천" if v_count >= 1000 else str(v_count))
                            sub_str = f"{s_count/10000:.1f}만" if s_count >= 10000 else (f"{s_count/1000:.1f}천" if s_count >= 1000 else str(s_count))
                            
                            # 자막 상태 뱃지
                            subtitle_status = '<span class="status-badge status-available">있음</span>' if v.get('has_subtitle') else '<span class="status-badge status-unavailable">없음</span>'
                            
                            video_list.append({
                                "키워드": kw, "채널명": v['channel_title'], "제목": v['title'],
                                "조회수": view_str, "자막": subtitle_status, "날짜": v['published_at'][:10], 
                                "링크": v['video_url'], "video_id": v['video_id'], "has_subtitle": v.get('has_subtitle')
                            })
                            
                            if v['channel_title'] not in channel_map:
                                channel_map[v['channel_title']] = {
                                    "키워드": kw, "구독자수": sub_str, "이메일": v.get('email', 'N/A')
                                }

                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-card"><div class="metric-label">총 수집 영상</div><div class="metric-value">{len(video_list)}개</div></div>
                    <div class="metric-card"><div class="metric-label">활동 채널</div><div class="metric-value">{len(channel_map)}개</div></div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.subheader("수집 영상 목록")
                v_html = '<table class="custom-table"><thead><tr><th>키워드</th><th>채널명</th><th>영상 제목 (클릭 시 이동)</th><th>조회수</th><th>자막</th><th>날짜</th></tr></thead><tbody>'
                for v in video_list:
                    v_html += f'<tr><td><span class="keyword-badge">{v["키워드"]}</span></td><td>{v["채널명"]}</td>'
                    v_html += f'<td><a href="{v["링크"]}" target="_blank" class="video-link">{v["제목"]}</a></td>'
                    v_html += f'<td>{v["조회수"]}</td><td>{v["자막"]}</td><td>{v["날짜"]}</td></tr>'
                v_html += '</tbody></table></div>'
                st.markdown(v_html, unsafe_allow_html=True)

                # AI 미션 분석 섹션 추가
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.subheader("🤖 AI 미션 자동 생성")
                
                # 자막이 있는 영상만 필터링
                subtitled_videos = [v for v in video_list if v['has_subtitle']]
                
                if subtitled_videos:
                    selected_video_title = st.selectbox("미션을 생성할 영상을 선택하세요", [v['제목'] for v in subtitled_videos])
                    selected_v = next(v for v in subtitled_videos if v['제목'] == selected_video_title)
                    
                    if st.button("Gemini AI로 미션 생성하기", type="primary"):
                        gemini_api = get_api_key('GEMINI_API_KEY')
                        youtube_api = get_api_key('YOUTUBE_API_KEY')
                        
                        if not gemini_api:
                            st.error("Gemini API 키가 설정되지 않았습니다.")
                        else:
                            with st.spinner("영상 자막을 추출하고 AI가 미션을 생성 중입니다..."):
                                try:
                                    from test_crawler import SimpleYouTubeCrawler
                                    from modules.gemini_analyzer import GeminiAnalyzer
                                    
                                    crawler = SimpleYouTubeCrawler(youtube_api)
                                    analyzer = GeminiAnalyzer(gemini_api)
                                    
                                    # 1. 자막 추출
                                    transcript = crawler.get_transcript(selected_v['video_id'])
                                    
                                    if transcript:
                                        # 2. AI 분석
                                        analysis_result = analyzer.analyze_with_transcript(selected_v, transcript)
                                        
                                        if analysis_result and 'missions' in analysis_result:
                                            st.success(f"✅ '{selected_video_title}' 영상을 기반으로 3개의 미션이 생성되었습니다!")
                                            
                                            for idx, mission in enumerate(analysis_result['missions'], 1):
                                                with st.expander(f"미션 {idx}: {mission['title']}", expanded=True):
                                                    st.write(f"**설명:** {mission['description']}")
                                                    st.write(f"**선택지:** {', '.join(mission['options'])}")
                                                    st.caption(f"카테고리: {mission['category']}")
                                                    if st.button(f"미션 {idx} 승인 및 저장", key=f"approve_{idx}"):
                                                        st.info("미션이 저장되었습니다. (DB 연동 예정)")
                                        else:
                                            st.error("AI 분석 결과 형식이 올바르지 않습니다.")
                                    else:
                                        st.error("자막 내용을 가져오는데 실패했습니다.")
                                except Exception as e:
                                    st.error(f"AI 분석 중 오류 발생: {str(e)}")
                else:
                    st.info("자막이 수집된 영상이 없습니다. 다른 키워드로 다시 시도해 보세요.")
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.subheader("채널 연락처 및 분석")
                c_html = '<table class="custom-table"><thead><tr><th>키워드</th><th>채널명</th><th>구독자수</th><th>연락처 (이메일)</th></tr></thead><tbody>'
                for name, info in channel_map.items():
                    email_color = "#10b981" if info['이메일'] != "N/A" else "#6b7280"
                    c_html += f'<tr><td><span class="keyword-badge">{info["키워드"]}</span></td><td>{name}</td><td>{info["구독자수"]}</td>'
                    c_html += f'<td><span style="color: {email_color}; font-weight: 600;">{info["이메일"]}</span></td></tr>'
                c_html += '</tbody></table></div>'
                st.markdown(c_html, unsafe_allow_html=True)
            else:
                st.warning("수집된 데이터가 없습니다.")
        elif latest_results:
            st.info("상세 내용을 확인하려면 '상세 항목 보기' 버튼을 눌러주세요.")

st.sidebar.markdown("---")
if st.sidebar.button("시스템 가이드"):
    st.sidebar.info("1. 키워드와 날짜 범위를 입력하세요.\n2. 자막이 있는 영상을 선택해 AI 미션을 생성하세요.")
