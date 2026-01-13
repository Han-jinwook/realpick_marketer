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

# 로컬 환경이라면 .env 파일 로드 (Streamlit Cloud에서는 st.secrets 사용)
if os.path.exists(".env"):
    load_dotenv()

# API 키 가져오는 함수 (로컬/서버 공통)
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

# 커스텀 CSS
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
                # API 키 가져오기 (st.secrets 우선)
                api_key = get_api_key('YOUTUBE_API_KEY')
                if not api_key:
                    st.error("YouTube API 키가 설정되지 않았습니다. Streamlit Secrets 또는 .env를 확인해주세요.")
                else:
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
                            
                            video_list.append({
                                "키워드": kw, "채널명": v['channel_title'], "제목": v['title'],
                                "조회수": view_str, "날짜": v['published_at'][:10], "링크": v['video_url']
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
                v_html = '<table class="custom-table"><thead><tr><th>키워드</th><th>채널명</th><th>영상 제목 (클릭 시 이동)</th><th>조회수</th><th>날짜</th></tr></thead><tbody>'
                for v in video_list:
                    v_html += f'<tr><td><span class="keyword-badge">{v["키워드"]}</span></td><td>{v["채널명"]}</td>'
                    v_html += f'<td><a href="{v["링크"]}" target="_blank" class="video-link">{v["제목"]}</a></td>'
                    v_html += f'<td>{v["조회수"]}</td><td>{v["날짜"]}</td></tr>'
                v_html += '</tbody></table></div>'
                st.markdown(v_html, unsafe_allow_html=True)

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
                st.warning("수집된 데이터가 없습니다. 먼저 크롤링을 실행해주세요.")
        elif latest_results:
            st.info("상세 내용을 확인하려면 '상세 항목 보기' 버튼을 눌러주세요.")

st.sidebar.markdown("---")
if st.sidebar.button("시스템 가이드"):
    st.sidebar.info("1. 키워드와 날짜 범위를 입력하세요.\n2. 결과를 확인하고 유튜버에게 연락하세요.")
