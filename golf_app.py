import streamlit as st
import pandas as pd
import numpy as np
import random
import json
import os
import base64
from datetime import datetime

st.set_page_config(
    page_title="Segok Golf Club", 
    page_icon="⛳", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_FILE = "club_data.json"
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

ADMIN_MEMBERS = ["이승환", "김성모", "김경수", "김지윤"]

DEFAULT_MEMBERS = [
    "김성모", "김선욱", "김경수", "김지윤", "Kim Shawn", "고종만", "김동숙", "김동현", 
    "김미화", "김영준", "김주연", "김춘환", "김치훈", "김태성", "김현태", "나승환", 
    "박재영", "변성규", "서영완", "안종원", "이민숙", "이승준", "이승환", "이윤진", 
    "이재익", "이주원", "이진아", "이태성", "이형준", "이희완", "임혜영", "정기영", 
    "진지영", "최성준", "최승락"
]

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "member_db" in data:
                    for m in DEFAULT_MEMBERS:
                        if m in data["member_db"]:
                            data["member_db"][m]["status"] = "approved"
                            data["member_db"][m]["is_admin"] = True if m in ADMIN_MEMBERS else False
                            if "last_notice_seen" not in data["member_db"][m]:
                                data["member_db"][m]["last_notice_seen"] = ""
                            if "last_lounge_seen" not in data["member_db"][m]:
                                data["member_db"][m]["last_lounge_seen"] = ""
                    if "notices" not in data:
                        data["notices"] = []
                    for post in data.get("feed_posts", []):
                        if "liked_users" not in post:
                            post["liked_users"] = []
                        if "poll" not in post:
                            post["poll"] = None
                        if "file_path" not in post:
                            post["file_path"] = None
                            post["file_name"] = None
                    return data
        except Exception:
            pass
    
    member_db = {}
    for name in DEFAULT_MEMBERS:
        member_db[name] = {
            "password": "1234",
            "nickname": name,
            "profile_img": None,
            "handicap": 0,
            "attendance": 0,
            "rounds_played": 0,
            "score_history": [],
            "status": "approved",
            "is_admin": True if name in ADMIN_MEMBERS else False,
            "last_notice_seen": "",
            "last_lounge_seen": ""
        }
    pair_history = {m1: {m2: 0 for m2 in DEFAULT_MEMBERS} for m1 in DEFAULT_MEMBERS}
    feed_posts = [] 
    rounds_data = [] 
    match_logs = []
    notices = []
    
    return {
        "total_events": 0,
        "member_db": member_db,
        "pair_history": pair_history,
        "feed_posts": feed_posts,
        "rounds_data": rounds_data,
        "match_logs": match_logs,
        "notices": notices
    }

def save_data(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def recalculate_all_stats(db_obj):
    r_list = [r for r in db_obj.get("rounds_data", []) if "필드" in r.get("type", "")]
    m_db = db_obj.get("member_db", {})
    
    completed_rounds = [r for r in r_list if r.get("completed", False)]
    total_r_count = len(completed_rounds)
    db_obj["total_events"] = total_r_count

    for name, m_info in m_db.items():
        m_info["score_history"] = []
        m_info["rounds_played"] = 0
        m_info["handicap"] = 0
        m_info["attendance"] = 0

    if total_r_count == 0:
        return

    for r in reversed(completed_rounds):
        scores_dict = r.get("scores", {})
        for name, p_info in scores_dict.items():
            if name in m_db:
                sc = p_info.get("score", 85)
                m_db[name]["score_history"].append(sc)
                m_db[name]["rounds_played"] += 1

    for name, m_info in m_db.items():
        hist = m_info.get("score_history", [])
        if hist:
            recent_5 = hist[-5:]
            avg_score = sum(recent_5) / len(recent_5)
            m_info["handicap"] = round(avg_score - 72)
        else:
            m_info["handicap"] = 0
            
        m_info["attendance"] = round((m_info["rounds_played"] / total_r_count) * 100)

st.session_state.db_data = load_data()

db = st.session_state.db_data
member_db = db.get("member_db", {})
pair_history = db.get("pair_history", {})
feed_posts = db.setdefault("feed_posts", [])
rounds_data = db.setdefault("rounds_data", [])
match_logs = db.setdefault("match_logs", [])
notices = db.setdefault("notices", [])

query_user = None
query_menu = None
try:
    query_user = st.query_params.get("u", None)
    query_menu = st.query_params.get("m", "HOME")
except Exception:
    pass

if 'logged_in_user' not in st.session_state or st.session_state.logged_in_user is None:
    if query_user and query_user in member_db and member_db[query_user].get("status", "approved") == "approved":
        st.session_state.logged_in_user = query_user

if 'current_menu' not in st.session_state:
    st.session_state.current_menu = query_menu if query_menu else "HOME"

def set_menu(menu_name):
    st.session_state.current_menu = menu_name
    try:
        st.query_params["m"] = menu_name
        if st.session_state.get('logged_in_user'):
            st.query_params["u"] = st.session_state.logged_in_user
    except Exception:
        pass

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,600&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    .stApp { background-color: #FAFAFA !important; font-family: 'Noto Sans KR', sans-serif; color: #262626; font-size: 0.9rem; }
    
    .compact-header { background-color: #FFFFFF; padding: 10px 20px; border-bottom: 1px solid #DBDBDB; display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
    
    .logo-hero { text-align: center; padding: 30px 15px 20px 15px; background: linear-gradient(135deg, #1B3B2B 0%, #2C523D 100%); border-radius: 14px; color: #FFFFFF; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(27,59,43,0.12); }
    .logo-hero h1 { font-family: 'Playfair Display', serif; font-size: 2rem; margin: 6px 0 2px 0; color: #F8F5F0; }
    .logo-hero p { color: #D4B475; font-size: 0.7rem; letter-spacing: 3px; text-transform: uppercase; font-weight: 600; margin: 0; }
    
    .menu-card { background-color: #FFFFFF; border-radius: 10px; border: 1px solid #DBDBDB; padding: 16px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.02); transition: all 0.2s ease; margin-bottom: 12px; position: relative; }
    .menu-card h3 { font-size: 1rem; margin-bottom: 4px; color: #1B3B2B; }
    .menu-card p { color: #666; font-size: 0.78rem; margin-bottom: 10px; line-height: 1.3; }
    
    .band-card { background-color: #FFFFFF; border-radius: 10px; border: 1px solid #E0E0E0; max-width: 100%; margin: 0 auto 16px auto; box-shadow: 0 1px 4px rgba(0,0,0,0.02); overflow: hidden; }
    .band-header { display: flex; align-items: center; padding: 12px 14px; border-bottom: 1px solid #F0F0F0; background-color: #FAFAFA; }
    .band-body { padding: 14px; font-size: 0.88rem; color: #262626; line-height: 1.5; word-break: break-all; user-select: text; }
    
    .team-box { background-color: #1B3B2B; color: #FFFFFF; padding: 14px; border-radius: 10px; margin-bottom: 12px; border: 1px solid #C5A059; font-size: 0.85rem; }
    .team-box h3 { color: #E5C585 !important; font-family: 'Playfair Display', serif; font-size: 1rem; margin-bottom: 6px; border-bottom: 1px solid #325843; padding-bottom: 4px; }
    
    .badge-admin { background-color: #1B3B2B; color: #FFFFFF; padding: 2px 6px; border-radius: 8px; font-size: 0.65rem; font-weight: 600; border: 1px solid #C5A059; }
    .badge-user { background-color: #EFEFEF; color: #262626; padding: 2px 6px; border-radius: 8px; font-size: 0.65rem; font-weight: 600; }
    .badge-hc { background-color: #FDF8F0; color: #B38F4E; padding: 2px 6px; border-radius: 8px; font-size: 0.65rem; font-weight: 700; border: 1px solid #E5DEC3; }
    .profile-avatar { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; border: 1.5px solid #C5A059; margin-right: 10px; }
    
    .new-badge { background-color: #2E7D32; color: #FFFFFF; padding: 2px 5px; border-radius: 8px; font-size: 0.6rem; font-weight: 700; vertical-align: middle; margin-left: 4px; }
    
    .stButton>button { background-color: #1B3B2B !important; color: #FFFFFF !important; border-radius: 6px !important; border: none !important; font-weight: 600 !important; width: 100% !important; padding: 6px 10px !important; font-size: 0.85rem !important; }
    .stButton>button:hover { background-color: #27523C !important; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN & SIGNUP ---
if not st.session_state.get('logged_in_user'):
    st.markdown("""
    <div style="text-align: center; padding: 35px 15px 20px 15px;">
        <div style="font-size: 2.5rem;">⛳</div>
        <h1 style="font-family: 'Playfair Display', serif; color: #1B3B2B; margin: 8px 0 0 0; font-size: 2rem;">Segok Golf Club</h1>
        <p style="color: #8E8E8E; font-size: 0.75rem; letter-spacing: 3px; text-transform: uppercase;">PREMIUM GOLF SOCIETY</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_login, _ = st.columns([1, 0.01])
    with col_login:
        tab1, tab2 = st.tabs(["🔑 클럽 회원 로그인", "✨ 신입 회원 가입 신청"])
        
        with tab1:
            st.caption("초기 비밀번호는 '1234' 입니다.")
            approved_members = [k for k, v in member_db.items() if v.get("status", "approved") == "approved"]
            login_name = st.selectbox("회원 성함 선택", ["선택하세요"] + approved_members)
            login_pw = st.text_input("비밀번호 입력", type="password")
            
            if st.button("로그인", type="primary", use_container_width=True):
                if login_name in member_db:
                    user = member_db[login_name]
                    if user.get("status", "approved") != "approved":
                        st.error("⌛ 운영진 승인 대기 중입니다.")
                    elif login_pw == user.get("password", "1234"):
                        st.session_state.logged_in_user = login_name
                        set_menu("HOME")
                        try:
                            st.query_params["u"] = login_name
                        except Exception:
                            pass
                        st.success(f"{login_name}님 환영합니다!")
                        st.rerun()
                    else:
                        st.error("비밀번호가 올바르지 않습니다.")
                else:
                    st.warning("회원 성함을 선택해 주세요.")
                    
        with tab2:
            st.caption("가입 신청 후 운영진 승인을 거쳐 클럽 활동에 참여하실 수 있습니다.")
            new_name = st.text_input("회원 성함")
            new_nick = st.text_input("클럽 닉네임 (선택)")
            new_pw = st.text_input("비밀번호 설정", type="password")
            
            if st.button("가입 신청서 제출", use_container_width=True):
                if new_name and new_pw:
                    if new_name in member_db:
                        st.error("이미 등록된 회원 성함입니다.")
                    else:
                        member_db[new_name] = {
                            "password": new_pw,
                            "nickname": new_nick if new_nick else new_name,
                            "profile_img": None,
                            "handicap": 0,
                            "attendance": 0,
                            "rounds_played": 0,
                            "score_history": [],
                            "status": "pending",
                            "is_admin": True if new_name in ADMIN_MEMBERS else False,
                            "last_notice_seen": "",
                            "last_lounge_seen": ""
                        }
                        pair_history[new_name] = {m: 0 for m in member_db.keys()}
                        for m in member_db.keys():
                            pair_history[m][new_name] = 0
                            
                        save_data(db)
                        st.success(f"🎉 {new_name}님 가입 신청이 완료되었습니다! 운영진 승인 후 이용 가능합니다.")
                else:
                    st.warning("성함과 비밀번호를 모두 입력해 주세요.")
    st.stop()

current_user = st.session_state.logged_in_user
if current_user not in member_db:
    st.session_state.logged_in_user = None
    set_menu("HOME")
    st.rerun()

user_info = member_db.get(current_user, {
    "nickname": current_user, "handicap": 0, "attendance": 0, "is_admin": False
})

is_admin = user_info.get('is_admin', False)
display_nickname = user_info.get('nickname', current_user)
admin_badge = '<span class="badge-admin">👑 운영진</span>' if is_admin else '<span class="badge-user">👤 정회원</span>'

last_n = user_info.get("last_notice_seen", "")
latest_notice_date = notices[0]["date"] if notices else ""
has_new_notice = latest_notice_date > last_n if latest_notice_date else False

last_l = user_info.get("last_lounge_seen", "")
latest_lounge_date = feed_posts[0]["date"] if feed_posts else ""
has_new_lounge = latest_lounge_date > last_l if latest_lounge_date else False

# --- 상단 고정 헤더 ---
col_h1, col_h2 = st.columns([2, 3])
with col_h1:
    if st.button("⛳ Segok Golf Club", key="logo_home_btn"):
        set_menu("HOME")
        st.rerun()
with col_h2:
    hc_val = user_info.get('handicap', 0)
    att_val = user_info.get('attendance', 0)
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; align-items: center; gap: 8px; padding-top: 6px; font-size: 0.82rem;">
        <span><b>{display_nickname}</b>님 {admin_badge}</span>
        <span class="badge-hc">HC {hc_val}</span>
        <span class="badge-user">참석 {att_val}%</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 8px 0 15px 0; border-top: 1px solid #DBDBDB;'>", unsafe_allow_html=True)

if st.session_state.current_menu == "HOME":
    st.markdown("""
    <div class="logo-hero">
        <div style="font-size: 2.5rem; margin-bottom: 4px;">🏆</div>
        <h1>Segok Golf Club</h1>
        <p>PREMIUM GOLF SOCIETY & COMMUNITY</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    
    with c1:
        notice_badge = '<span class="new-badge">NEW</span>' if has_new_notice else ''
        st.markdown(f"""
        <div class="menu-card">
            <h3>📢 공지사항{notice_badge}</h3>
            <p>클럽 소식 및 조편성 안내</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("공지사항 입장", use_container_width=True, key="go_notice"):
            set_menu("클럽 공지사항")
            st.rerun()
            
        lounge_badge = '<span class="new-badge">NEW</span>' if has_new_lounge else ''
        st.markdown(f"""
        <div class="menu-card" style="margin-top: 15px;">
            <h3>💬 클럽 라운지{lounge_badge}</h3>
            <p>자유 소통, 투표 및 파일 공유</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("클럽 라운지 입장", use_container_width=True, key="go_lounge"):
            set_menu("클럽 라운지")
            st.rerun()

        st.markdown(f"""
        <div class="menu-card" style="margin-top: 15px;">
            <h3>📁 조편성 아카이브</h3>
            <p>지난 날짜별 조편성 기록 확인</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("아카이브 입장", use_container_width=True, key="go_archive"):
            set_menu("역대 조편성 아카이브")
            st.rerun()

    with c2:
        st.markdown("""
        <div class="menu-card">
            <h3>🏆 경기 결과 & 랭킹</h3>
            <p>역대 스코어 및 공식 시상</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("경기 결과 입장", use_container_width=True, key="go_result"):
            set_menu("경기 결과 및 랭킹")
            st.rerun()
            
        st.markdown("""
        <div class="menu-card" style="margin-top: 15px;">
            <h3>👑 명예의 전당</h3>
            <p>회원별 평균타수 및 출석 현황</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("명예의 전당 입장", use_container_width=True, key="go_records"):
            set_menu("명예의 전당")
            st.rerun()

        st.markdown("""
        <div class="menu-card" style="margin-top: 15px;">
            <h3>👤 마이페이지</h3>
            <p>프로필, 로그아웃 및 클럽 탈퇴</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("마이페이지 입장", use_container_width=True, key="go_mypage"):
            set_menu("마이페이지")
            st.rerun()

    if is_admin:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        ac1, ac2 = st.columns(2)
        with ac1:
            st.markdown("""
            <div class="menu-card">
                <h3>⛳ 티타임 조편성</h3>
                <p>맞춤형 조편성 및 수동 복사 지원</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("조편성 실행", use_container_width=True, key="go_match"):
                set_menu("티타임 조편성")
                st.rerun()
        with ac2:
            pending_cnt = len([k for k, v in member_db.items() if v.get("status") == "pending"])
            badge_txt = f" (대기 {pending_cnt})" if pending_cnt > 0 else ""
            st.markdown(f"""
            <div class="menu-card">
                <h3>👥 회원 리스트{badge_txt}</h3>
                <p>정회원 관리 및 가입 승인</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("회원 리스트 관리", use_container_width=True, key="go_members"):
                set_menu("회원 리스트")
                st.rerun()

else:
    notice_label = f"📢 클럽 공지사항 {'🟢' if has_new_notice else ''}"
    lounge_label = f"💬 클럽 라운지 {'🟢' if has_new_lounge else ''}"
    
    menu_list = ["메인 홈", notice_label, lounge_label, "🏆 경기 결과 및 랭킹", "👑 명예의 전당", "📁 역대 조편성 아카이브", "👤 마이페이지"]
    if is_admin:
        menu_list.insert(3, "⛳ 티타임 조편성")
        menu_list.append("👥 회원 리스트")
        
    current_label_map = {
        "HOME": "메인 홈",
        "클럽 공지사항": notice_label,
        "클럽 라운지": lounge_label,
        "티타임 조편성": "⛳ 티타임 조편성",
        "경기 결과 및 랭킹": "🏆 경기 결과 및 랭킹",
        "명예의 전당": "👑 명예의 전당",
        "역대 조편성 아카이브": "📁 역대 조편성 아카이브",
        "회원 리스트": "👥 회원 리스트",
        "마이페이지": "👤 마이페이지"
    }
    reverse_map = {v: k for k, v in current_label_map.items()}
    curr_label = current_label_map.get(st.session_state.current_menu, notice_label)

    nav_c1, _ = st.columns([1, 0.01])
    with nav_c1:
        selected_nav = st.selectbox("📌 빠른 메뉴 이동", menu_list, index=menu_list.index(curr_label) if curr_label in menu_list else 0)
        target_menu = reverse_map.get(selected_nav, "HOME")
        if "공지사항" in selected_nav: target_menu = "클럽 공지사항"
        elif "라운지" in selected_nav: target_menu = "클럽 라운지"
        
        if target_menu != st.session_state.current_menu:
            set_menu(target_menu)
            st.rerun()

    st.markdown("<hr style='margin: 12px 0 15px 0; border-top: 1px solid #DBDBDB;'>", unsafe_allow_html=True)
    
    menu = st.session_state.current_menu

    # 1. 📢 클럽 공지사항 (복사하기 쉽도록 standard text/code block 사용)
    if menu == "클럽 공지사항":
        if notices:
            user_info["last_notice_seen"] = notices[0]["date"]
            save_data(db)
            
        st.subheader("📢 클럽 공지사항")
        st.caption("세곡 골프클럽의 주요 소식과 안내 사항을 확인하세요.")
        
        if is_admin:
            with st.expander("✍️ [운영진] 새 공지사항 등록하기"):
                n_title = st.text_input("공지 제목")
                n_content = st.text_area("공지 내용 (카톡 복사본 붙여넣기 적합)")
                if st.button("공지 발행", type="primary", use_container_width=True):
                    if n_title and n_content:
                        notices.insert(0, {
                            "id": int(datetime.now().timestamp()),
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "title": n_title,
                            "content": n_content
                        })
                        save_data(db)
                        st.success("공지가 성공적으로 발행되었습니다.")
                        st.rerun()
                    else:
                        st.warning("제목과 내용을 모두 입력해 주세요.")
                        
        if not notices:
            st.info("등록된 공지사항이 없습니다.")
        else:
            for n_idx, notice in enumerate(notices):
                st.markdown(f"""
                <div class="band-card">
                    <div class="band-header">
                        <div>
                            <strong style="color:#1B3B2B; font-size:0.9rem;">📌 {notice['title']}</strong><br>
                            <span style="color:#8E8E8E; font-size:0.7rem;">{notice['date']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 쉽게 복사할 수 있도록 st.code 사용 (우측 상단에 복사 버튼 제공됨)
                st.code(notice['content'], language="text")
                
                if is_admin:
                    del_key = f"del_notice_{notice['id']}"
                    confirm_key = f"conf_notice_{notice['id']}"
                    
                    with st.expander("🗑️ 공지 삭제 관리"):
                        confirm_del = st.checkbox("정말로 이 공지사항을 삭제하시겠습니까?", key=confirm_key)
                        if confirm_del:
                            if st.button("⚠️ 최종 삭제 실행", key=del_key, type="primary", use_container_width=True):
                                notices.pop(n_idx)
                                save_data(db)
                                st.success("공지사항이 삭제되었습니다.")
                                st.rerun()

    # 2. 💬 클럽 라운지 (동적 항목 추가 버튼식 투표 시스템 도입)
    elif menu == "클럽 라운지":
        if feed_posts:
            user_info["last_lounge_seen"] = feed_posts[0]["date"]
            save_data(db)
            
        st.subheader("💬 클럽 라운지")
        with st.expander("✍️ 새 글 작성하기 (사진/파일/투표 첨부)", expanded=True):
            post_text = st.text_area("내용 입력", placeholder="라운딩 후기, 모임 소식 등을 자유롭게 남겨보세요...")
            
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                uploaded_file = st.file_uploader("이미지 첨부 (선택)", type=["jpg", "png", "jpeg"])
            with col_u2:
                doc_file = st.file_uploader("문서/엑셀 파일 첨부 (선택)", type=["xlsx", "xls", "pdf", "txt", "csv"])
            
            use_poll = st.checkbox("📊 투표 생성하기")
            poll_question = ""
            poll_options = []
            
            if use_poll:
                poll_question = st.text_input("투표 주제", placeholder="예: 다음 모임 장소 추천")
                
                if 'poll_option_count' not in st.session_state:
                    st.session_state.poll_option_count = 2
                
                col_cnt1, col_cnt2 = st.columns([3, 1])
                with col_cnt2:
                    if st.button("➕ 항목 추가"):
                        st.session_state.poll_option_count += 1
                        st.rerun()
                
                for i in range(st.session_state.poll_option_count):
                    opt_val = st.text_input(f"투표 항목 {i+1}", key=f"poll_opt_input_{i}", placeholder=f"항목 {i+1} 입력")
                    if opt_val:
                        poll_options.append(opt_val.strip())

            if st.button("게시물 등록하기", type="primary", use_container_width=True):
                if post_text or uploaded_file or doc_file or use_poll:
                    media_path = None
                    media_type = None
                    if uploaded_file is not None:
                        file_name = f"{int(datetime.now().timestamp())}_{uploaded_file.name}"
                        media_path = os.path.join(UPLOAD_DIR, file_name)
                        with open(media_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        media_type = "image"
                    
                    file_path = None
                    file_name = None
                    if doc_file is not None:
                        file_name = doc_file.name
                        file_path = os.path.join(UPLOAD_DIR, f"doc_{int(datetime.now().timestamp())}_{file_name}")
                        with open(file_path, "wb") as f:
                            f.write(doc_file.getbuffer())

                    poll_data = None
                    if use_poll and poll_question and len(poll_options) >= 2:
                        poll_data = {
                            "question": poll_question,
                            "options": {opt: [] for opt in poll_options}
                        }
                    
                    feed_posts.insert(0, {
                        "id": int(datetime.now().timestamp()),
                        "author": current_user,
                        "nickname": user_info.get("nickname", current_user),
                        "profile_img": user_info.get("profile_img", None),
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "content": post_text,
                        "media_path": media_path,
                        "media_type": media_type,
                        "file_path": file_path,
                        "file_name": file_name,
                        "poll": poll_data,
                        "likes": 0,
                        "liked_users": [],
                        "comments": []
                    })
                    st.session_state.poll_option_count = 2
                    save_data(db)
                    st.success("게시물이 등록되었습니다!")
                    st.rerun()

        if not feed_posts:
            st.info("아직 등록된 게시물이 없습니다. 첫 소식을 공유해 보세요!")
        else:
            for idx, post in enumerate(feed_posts):
                p_author = post.get("author", "알수없음")
                author_info = member_db.get(p_author, {})
                p_nickname = author_info.get("nickname", post.get("nickname", p_author))
                p_img = author_info.get("profile_img", post.get("profile_img"))
                
                if p_img:
                    avatar_html = f'<img src="data:image/png;base64,{p_img}" class="profile-avatar">'
                else:
                    avatar_html = '<span style="font-size:1.3rem; margin-right:8px;">👤</span>'
                    
                st.markdown(f"""
                <div class="band-card">
                    <div class="band-header">
                        {avatar_html}
                        <div>
                            <strong style="color:#262626; font-size:0.9rem;">{p_nickname}</strong><br>
                            <span style="color:#8E8E8E; font-size:0.7rem;">{post['date']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                m_path = post.get("media_path")
                if m_path and os.path.exists(m_path):
                    st.image(m_path, use_column_width=True)

                f_path = post.get("file_path")
                f_name = post.get("file_name")
                if f_path and f_name and os.path.exists(f_path):
                    with open(f_path, "rb") as fp:
                        st.download_button(label=f"📎 첨부파일 다운로드: {f_name}", data=fp, file_name=f_name, key=f"dl_{post['id']}")

                if post.get('content'):
                    st.markdown(f"""
                    <div class="band-body">
                        <p style="margin:0; color:#262626; word-break:break-all; white-space: pre-wrap; user-select: text;">{post['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                poll = post.get("poll")
                if poll:
                    st.markdown(f"**📊 [투표] {poll['question']}**")
                    total_votes = sum(len(v) for v in poll["options"].values())
                    for opt, voters in poll["options"].items():
                        voted_here = current_user in voters
                        btn_label = f"✓ {opt} ({len(voters)}표)" if voted_here else f"{opt} ({len(voters)}표)"
                        if st.button(btn_label, key=f"poll_{post['id']}_{opt}", use_container_width=True):
                            for o_key, o_list in poll["options"].items():
                                if current_user in o_list:
                                    o_list.remove(current_user)
                            if not voted_here:
                                voters.append(current_user)
                            save_data(db)
                            st.rerun()
                    st.caption(f"총 투표 참여 인원: {total_votes}명")

                st.markdown("</div>", unsafe_allow_html=True)
                    
                c_lk, c_del = st.columns([1, 1])
                with c_lk:
                    liked_list = post.setdefault("liked_users", [])
                    has_liked = current_user in liked_list
                    heart_label = f"❤️ ({post['likes']})" if has_liked else f"🤍 ({post['likes']})"
                    
                    if st.button(heart_label, key=f"lk_{post['id']}"):
                        if has_liked:
                            liked_list.remove(current_user)
                            post['likes'] = max(0, post['likes'] - 1)
                        else:
                            liked_list.append(current_user)
                            post['likes'] += 1
                        save_data(db)
                        st.rerun()
                        
                if post['author'] == current_user or is_admin:
                    with c_del:
                        with st.expander("🗑️ 삭제"):
                            conf_post = st.checkbox("정말로 삭제하시겠습니까?", key=f"conf_post_{post['id']}")
                            if conf_post:
                                if st.button("⚠️ 삭제 실행", key=f"btn_del_post_{post['id']}", type="primary", use_container_width=True):
                                    feed_posts.pop(idx)
                                    save_data(db)
                                    st.success("삭제되었습니다.")
                                    st.rerun()

                with st.expander(f"💬 댓글 ({len(post.get('comments', []))})"):
                    for c in post.get('comments', []):
                        c_author = c.get('author', '')
                        c_nick = member_db.get(c_author, {}).get("nickname", c_author)
                        st.write(f"**{c_nick}**: {c['text']}")
                    new_c = st.text_input("댓글 작성", key=f"nc_{post['id']}")
                    if st.button("등록", key=f"btn_c_{post['id']}", use_container_width=True) and new_c:
                        post.setdefault('comments', []).append({"author": current_user, "text": new_c})
                        save_data(db)
                        st.rerun()

    # 3. ⛳ 티타임 조편성 (수동 복사 지원 - 자동 공지 등록 취소)
    elif menu == "티타임 조편성":
        st.subheader("⛳ 필드 월례회 티타임 조편성")
        if not is_admin:
            st.error("⛔ 조편성 기능은 운영진 전용 메뉴입니다.")
        else:
            st.success("👑 **운영자 권한 완료** | 모임 일정, 장소 및 각 조별 티오프 시간과 코스 정보를 개별 설정합니다.")
            
            st.markdown("##### 📌 기본 라운드 정보 입력")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                r_date_input = st.date_input("라운드 일정 (날짜)")
            with col_t2:
                golf_location = st.text_input("골프장 장소", placeholder="예: 남서울CC")

            balance_rule = st.radio("조편성 방식", ["과거 동반 중복 방지 (기본)", "핸디캡 균등 배정 (고수+초보 믹스)"])
            
            approved_names = [k for k, v in member_db.items() if v.get("status", "approved") == "approved"]
            default_selected = approved_names[:16] if len(approved_names) >= 16 else approved_names
            selected_attendees = st.multiselect("오늘 참석자 선택", approved_names, default=default_selected)
            
            def generate_teams_smart(attendees, pair_hist, mem_db, rule="중복방지", team_sz=4, iterations=300):
                if not attendees:
                    return []
                best_teams = []
                min_score = float('inf')
                for _ in range(iterations):
                    shuffled = attendees.copy()
                    random.shuffle(shuffled)
                    teams = [shuffled[i:i + team_sz] for i in range(0, len(shuffled), team_sz)]
                    score = 0
                    if "중복방지" in rule:
                        for t in teams:
                            for i in range(len(t)):
                                for j in range(i+1, len(t)):
                                    score += (pair_hist.get(t[i], {}).get(t[j], 0) ** 2) * 10
                    else:
                        team_hcs = [sum(mem_db[m]['handicap'] for m in t)/len(t) for t in teams]
                        score = np.std(team_hcs) * 100
                    if score < min_score:
                        min_score = score
                        best_teams = teams
                return best_teams

            if st.button("🎲 자동 조편성 실행하기", type="primary", use_container_width=True):
                teams = generate_teams_smart(selected_attendees, pair_history, member_db, balance_rule)
                st.session_state.generated_teams = teams
                st.success("🎉 자동 조편성이 완료되었습니다!")

            if 'generated_teams' in st.session_state and st.session_state.generated_teams:
                teams = st.session_state.generated_teams
                
                with st.expander("✏️ 조 구성원 수동 변경"):
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        move_mem = st.selectbox("이동시킬 회원", selected_attendees)
                    with col_m2:
                        target_team_num = st.selectbox("이동할 조", [f"{i+1}조" for i in range(len(teams))])
                        
                    if st.button("🔄 조 이동 실행", use_container_width=True):
                        for t in teams:
                            if move_mem in t:
                                t.remove(move_mem)
                        target_idx = int(target_team_num.replace("조", "")) - 1
                        teams[target_idx].append(move_mem)
                        st.session_state.generated_teams = teams
                        st.success(f"{move_mem} 회원이 {target_team_num}로 이동되었습니다.")
                        st.rerun()

                st.markdown("---")
                st.markdown("##### ⏰ 각 조별 티오프 시간 및 코스 정보")
                
                group_tee_times = []
                group_courses = []
                
                for idx in range(len(teams)):
                    st.markdown(f"**⛳ {idx+1}조 설정**")
                    gc1, gc2 = st.columns(2)
                    with gc1:
                        t_val = st.text_input(f"{idx+1}조 티오프 시간", value=f"08:{(idx*8):02d}", key=f"tee_group_{idx}")
                        group_tee_times.append(t_val)
                    with gc2:
                        c_val = st.text_input(f"{idx+1}조 코스 정보", value="IN 코스" if idx%2==1 else "OUT 코스", key=f"course_group_{idx}")
                        group_courses.append(c_val)

                date_str = r_date_input.strftime("%Y-%m-%d")
                
                notice_text = f"📢 [필드 월례회 조편성 공식 안내]\n\n"
                notice_text += f"🗓️ 일정: {date_str}  |  🏟️ 장소: {golf_location or '장소 미입력'}\n"
                notice_text += f"----------------------------------------\n"
                for idx, team in enumerate(teams):
                    t_time = group_tee_times[idx] if idx < len(group_tee_times) else "미정"
                    c_info = group_courses[idx] if idx < len(group_courses) else "미정"
                    team_str = ", ".join(team)
                    notice_text += f"• {idx+1}조 ({t_time} / {c_info}): {team_str}\n"
                notice_text += f"----------------------------------------\n"
                notice_text += f"즐거운 라운딩 되세요! 🏌️‍♂️✨"

                for idx, team in enumerate(teams):
                    t_time = group_tee_times[idx] if idx < len(group_tee_times) else "미정"
                    c_info = group_courses[idx] if idx < len(group_courses) else ""
                    team_html = f"<div class='team-box'><h3>⛳ {idx+1}조 ({t_time})</h3><div style='font-size:0.8rem; color:#E5C585; margin-bottom:6px;'>🏟️ {c_info}</div>" + "<br>".join([f"• <b>{m}</b> ({member_db.get(m, {}).get('handicap', 0)})" for m in team]) + "</div>"
                    st.markdown(team_html, unsafe_allow_html=True)
                
                st.subheader("📱 카카오톡 공지문 복사 (아래 복사 버튼 클릭)")
                st.code(notice_text, language="text")
                
                if st.button("💾 조편성 저장 및 경기 결과 카드 생성", use_container_width=True):
                    for team in teams:
                        for i in range(len(team)):
                            for j in range(i + 1, len(team)):
                                m1, m2 = team[i], team[j]
                                if m1 in pair_history and m2 in pair_history[m1]:
                                    pair_history[m1][m2] += 1
                                    pair_history[m2][m1] += 1
                                    
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    match_logs.insert(0, {
                        "id": len(match_logs) + 1,
                        "date": now_str,
                        "event_type": "필드 월례회",
                        "teams": teams
                    })
                    
                    round_entry = {
                        "id": int(datetime.now().timestamp()),
                        "title": f"{r_date_input.month}월 정기 필드 월례회 ({golf_location or '필드'})",
                        "date": date_str,
                        "type": "필드 월례회",
                        "teams": teams,
                        "scores": {},
                        "completed": False,
                        "awards": {"medalist": "-", "longist": "-", "nearest": "-"}
                    }
                    rounds_data.insert(0, round_entry)
                    
                    save_data(db)
                    st.success("🎉 조편성이 저장되었으며, [경기 결과] 메뉴에 성적 입력 카드가 생성되었습니다! (위 코드 박스의 복사 버튼을 눌러 카카오톡에 공유하세요)")

    # 4. 🏆 경기 결과 및 랭킹
    elif menu == "경기 결과 및 랭킹":
        st.subheader("🏆 경기 결과 및 랭킹")
        
        field_rounds = [r for r in rounds_data if "필드" in r.get("type", "")]
        
        if not field_rounds:
            st.info("등록된 필드 경기 결과가 없습니다. 운영진이 필드 조편성을 확정하면 입력 카드가 생성됩니다.")
        else:
            selected_round_title = st.selectbox(
                "조회할 라운드 선택", 
                [f"{r['date']} | {r['title']} ({'입력 완료' if r.get('completed') else '입력 대기'})" for r in field_rounds]
            )
            selected_r_idx = [f"{r['date']} | {r['title']} ({'입력 완료' if r.get('completed') else '입력 대기'})" for r in field_rounds].index(selected_round_title)
            r = field_rounds[selected_r_idx]
            
            is_done = r.get("completed", False)
            status_tag = "✅ 성적 입력 완료" if is_done else "⌛ 성적 입력 대기 중"
            
            st.markdown(f"""
            <div class="css-card" style="margin-top: 15px;">
                <h3 style="color:#1B3B2B; margin-top:0; font-size:1.1rem;">🚩 {r['date']} | {r['title']} [{status_tag}]</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if is_done:
                st.markdown(f"""
                <div class="css-card">
                    <h4 style="color:#A88B58; margin-bottom:8px; font-size:1rem;">🏆 공식 시상 내역</h4>
                    <p style="margin:4px 0;">🥇 <b>메달리스트:</b> {r['awards']['medalist']}</p>
                    <p style="margin:4px 0;">💣 <b>롱기스트:</b> {r['awards']['longist']}</p>
                    <p style="margin:4px 0;">🎯 <b>니어리스트:</b> {r['awards']['nearest']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("##### 📊 회원별 스코어 기록표")
                score_table = []
                for p_name, p_info in r['scores'].items():
                    score_table.append({
                        "회원(닉네임)": f"{p_name} ({member_db.get(p_name, {}).get('nickname', p_name)})",
                        "스코어": f"{p_info['score']}타",
                        "비거리": f"{p_info['long']}m" if p_info['long'] > 0 else "-",
                        "니어": f"{p_info['near']}m" if p_info['near'] > 0 else "-"
                    })
                st.table(pd.DataFrame(score_table))
                
            if is_admin:
                st.markdown("---")
                btn_label = "✏️ 해당 라운드 성적 수정하기" if is_done else "✍️ 해당 라운드 스코어/롱기/니어 입력하기"
                with st.expander(btn_label):
                    teams = r.get("teams", [])
                    entered_mod_scores = {}
                    
                    if teams:
                        for t_idx, team in enumerate(teams):
                            st.markdown(f"##### ⛳ {t_idx+1}조")
                            for m in team:
                                curr = r.get("scores", {}).get(m, {"score": 85, "long": 0, "near": 0.0})
                                m_nick = member_db.get(m, {}).get("nickname", m)
                                c1, c2, c3 = st.columns(3)
                                with c1:
                                    sc = st.number_input(f"[{m_nick}] 스코어", min_value=50, max_value=140, value=curr['score'], key=f"sc_{r['id']}_{m}")
                                with c2:
                                    ld = st.number_input(f"[{m_nick}] 비거리(m)", min_value=0, max_value=350, value=curr['long'], key=f"ld_{r['id']}_{m}")
                                with c3:
                                    nd = st.number_input(f"[{m_nick}] 니어(m)", min_value=0.0, max_value=50.0, value=float(curr['near']), step=0.1, key=f"nd_{r['id']}_{m}")
                                entered_mod_scores[m] = {"score": sc, "long": ld, "near": nd}
                    else:
                        approved_names = [k for k, v in member_db.items() if v.get("status", "approved") == "approved"]
                        sel_mems = st.multiselect("참석 회원 선택", approved_names, default=list(r.get("scores", {}).keys()), key=f"melsel_{r['id']}")
                        for m in sel_mems:
                            curr = r.get("scores", {}).get(m, {"score": 85, "long": 0, "near": 0.0})
                            m_nick = member_db.get(m, {}).get("nickname", m)
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                sc = st.number_input(f"[{m_nick}] 스코어", min_value=50, max_value=140, value=curr['score'], key=f"sc_{r['id']}_{m}")
                            with c2:
                                ld = st.number_input(f"[{m_nick}] 비거리(m)", min_value=0, max_value=350, value=curr['long'], key=f"ld_{r['id']}_{m}")
                            with c3:
                                nd = st.number_input(f"[{m_nick}] 니어(m)", min_value=0.0, max_value=50.0, value=float(curr['near']), step=0.1, key=f"nd_{r['id']}_{m}")
                            entered_mod_scores[m] = {"score": sc, "long": ld, "near": nd}

                    if st.button("🏆 성적 최종 저장 및 시상 자동 계산", key=f"sv_rnd_{r['id']}", use_container_width=True):
                        if entered_mod_scores:
                            r['scores'] = entered_mod_scores
                            r['completed'] = True
                            
                            medalist = min(entered_mod_scores.items(), key=lambda x: x[1]["score"])
                            v_longs = {k: v for k, v in entered_mod_scores.items() if v["long"] > 0}
                            longist = max(v_longs.items(), key=lambda x: x[1]["long"]) if v_longs else None
                            v_nears = {k: v for k, v in entered_mod_scores.items() if v["near"] > 0}
                            nearest = min(v_nears.items(), key=lambda x: x[1]["near"]) if v_nears else None
                            
                            medalist_nick = member_db.get(medalist[0], {}).get("nickname", medalist[0])
                            longist_nick = member_db.get(longist[0], {}).get("nickname", longist[0]) if longist else ""
                            nearest_nick = member_db.get(nearest[0], {}).get("nickname", nearest[0]) if nearest else ""
                            
                            r['awards'] = {
                                "medalist": f"{medalist_nick} ({medalist[1]['score']}타)",
                                "longist": f"{longist_nick} ({longist[1]['long']}m)" if longist else "기록 없음",
                                "nearest": f"{nearest_nick} ({nearest[1]['near']}m)" if nearest else "기록 없음",
                                "raw_medalist": medalist[0],
                                "raw_longist": longist[0] if longist else None,
                                "raw_nearest": nearest[0] if nearest else None,
                                "raw_medalist_score": medalist[1]['score'],
                                "raw_longist_dist": longist[1]['long'] if longist else 0,
                                "raw_nearest_dist": nearest[1]['near'] if nearest else 999
                            }
                            recalculate_all_stats(db)
                            save_data(db)
                            st.success("🎉 성적이 성공적으로 등록되었습니다!")
                            st.rerun()

                with st.expander("🗑️ 라운드 삭제 관리"):
                    conf_rnd = st.checkbox("정말로 이 라운드 기록을 삭제하시겠습니까?", key=f"conf_rnd_{r['id']}")
                    if conf_rnd:
                        if st.button(f"⚠️ 최종 라운드 삭제 실행", key=f"btn_del_rnd_{r['id']}", type="primary", use_container_width=True):
                            rounds_data.remove(r)
                            recalculate_all_stats(db)
                            save_data(db)
                            st.success("해당 라운드가 삭제되었습니다.")
                            st.rerun()

        # --- 누적 통계 & 랭킹 ---
        st.divider()
        st.subheader("📊 클럽 누적 통계 & 랭킹")
        
        completed_r = [r for r in field_rounds if r.get("completed")]
        
        if not completed_r:
            st.warning("아직 완료된 필드 라운드가 없습니다.")
        else:
            medalist_records = []
            longist_records = []
            nearest_records = []
            attendance_counts = {}

            for r in completed_r:
                r_info_str = f"{r['date']} ({r['title']})"
                awards = r.get("awards", {})
                raw_m = awards.get("raw_medalist")
                raw_l = awards.get("raw_longist")
                raw_n = awards.get("raw_nearest")
                
                m_score = awards.get("raw_medalist_score", 0)
                l_dist = awards.get("raw_longist_dist", 0)
                n_dist = awards.get("raw_nearest_dist", 999)

                if raw_m:
                    medalist_records.append({"member": raw_m, "score": m_score, "round": r_info_str})
                if raw_l and l_dist > 0:
                    longist_records.append({"member": raw_l, "dist": l_dist, "round": r_info_str})
                if raw_n and n_dist < 999:
                    nearest_records.append({"member": raw_n, "dist": n_dist, "round": r_info_str})

                for m_name in r.get("scores", {}).keys():
                    attendance_counts[m_name] = attendance_counts.get(m_name, 0) + 1

            st.markdown("##### 🥇 최저타(메달리스트) 랭킹")
            if medalist_records:
                m_df_raw = pd.DataFrame(medalist_records)
                m_agg = m_df_raw.groupby("member").agg(
                    우승횟수=("score", "count"),
                    최저타수=("score", "min"),
                    달성라운드=("round", lambda x: ", ".join(x))
                ).reset_index().sort_values(by=["우승횟수", "최저타수"], ascending=[False, True]).head(10)
                
                m_agg["회원"] = m_agg["member"].apply(lambda x: member_db.get(x, {}).get("nickname", x))
                display_m = m_agg[["회원", "우승횟수", "최저타수", "달성라운드"]].copy()
                display_m["우승횟수"] = display_m["우승횟수"].astype(str) + "회"
                display_m["최소 타수"] = display_m["최저타수"].astype(str) + "타"
                display_m = display_m.drop(columns=["최저타수"])
                display_m.index += 1
                st.table(display_m)

            st.markdown("##### 💣 롱기스트(최장타) 랭킹")
            if longist_records:
                l_df_raw = pd.DataFrame(longist_records)
                l_agg = l_df_raw.groupby("member").agg(
                    달성횟수=("dist", "count"),
                    최고비거리=("dist", "max"),
                    달성라운드=("round", lambda x: ", ".join(x))
                ).reset_index().sort_values(by=["달성횟수", "최고비거리"], ascending=[False, False]).head(10)
                
                l_agg["회원"] = l_agg["member"].apply(lambda x: member_db.get(x, {}).get("nickname", x))
                display_l = l_agg[["회원", "달성횟수", "최고비거리", "달성라운드"]].copy()
                display_l["달성 횟수"] = display_l["달성횟수"].astype(str) + "회"
                display_l["최고 비거리"] = display_l["최고비거리"].astype(str) + "m"
                display_l = display_l.drop(columns=["달성횟수", "최고비거리"])
                display_l.index += 1
                st.table(display_l)

    # 5. 👑 명예의 전당
    elif menu == "명예의 전당":
        st.subheader("👑 명예의 전당 및 회원별 기록실")
        st.caption("클럽 회원들의 개인별 라운딩 스코어 이력, 평균 타수 및 출석 현황을 확인합니다.")
        
        approved_members = [k for k, v in member_db.items() if v.get("status", "approved") == "approved"]
        selected_member_name = st.selectbox("🔍 조회할 회원 선택", approved_members)
        
        if selected_member_name:
            m_info = member_db.get(selected_member_name, {})
            m_nick = m_info.get("nickname", selected_member_name)
            m_hc = m_info.get("handicap", 0)
            m_att = m_info.get("attendance", 0)
            m_rounds_cnt = m_info.get("rounds_played", 0)
            m_history = m_info.get("score_history", [])
            
            avg_sc = round(sum(m_history) / len(m_history), 1) if m_history else 0
            
            st.markdown(f"""
            <div class="css-card" style="background: linear-gradient(135deg, #1B3B2B 0%, #2C523D 100%); color: #FFFFFF; padding: 18px; border-radius: 12px;">
                <h3 style="margin:0 0 8px 0; color: #E5C585; font-size:1.1rem;">👤 {selected_member_name} ({m_nick}) 회원님</h3>
                <div style="font-size: 0.85rem; line-height: 1.6;">
                    🎯 <b>핸디캡:</b> {m_hc} | 📈 <b>평균 스코어:</b> {avg_sc}타<br>
                    ⛳ <b>총 참석:</b> {m_rounds_cnt}회 | 📅 <b>참석률:</b> {m_att}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("##### 🏌️‍♂️ 라운드별 상세 스코어 및 출석 내역")
            field_rounds = [r for r in rounds_data if "필드" in r.get("type", "") and r.get("completed")]
            
            if not field_rounds:
                st.info("등록된 완료된 필드 라운드가 없습니다.")
            else:
                member_rounds_data = []
                for r in field_rounds:
                    scores_dict = r.get("scores", {})
                    if selected_member_name in scores_dict:
                        p_data = scores_dict[selected_member_name]
                        member_rounds_data.append({
                            "날짜": r['date'],
                            "라운드 명칭": r['title'],
                            "참석": "출석 ✅",
                            "스코어": f"{p_data['score']}타",
                            "비거리": f"{p_data['long']}m" if p_data['long'] > 0 else "-",
                            "니어": f"{p_data['near']}m" if p_data['near'] > 0 else "-"
                        })
                    else:
                        member_rounds_data.append({
                            "날짜": r['date'],
                            "라운드 명칭": r['title'],
                            "참석": "결석 ❌",
                            "스코어": "-",
                            "비거리": "-",
                            "니어": "-"
                        })
                
                df_m_rounds = pd.DataFrame(member_rounds_data)
                st.table(df_m_rounds)

    # 6. 📁 역대 조편성 아카이브
    elif menu == "역대 조편성 아카이브":
        st.subheader("📁 역대 조편성 아카이브")
        if not match_logs:
            st.warning("아직 저장된 조편성 이력이 없습니다.")
        else:
            log_options = [f"{log['date']} | {log['event_type']}" for log in match_logs]
            selected_log_label = st.selectbox("📂 조회할 조편성 이력 선택", log_options)
            selected_log_idx = log_options.index(selected_log_label)
            log = match_logs[selected_log_idx]
            
            st.markdown(f"### 🗓️ {log['date']} | {log['event_type']}")
            
            if is_admin:
                with st.expander("🗑️ 조편성 이력 삭제 관리"):
                    conf_log = st.checkbox("정말로 이 조편성 이력을 삭제하시겠습니까?", key=f"conf_log_{selected_log_idx}")
                    if conf_log:
                        if st.button("⚠️ 최종 이력 삭제 실행", key=f"btn_del_log_{selected_log_idx}", type="primary", use_container_width=True):
                            match_logs.pop(selected_log_idx)
                            save_data(db)
                            st.success("해당 조편성 이력이 삭제되었습니다.")
                            st.rerun()
                    
            st.markdown("---")
            cols = st.columns(min(len(log['teams']), 4))
            for t_idx, team in enumerate(log['teams']):
                with cols[t_idx % 4]:
                    team_names = ", ".join([f"{m}({member_db.get(m, {}).get('handicap', '0')})" for m in team])
                    st.markdown(f"**⛳ {t_idx+1}조:** {team_names}")

    # 7. 👥 회원 리스트
    elif menu.startswith("회원 리스트") or menu.startswith("회원 명부"):
        st.subheader("👥 클럽 회원 리스트")
        
        df_data = [{
            "성함": k, 
            "닉네임": v.get('nickname', k),
            "핸디캡": v.get('handicap', 0), 
            "참석률": f"{v.get('attendance', 0)}%", 
            "참석": f"{v.get('rounds_played', 0)}회"
        } for k, v in member_db.items() if v.get("status", "approved") == "approved"]
        
        st.table(pd.DataFrame(df_data))
        
        if is_admin:
            st.divider()
            st.subheader("👑 [운영진 전용] 신입회원 가입 승인 센터")
            pending_members = [k for k, v in member_db.items() if v.get("status") == "pending"]
            
            if not pending_members:
                st.info("현재 가입 승인 대기 중인 회원이 없습니다.")
            else:
                for p_name in pending_members:
                    col_p1, col_p2 = st.columns([3, 1])
                    with col_p1:
                        st.write(f"👤 **가입 대기 회원:** `{p_name}`")
                    with col_p2:
                        if st.button(f"✅ {p_name} 승인", key=f"app_{p_name}", use_container_width=True):
                            member_db[p_name]["status"] = "approved"
                            save_data(db)
                            st.success(f"🎉 {p_name} 회원의 가입이 최종 승인되었습니다!")
                            st.rerun()

            st.divider()
            st.subheader("🚫 [운영진 전용] 회원 강퇴 관리")
            expel_candidates = [k for k in member_db.keys() if k != current_user and member_db[k].get("status", "approved") == "approved"]
            if expel_candidates:
                target_expel = st.selectbox("강퇴할 회원 선택", expel_candidates, key="target_expel")
                with st.expander("⚠️ 회원 강퇴 실행"):
                    conf_expel = st.checkbox(f"정말로 '{target_expel}' 회원을 클럽에서 강퇴하시겠습니까?", key="conf_expel")
                    if conf_expel:
                        if st.button("🚨 최종 강퇴 실행", type="primary", key="btn_expel", use_container_width=True):
                            member_db.pop(target_expel, None)
                            save_data(db)
                            st.success(f"'{target_expel}' 회원이 강퇴 조치되었습니다.")
                            st.rerun()
            else:
                st.info("강퇴할 수 있는 회원이 없습니다.")

    # 8. 👤 마이페이지
    elif menu == "마이페이지":
        st.subheader("👤 마이페이지 & 프로필 설정")
        st.info("💡 회원 성함, 닉네임, 비밀번호, 프로필 사진 변경 및 클럽 탈퇴를 관리할 수 있습니다.")
        
        with st.form("edit_profile_form"):
            edit_name = st.text_input("회원 성함", value=current_user)
            edit_nickname = st.text_input("클럽 닉네임", value=user_info.get("nickname", current_user))
            edit_pw = st.text_input("비밀번호 변경", value=user_info.get("password", "1234"), type="password")
            
            p_img_file = st.file_uploader("프로필 아바타 등록 (선택)", type=["jpg", "png", "jpeg"])
            if user_info.get("profile_img"):
                st.image(base64.b64decode(user_info["profile_img"]), width=100, caption="현재 등록된 프로필 사진")
                
            submit_btn = st.form_submit_button("💾 정보 저장하기", type="primary", use_container_width=True)
            
            if submit_btn:
                if edit_name != current_user:
                    if edit_name in member_db:
                        st.error("이미 존재하는 회원 성함입니다.")
                    else:
                        member_db[edit_name] = member_db.pop(current_user)
                        st.session_state.logged_in_user = edit_name
                        current_user = edit_name
                
                user_info['nickname'] = edit_nickname
                user_info['password'] = edit_pw
                
                if p_img_file is not None:
                    img_bytes = p_img_file.getvalue()
                    user_info['profile_img'] = base64.b64encode(img_bytes).decode()
                    
                save_data(db)
                st.success("🎉 마이페이지 정보가 성공적으로 업데이트되었습니다!")
                st.rerun()

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("##### 🚪 세션 관리: 로그아웃")
        if st.button("🚪 클럽 로그아웃", type="secondary", use_container_width=True, key="mypage_logout"):
            st.session_state.logged_in_user = None
            set_menu("HOME")
            try:
                st.query_params.clear()
            except Exception:
                pass
            st.rerun()

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("##### ❌ 위험 구역: 클럽 탈퇴")
        with st.expander("⚠️ 클럽 탈퇴하기 (계정 삭제)"):
            conf_withdraw = st.checkbox("정말로 클럽에서 탈퇴하시겠습니까? 계정 정보가 영구 삭제됩니다.", key="conf_withdraw_mypage")
            if conf_withdraw:
                if st.button("🚨 최종 클럽 탈퇴 실행", type="primary", key="btn_withdraw_mypage", use_container_width=True):
                    member_db.pop(current_user, None)
                    save_data(db)
                    st.session_state.logged_in_user = None
                    set_menu("HOME")
                    st.success("클럽 탈퇴가 정상적으로 처리되었습니다.")
                    st.rerun()
