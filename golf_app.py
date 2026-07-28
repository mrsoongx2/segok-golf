import streamlit as st
import pandas as pd
import numpy as np
import random
import json
import os
import base64
from datetime import datetime, time

st.set_page_config(
    page_title="SEGOK GOLF CLUB", 
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
    "진지영", "최성준", "최승락", "황성준", "최혁중"
]

COUPLES_LIST = [
    ("김성모", "김지윤"),
    ("김경수", "이진아"),
    ("Kim Shawn", "이주원"),
    ("김동숙", "김현태"),
    ("김미화", "이승준"),
    ("이승환", "진지영"),
    ("이윤진", "황성준"),
    ("임혜영", "최혁중")
]

FEMALE_SET = {"김지윤", "김동숙", "김미화", "김주연", "이민숙", "이윤진", "이주원", "이진아", "임혜영", "진지영"}

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
                    for notice in data.get("notices", []):
                        if "media_path" not in notice:
                            notice["media_path"] = None
                            notice["media_type"] = None
                        if "file_path" not in notice:
                            notice["file_path"] = None
                            notice["file_name"] = None
                        if "poll" not in notice:
                            notice["poll"] = None
                    for post in data.get("feed_posts", []):
                        if "liked_users" not in post:
                            post["liked_users"] = []
                        if "poll" not in post:
                            post["poll"] = None
                        else:
                            if "is_anonymous" not in post["poll"]:
                                post["poll"]["is_anonymous"] = False
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
query_menu = "HOME"
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
else:
    if query_menu and query_menu != st.session_state.current_menu:
        st.session_state.current_menu = query_menu

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
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    .stApp { background-color: #F4F6F4 !important; font-family: 'Noto Sans KR', sans-serif; color: #1E2923; font-size: 0.9rem; }
    
    h2 { font-size: 1.15rem !important; font-weight: 700 !important; color: #0F2E1B !important; margin-bottom: 0.5rem !important; }
    h3 { font-size: 1.05rem !important; font-weight: 700 !important; color: #0F2E1B !important; }
    
    .logo-hero { 
        text-align: center; 
        padding: 35px 15px; 
        background: linear-gradient(135deg, #0F2E1B 0%, #1B4D33 50%, #123822 100%); 
        border-radius: 16px; 
        color: #FFFFFF; 
        margin-bottom: 20px; 
        box-shadow: 0 8px 24px rgba(15,46,27,0.18); 
        border: 1px solid rgba(212,180,117,0.3);
    }
    .logo-hero h1 { 
        font-family: 'Montserrat', sans-serif; 
        font-size: 1.8rem; 
        font-weight: 800; 
        letter-spacing: 2px; 
        margin: 6px 0 4px 0; 
        color: #F8F5F0; 
        text-transform: uppercase;
    }
    .logo-hero p { 
        color: #D4B475; 
        font-size: 0.65rem; 
        letter-spacing: 3px; 
        text-transform: uppercase; 
        font-weight: 600; 
        margin: 0; 
        font-family: 'Montserrat', sans-serif;
    }
    
    .menu-card-box { 
        background-color: #FFFFFF; 
        border-radius: 12px; 
        border: 1px solid #E2E8F0; 
        padding: 18px 14px; 
        text-align: center; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); 
        transition: all 0.25s ease; 
        margin-bottom: 8px;
        height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .menu-card-box:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 6px 16px rgba(27,77,51,0.1); 
        border-color: #1B4D33; 
    }
    .menu-card-box h3 { 
        font-family: 'Montserrat', sans-serif;
        font-size: 0.92rem; 
        font-weight: 700;
        margin-bottom: 4px; 
        color: #0F2E1B; 
        text-transform: uppercase;
    }
    .menu-card-box p { 
        color: #64748B; 
        font-size: 0.72rem; 
        margin: 0; 
        line-height: 1.2; 
    }
    
    .band-card { background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; max-width: 100%; margin: 0 auto 16px auto; box-shadow: 0 2px 6px rgba(0,0,0,0.03); overflow: hidden; }
    .band-header { display: flex; align-items: center; padding: 12px 14px; border-bottom: 1px solid #F1F5F9; background-color: #FAFAFA; }
    .band-body { padding: 14px; font-size: 0.88rem; color: #1E2923; line-height: 1.5; }
    
    .team-box { background-color: #0F2E1B; color: #FFFFFF; padding: 14px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #D4B475; font-size: 0.85rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .team-box h3 { color: #E5C585 !important; font-family: 'Montserrat', sans-serif; font-size: 0.95rem; margin-bottom: 6px; border-bottom: 1px solid #235C3D; padding-bottom: 4px; }
    
    .badge-admin { background-color: #0F2E1B; color: #FFFFFF; padding: 2px 6px; border-radius: 6px; font-size: 0.65rem; font-weight: 700; border: 1px solid #D4B475; font-family: 'Montserrat', sans-serif; }
    .badge-user { background-color: #E2E8F0; color: #334155; padding: 2px 6px; border-radius: 6px; font-size: 0.65rem; font-weight: 700; font-family: 'Montserrat', sans-serif; }
    .badge-hc { background-color: #FEF3C7; color: #92400E; padding: 2px 6px; border-radius: 6px; font-size: 0.65rem; font-weight: 800; border: 1px solid #FDE68A; font-family: 'Montserrat', sans-serif; }
    
    .new-badge { background-color: #16A34A; color: #FFFFFF; padding: 2px 5px; border-radius: 6px; font-size: 0.6rem; font-weight: 800; vertical-align: middle; margin-left: 4px; font-family: 'Montserrat', sans-serif; }
    
    .stButton>button { 
        background: linear-gradient(135deg, #1B4D33 0%, #0F2E1B 100%) !important; 
        color: #FFFFFF !important; 
        border-radius: 8px !important; 
        border: none !important; 
        font-weight: 700 !important; 
        width: 100% !important; 
        height: 40px !important;
        font-size: 0.82rem !important; 
        box-shadow: 0 3px 8px rgba(27,77,51,0.2);
        font-family: 'Montserrat', 'Noto Sans KR', sans-serif;
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, #235C3D 100%, #164027 100%) !important; 
    }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN & SIGNUP ---
if not st.session_state.get('logged_in_user'):
    st.markdown("""
    <div style="text-align: center; padding: 35px 15px 20px 15px;">
        <div style="font-size: 2.8rem;">⛳</div>
        <h1 style="font-family: 'Montserrat', sans-serif; color: #0F2E1B; margin: 6px 0 0 0; font-size: 1.8rem; font-weight: 800; letter-spacing: 1px;">SEGOK GOLF CLUB</h1>
        <p style="color: #64748B; font-size: 0.7rem; letter-spacing: 3px; text-transform: uppercase; font-weight: 700; font-family: 'Montserrat', sans-serif;">PREMIUM GOLF SOCIETY</p>
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
                        st.success("등록되었습니다!")
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
                        st.success("등록되었습니다!")
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
admin_badge = '<span class="badge-admin">👑 OP</span>' if is_admin else '<span class="badge-user">👤 MEM</span>'
hc_val = user_info.get('handicap', 0)

last_n = user_info.get("last_notice_seen", "")
latest_notice_date = notices[0]["date"] if notices else ""
has_new_notice = latest_notice_date > last_n if latest_notice_date else False

last_l = user_info.get("last_lounge_seen", "")
latest_lounge_date = feed_posts[0]["date"] if feed_posts else ""
has_new_lounge = latest_lounge_date > last_l if latest_lounge_date else False

unread_notices_count = len([n for n in notices if n["date"] > last_n]) if last_n else len(notices)
unread_lounge_count = len([p for p in feed_posts if p["date"] > last_l]) if last_l else len(feed_posts)
total_unread_alerts = unread_notices_count + unread_lounge_count

alert_badge_label = f"🔔 INBOX ({total_unread_alerts})" if total_unread_alerts > 0 else "🔔 INBOX"

# --- 상단 고정 헤더 ---
col_h1, col_h2 = st.columns([1.2, 1.2])
with col_h1:
    left_header_cols = st.columns([1, 1])
    with left_header_cols[0]:
        if st.button("⛳ SEGOK", key="logo_home_btn", use_container_width=True):
            set_menu("HOME")
            st.rerun()
    with left_header_cols[1]:
        if st.button(alert_badge_label, key="header_inbox_btn", use_container_width=True):
            set_menu("알림 센터")
            st.rerun()
with col_h2:
    st.markdown(f"""
    <div style="text-align: right; padding-top: 6px; font-size: 0.82rem; white-space: nowrap;">
        <b>{display_nickname}</b>님 <span class="badge-hc">HC {hc_val}</span> {admin_badge}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 6px 0 12px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

if st.session_state.current_menu == "HOME":
    st.markdown("""
    <div class="logo-hero">
        <div style="font-size: 2.5rem; margin-bottom: 4px;">⛳</div>
        <h1>SEGOK GOLF CLUB</h1>
        <p>PREMIUM GOLF SOCIETY & COMMUNITY</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    
    with c1:
        notice_badge = '<span class="new-badge">NEW</span>' if has_new_notice else ''
        st.markdown(f"""
        <div class="menu-card-box">
            <h3>📢 NOTICE{notice_badge}</h3>
            <p>클럽 소식 및 조편성 안내</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("공지사항 입장", use_container_width=True, key="go_notice"):
            set_menu("클럽 공지사항")
            st.rerun()
            
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        lounge_badge = '<span class="new-badge">NEW</span>' if has_new_lounge else ''
        st.markdown(f"""
        <div class="menu-card-box">
            <h3>💬 CLUB LOUNGE{lounge_badge}</h3>
            <p>자유 소통, 투표 및 파일 공유</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("클럽 라운지 입장", use_container_width=True, key="go_lounge"):
            set_menu("클럽 라운지")
            st.rerun()

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="menu-card-box">
            <h3>📁 ARCHIVE</h3>
            <p>지난 날짜별 조편성 기록 확인</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("아카이브 입장", use_container_width=True, key="go_archive"):
            set_menu("역대 조편성 아카이브")
            st.rerun()

    with c2:
        st.markdown("""
        <div class="menu-card-box">
            <h3>🏆 RESULTS</h3>
            <p>역대 스코어 및 공식 시상</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("경기 결과 입장", use_container_width=True, key="go_result"):
            set_menu("경기 결과 및 랭킹")
            st.rerun()
            
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="menu-card-box">
            <h3>👑 HALL OF FAME</h3>
            <p>회원별 평균타수 및 출석 현황</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("명예의 전당 입장", use_container_width=True, key="go_records"):
            set_menu("명예의 전당")
            st.rerun()

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="menu-card-box">
            <h3>👤 MY PAGE</h3>
            <p>프로필, 로그아웃 및 클럽 탈퇴</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("마이페이지 입장", use_container_width=True, key="go_mypage"):
            set_menu("마이페이지")
            st.rerun()

    if is_admin:
        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        ac1, ac2 = st.columns(2)
        with ac1:
            st.markdown("""
            <div class="menu-card-box">
                <h3>⛳ MATCH</h3>
                <p>맞춤형 조편성 및 수동 복사</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("조편성 실행", use_container_width=True, key="go_match"):
                set_menu("티타임 조편성")
                st.rerun()
        with ac2:
            pending_cnt = len([k for k, v in member_db.items() if v.get("status") == "pending"])
            badge_txt = f" (대기 {pending_cnt})" if pending_cnt > 0 else ""
            st.markdown(f"""
            <div class="menu-card-box">
                <h3>👥 MEMBERS{badge_txt}</h3>
                <p>정회원 관리 및 가입 승인</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("회원 리스트 관리", use_container_width=True, key="go_members"):
                set_menu("회원 리스트")
                st.rerun()

else:
    notice_label = f"📢 공지사항 (NOTICE) {'🟢' if has_new_notice else ''}"
    lounge_label = f"💬 클럽 라운지 (CLUB LOUNGE) {'🟢' if has_new_lounge else ''}"
    
    menu_list = ["메인 홈", notice_label, lounge_label, "🏆 경기 결과 및 랭킹 (RESULTS)", "👑 명예의 전당 (HALL OF FAME)", "📁 조편성 아카이브 (ARCHIVE)", "👤 마이페이지 (MY PAGE)"]
    if is_admin:
        menu_list.insert(3, "⛳ 티타임 조편성 (MATCH)")
        menu_list.append("👥 회원 리스트 (MEMBERS)")
        
    current_label_map = {
        "HOME": "메인 홈",
        "클럽 공지사항": notice_label,
        "클럽 라운지": lounge_label,
        "알림 센터": "알림 센터",
        "티타임 조편성": "⛳ 티타임 조편성 (MATCH)",
        "경기 결과 및 랭킹": "🏆 경기 결과 및 랭킹 (RESULTS)",
        "명예의 전당": "👑 명예의 전당 (HALL OF FAME)",
        "역대 조편성 아카이브": "📁 조편성 아카이브 (ARCHIVE)",
        "회원 리스트": "👥 회원 리스트 (MEMBERS)",
        "마이페이지": "👤 마이페이지 (MY PAGE)"
    }
    reverse_map = {v: k for k, v in current_label_map.items()}
    curr_label = current_label_map.get(st.session_state.current_menu, notice_label)

    nav_c1, _ = st.columns([1, 0.01])
    with nav_c1:
        nav_index = menu_list.index(curr_label) if curr_label in menu_list else 0
        selected_nav = st.selectbox("📌 QUICK MENU", menu_list, index=nav_index)
        target_menu = reverse_map.get(selected_nav, "HOME")
        if "공지사항" in selected_nav: target_menu = "클럽 공지사항"
        elif "라운지" in selected_nav: target_menu = "클럽 라운지"
        
        if target_menu != st.session_state.current_menu:
            set_menu(target_menu)
            st.rerun()

    st.markdown("<hr style='margin: 8px 0 10px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    
    menu = st.session_state.current_menu

    # 1. 🔔 알림 센터 (인박스)
    if menu == "알림 센터":
        st.subheader("🔔 INBOX (알림 센터)")
        st.caption("읽지 않은 공지사항, 클럽 라운지 새 글 및 내 게시물에 달린 댓글을 모아봅니다.")

        if st.button("✔️ 모든 알림 읽음 처리", type="primary", use_container_width=True):
            if notices:
                user_info["last_notice_seen"] = notices[0]["date"]
            if feed_posts:
                user_info["last_lounge_seen"] = feed_posts[0]["date"]
            save_data(db)
            st.success("수정되었습니다!")
            st.rerun()

        st.markdown("---")

        st.markdown("##### 📢 미확인 공지사항")
        unread_notices = [n for n in notices if n["date"] > last_n] if last_n else notices
        if not unread_notices:
            st.info("새로운 공지사항이 없습니다.")
        else:
            for n in unread_notices:
                st.markdown(f"""
                <div class="band-card" style="padding:10px;">
                    <strong>📌 {n['title']}</strong> <span style="font-size:0.75rem; color:#888;">({n['date']})</span>
                    <div style="font-size:0.85rem; color:#444; margin-top:4px;">{n['content'][:50]}...</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("공지사항으로 이동", key=f"go_n_{n['id']}"):
                    set_menu("클럽 공지사항")
                    st.rerun()

        st.markdown("##### 💬 미확인 클럽 라운지 소식")
        unread_posts = [p for p in feed_posts if p["date"] > last_l] if last_l else feed_posts
        if not unread_posts:
            st.info("새로운 클럽 라운지 소식이 없습니다.")
        else:
            for p in unread_posts:
                nick = member_db.get(p.get("author"), {}).get("nickname", p.get("author"))
                st.markdown(f"""
                <div class="band-card" style="padding:10px;">
                    <strong>💬 {nick}님의 새 글</strong> <span style="font-size:0.75rem; color:#888;">({p['date']})</span>
                    <div style="font-size:0.85rem; color:#444; margin-top:4px;">{p['content'][:50]}...</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("클럽 라운지로 이동", key=f"go_p_{p['id']}"):
                    set_menu("클럽 라운지")
                    st.rerun()

        st.markdown("##### 💬 내 게시물에 달린 댓글")
        my_posts = [p for p in feed_posts if p.get("author"] == current_user]
        my_comments_found = False
        for p in my_posts:
            comments = p.get("comments", [])
            if comments:
                my_comments_found = True
                for c in comments:
                    c_nick = member_db.get(c.get('author'), {}).get('nickname', c.get('author'))
                    st.markdown(f"""
                    <div class="band-card" style="padding:8px; font-size:0.85rem;">
                        내 글 ➔ <b>{c_nick}</b>님의 댓글: "{c['text']}"
                    </div>
                    """, unsafe_allow_html=True)
        if not my_comments_found:
            st.info("내 게시물에 달린 댓글이 없습니다.")

    # 2. 📢 클럽 공지사항
    elif menu == "클럽 공지사항":
        if notices:
            user_info["last_notice_seen"] = notices[0]["date"]
            save_data(db)
            
        st.subheader("📢 NOTICE (클럽 공지사항)")
        st.caption("세곡 골프클럽의 주요 소식과 안내 사항을 확인하세요.")
        
        if is_admin:
            with st.expander("✍️ [OPERATOR] 새 공지사항 등록하기 (사진/파일/투표 첨부)"):
                with st.form("notice_write_form"):
                    n_title = st.text_input("공지 제목")
                    n_content = st.text_area("공지 내용")
                    
                    col_n_u1, col_n_u2 = st.columns(2)
                    with col_n_u1:
                        n_uploaded_file = st.file_uploader("이미지 첨부 (선택)", type=["jpg", "png", "jpeg"], key="notice_img_up")
                    with col_n_u2:
                        n_doc_file = st.file_uploader("문서/엑셀 파일 첨부 (선택)", type=["xlsx", "xls", "pdf", "txt", "csv"], key="notice_doc_up")
                    
                    n_use_poll = st.checkbox("📊 투표 생성하기", key="notice_use_poll")
                    n_poll_question = st.text_input("투표 주제", placeholder="예: 정기 라운딩 참석 여부", key="notice_poll_q")
                    n_allow_multiple = st.checkbox("복수 선택 허용 (최대 3개까지 선택 가능)", key="notice_poll_multi")
                    n_is_anonymous = st.checkbox("익명 투표", key="notice_poll_anon")
                    
                    col_nd1, col_nd2 = st.columns(2)
                    with col_nd1:
                        nd_date = st.date_input("마감 날짜", value=datetime.now().date(), key="notice_poll_date")
                    with col_nd2:
                        nd_time = st.time_input("마감 시간", value=time(23, 59), key="notice_poll_time")

                    notice_submitted = st.form_submit_button("공지 발행", use_container_width=True)
                    
                    if notice_submitted:
                        if n_title and (n_content or n_uploaded_file or n_doc_file or n_use_poll):
                            n_media_path = None
                            n_media_type = None
                            if n_uploaded_file is not None:
                                file_name = f"{int(datetime.now().timestamp())}_{n_uploaded_file.name}"
                                n_media_path = os.path.join(UPLOAD_DIR, file_name)
                                with open(n_media_path, "wb") as f:
                                    f.write(n_uploaded_file.getbuffer())
                                n_media_type = "image"
                            
                            n_file_path = None
                            n_file_name = None
                            if n_doc_file is not None:
                                n_file_name = n_doc_file.name
                                n_file_path = os.path.join(UPLOAD_DIR, f"notice_doc_{int(datetime.now().timestamp())}_{n_file_name}")
                                with open(n_file_path, "wb") as f:
                                    f.write(n_doc_file.getbuffer())

                            n_poll_deadline = datetime.combine(nd_date, nd_time).strftime("%Y-%m-%d %H:%M")
                            n_poll_data = None
                            if n_use_poll and n_poll_question:
                                n_poll_data = {
                                    "question": n_poll_question,
                                    "deadline": n_poll_deadline,
                                    "allow_multiple": n_allow_multiple,
                                    "is_anonymous": n_is_anonymous,
                                    "options": {"참석": [], "불참": [], "미정": []}
                                }

                            notices.insert(0, {
                                "id": int(datetime.now().timestamp()),
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "title": n_title,
                                "content": n_content,
                                "media_path": n_media_path,
                                "media_type": n_media_type,
                                "file_path": n_file_path,
                                "file_name": n_file_name,
                                "poll": n_poll_data
                            })
                            save_data(db)
                            st.success("등록되었습니다!")
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
                            <strong style="color:#0F2E1B; font-size:0.95rem;">📌 {notice['title']}</strong><br>
                            <span style="color:#64748B; font-size:0.75rem;">{notice['date']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                n_m_path = notice.get("media_path")
                if n_m_path and os.path.exists(n_m_path):
                    st.image(n_m_path, use_column_width=True)

                n_f_path = notice.get("file_path")
                n_f_name = notice.get("file_name")
                if n_f_path and n_f_name and os.path.exists(n_f_path):
                    with open(n_f_path, "rb") as fp:
                        st.download_button(label=f"📎 첨부파일 다운로드: {n_f_name}", data=fp, file_name=n_f_name, key=f"notice_dl_{notice['id']}")

                if notice.get('content'):
                    st.markdown(f"""
                    <div class="band-body">
                        <p style="margin:0; color:#1E2923; word-break:break-all; white-space: pre-wrap; user-select: text;">{notice['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                n_poll = notice.get("poll")
                if n_poll:
                    deadline_str = n_poll.get("deadline", "")
글만 입력했을 때 등록이 정상적으로 완료되지 않고 첨부 화면으로 되돌아가는 현상은 주로 **폼 유효성 검사(Validation)** 나 **데이터 전송/상태 관리(State Management)** 로직의 문제일 가능성이 높습니다. 구체적인 원인과 점검해야 할 포인트는 다음과 같습니다.

### 주요 원인 분석

1. **필수 파일 첨부 조건 (Validation)**
   * 프론트엔드 코드나 백엔드 API 스키마에서 이미지 파일 업로드가 **필수값(Required)** 으로 설정되어 있을 수 있습니다. 이 경우, 텍스트만 입력하고 제출하면 파일이 없다는 유효성 검사 에러가 발생하면서 요청이 차단됩니다.
2. **FormData 및 상태 초기화 (State Reset)**
   * 텍스트 전송 시 `FormData` 객체에 빈 값이나 잘못된 파일 키가 들어가 서버에서 에러(예: 400 Bad Request)를 반환하고, 에러 핸들링 과정에서 컴포넌트 상태가 초기화되면서 첨부 화면으로 강제 이동(리셋)될 수 있습니다.
3. **이벤트 핸들러 분기 처리 오류**
   * 제출 버튼 클릭 시 이미지 유무(`if (file)`)에 따라 전송 로직이 분기되어 있는데, 파일이 없을 때의 예외 처리가 누락되었거나 `e.preventDefault()` 등이 올바르게 작동하지 않아 폼이 기본 동작으로 리셋되는 경우입니다.

---

### 해결을 위한 점검 항목

* **유효성 검사 로직 확인:** 파일 첨부 필드가 필수(`required`)로 지정되어 있다면, 텍스트 단독 등록 시에는 해당 필드를 선택사항(Optional)으로 풀어주거나 조건부 검사로 수정해야 합니다.
* **API 전송 데이터(Payload) 확인:** 브라우저 개발자 도구(F12)의 **Network(네트워크)** 탭에서 텍스트만 입력하고 등록을 눌렀을 때 서버로 전송되는 요청(Request) 데이터와 응답(Response) 에러 코드를 확인해 보세요. 
* **상태 보존(State Persistence):** 에러나 유효성 검사 실패 시 입력했던 텍스트와 상태가 날아가지 않고 유지되도록 폼 리셋 로직(`form.reset()` 등)의 실행 조건을 점검해야 합니다.
