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
LOGO_FILE = "logo.png"

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

DEFAULT_SCHEDULES = [
    {"month": "2026. 08 (Yr.26 AUG)", "field": "2026-08-21 (금)", "screen": "2026-08-08 (토)", "etc": ""},
    {"month": "2026. 09 (Yr.26 SEP)", "field": "2026-09-19 (토)", "screen": "2026-09-05 (토)", "etc": ""},
    {"month": "2026. 10 (Yr.26 OCT)", "field": "2026-10-23 (금)", "screen": "2026-10-17 (토)", "etc": ""},
    {"month": "2026. 11 (Yr.26 NOV)", "field": "2026-11-21 (토)", "screen": "2026-11-07 (토)", "etc": ""},
    {"month": "2026. 12 (Yr.26 DEC)", "field": "2026-12-05 (토)", "screen": "2026-12-19 (토)", "etc": "🎉 송년회 겸사 (12/5)"},
    {"month": "2027. 01 (Yr.27 JAN)", "field": "2027-01-15 (금)", "screen": "2027-01-09 (토)", "etc": ""},
    {"month": "2027. 02 (Yr.27 FEB)", "field": "2027-02-27 (토)", "screen": "2027-02-13 (토)", "etc": ""},
    {"month": "2027. 03 (Yr.27 MAR)", "field": "2027-03-19 (금)", "screen": "2027-03-06 (토)", "etc": ""},
    {"month": "2027. 04 (Yr.27 APR)", "field": "2027-04-17 (토)", "screen": "2027-04-03 (토)", "etc": ""},
    {"month": "2027. 05 (Yr.27 MAY)", "field": "2027-05-21 (금)", "screen": "2027-05-15 (토)", "etc": ""},
    {"month": "2027. 06 (Yr.27 JUN)", "field": "2027-06-19 (토)", "screen": "2027-06-05 (토)", "etc": ""},
    {"month": "2027. 07 (Yr.27 JUL)", "field": "2027-07-23 (금)", "screen": "2027-07-03 (토)", "etc": ""},
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
                            if "secret_friend" not in data["member_db"][m]:
                                data["member_db"][m]["secret_friend"] = "친구"
                            if "last_notice_seen" not in data["member_db"][m]:
                                data["member_db"][m]["last_notice_seen"] = ""
                            if "last_lounge_seen" not in data["member_db"][m]:
                                data["member_db"][m]["last_lounge_seen"] = ""
                    if "notices" not in data:
                        data["notices"] = []
                    if "annual_schedules" not in data:
                        data["annual_schedules"] = DEFAULT_SCHEDULES
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
            "secret_friend": "친구",
            "last_notice_seen": "",
            "last_lounge_seen": ""
        }
    pair_history = {m1: {m2: 0 for m2 in DEFAULT_MEMBERS} for m1 in DEFAULT_MEMBERS}
    feed_posts = [] 
    rounds_data = [] 
    match_logs = []
    notices = []
    annual_schedules = DEFAULT_SCHEDULES
    
    return {
        "total_events": 0,
        "member_db": member_db,
        "pair_history": pair_history,
        "feed_posts": feed_posts,
        "rounds_data": rounds_data,
        "match_logs": match_logs,
        "notices": notices,
        "annual_schedules": annual_schedules
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
annual_schedules = db.setdefault("annual_schedules", DEFAULT_SCHEDULES)

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
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden; display: none !important;}
    .stDeployButton {display: none !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    
    .stApp { background-color: #F8FAF8 !important; font-family: 'Noto Sans KR', sans-serif; color: #1E2923; font-size: 0.9rem; }
    
    h2 { font-size: 1.15rem !important; font-weight: 700 !important; color: #0F2E1B !important; margin-bottom: 0.5rem !important; }
    h3 { font-size: 1.05rem !important; font-weight: 700 !important; color: #0F2E1B !important; }
    
    .logo-card {
        background: linear-gradient(135deg, #0F2E1B 0%, #1B4D33 100%);
        border-radius: 16px;
        padding: 22px 15px;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(15,46,27,0.15);
        border: 1px solid rgba(212,180,117,0.3);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .logo-card img {
        max-width: 280px;
        width: 100%;
        height: auto;
        border-radius: 10px;
        filter: drop-shadow(0 4px 12px rgba(0,0,0,0.25));
    }
    
    .menu-card-box { 
        background-color: #FFFFFF; 
        border-radius: 12px; 
        border: 1px solid #E2E8F0; 
        padding: 16px 12px; 
        text-align: center; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.02); 
        transition: all 0.25s ease; 
        margin-bottom: 8px;
        height: 95px;
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
        font-size: 0.9rem; 
        font-weight: 700;
        margin-bottom: 4px; 
        color: #0F2E1B; 
        text-transform: uppercase;
    }
    .menu-card-box p { 
        color: #64748B; 
        font-size: 0.7rem; 
        margin: 0; 
        line-height: 1.2; 
    }
    
    .band-card { background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; max-width: 100%; margin: 0 auto 16px auto; box-shadow: 0 2px 6px rgba(0,0,0,0.03); overflow: hidden; }
    .band-header { display: flex; align-items: center; padding: 12px 14px; border-bottom: 1px solid #F1F5F9; background-color: #FAFAFA; }
    .band-body { padding: 14px; font-size: 0.88rem; color: #1E2923; line-height: 1.5; }
    
    .schedule-card { background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 14px 16px; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); border-left: 5px solid #1B4D33; }
    .schedule-card h4 { margin: 0 0 8px 0; color: #0F2E1B; font-family: 'Montserrat', sans-serif; font-size: 0.95rem; }
    
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

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None

logo_b64 = get_image_base64(LOGO_FILE)

# --- LOGIN & SIGNUP ---
if not st.session_state.get('logged_in_user'):
    if logo_b64:
        st.markdown(f"""
        <div style="text-align: center; padding: 25px 15px 15px 15px;">
            <img src="data:image/png;base64,{logo_b64}" style="max-width: 220px; width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 35px 15px 20px 15px;">
            <h1 style="font-family: 'Montserrat', sans-serif; color: #0F2E1B; margin: 0; font-size: 1.6rem; font-weight: 700;">SEGOK GOLF COMMUNITY</h1>
        </div>
        """, unsafe_allow_html=True)
    
    col_login, _ = st.columns([1, 0.01])
    with col_login:
        tab1, tab2, tab3 = st.tabs(["🔑 클럽 회원 로그인", "✨ 신입 회원 가입", "🔒 비밀번호 찾기"])
        
        with tab1:
            st.caption("초기 비밀번호는 '1234' 입니다.")
            approved_members = [k for k, v in member_db.items() if v.get("status", "approved") == "approved"]
            login_name = st.selectbox("회원 성함 선택", ["선택하세요"] + approved_members, key="login_select_name")
            login_pw = st.text_input("비밀번호 입력", type="password", key="login_input_pw")
            
            if st.button("로그인", type="primary", use_container_width=True, key="login_submit_btn"):
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
            new_name = st.text_input("회원 성함", key="signup_name")
            new_nick = st.text_input("클럽 닉네임 (선택)", key="signup_nick")
            new_pw = st.text_input("비밀번호 설정", type="password", key="signup_pw")
            new_friend = st.text_input("보안 질문: 어렸을 적 가장 친한 친구 이름", placeholder="비밀번호 찾기 시 사용됩니다", key="signup_friend")
            
            if st.button("가입 신청서 제출", use_container_width=True, key="signup_submit"):
                if new_name and new_pw and new_friend:
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
                            "secret_friend": new_friend.strip(),
                            "last_notice_seen": "",
                            "last_lounge_seen": ""
                        }
                        pair_history[new_name] = {m: 0 for m in member_db.keys()}
                        for m in member_db.keys():
                            pair_history[m][new_name] = 0
                            
                        save_data(db)
                        st.success("등록되었습니다!")
                else:
                    st.warning("성함, 비밀번호, 보안 질문(친구 이름)을 모두 입력해 주세요.")

        with tab3:
            st.caption("등록된 보안 질문('가장 친한 친구 이름')을 확인하여 비밀번호를 새로 설정합니다.")
            find_name = st.selectbox("회원 성함 선택", ["선택하세요"] + list(member_db.keys()), key="find_pw_name")
            find_friend = st.text_input("보안 질문: 어렸을 적 가장 친한 친구 이름", key="find_pw_friend")
            new_reset_pw = st.text_input("새로 사용할 비밀번호 설정", type="password", key="find_pw_new")

            if st.button("비밀번호 재설정", use_container_width=True, key="find_pw_submit"):
                if find_name in member_db and find_friend and new_reset_pw:
                    stored_friend = member_db[find_name].get("secret_friend", "친구")
                    if find_friend.strip() == stored_friend:
                        member_db[find_name]["password"] = new_reset_pw
                        save_data(db)
                        st.success("등록되었습니다! 새 비밀번호로 로그인해 주세요.")
                    else:
                        st.error("보안 질문 정답이 일치하지 않습니다.")
                else:
                    st.warning("모든 항목을 올바르게 입력해 주세요.")
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
    if logo_b64:
        st.markdown(f"""
        <div class="logo-card">
            <img src="data:image/png;base64,{logo_b64}">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="logo-card">
            <h1 style="color: #FFFFFF; font-size: 1.6rem; text-align: center; margin: 0;">SEGOK GOLF COMMUNITY</h1>
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
            <p>자유 소통 및 파일 공유</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("클럽 라운지 입장", use_container_width=True, key="go_lounge"):
            set_menu("클럽 라운지")
            st.rerun()

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="menu-card-box">
            <h3>📅 SCHEDULE</h3>
            <p>세곡 골프클럽 연간 일정 및 규정</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("연간 일정 입장", use_container_width=True, key="go_schedule"):
            set_menu("연간 일정")
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
    
    menu_list = ["메인 홈", notice_label, lounge_label, "📅 연간 일정 (SCHEDULE)", "🏆 경기 결과 및 랭킹 (RESULTS)", "👑 명예의 전당 (HALL OF FAME)", "📁 조편성 아카이브 (ARCHIVE)", "👤 마이페이지 (MY PAGE)"]
    if is_admin:
        menu_list.insert(3, "⛳ 티타임 조편성 (MATCH)")
        menu_list.append("👥 회원 리스트 (MEMBERS)")
        
    current_label_map = {
        "HOME": "메인 홈",
        "클럽 공지사항": notice_label,
        "클럽 라운지": lounge_label,
        "연간 일정": "📅 연간 일정 (SCHEDULE)",
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
        elif "연간 일정" in selected_nav: target_menu = "연간 일정"
        
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
        my_posts = [p for p in feed_posts if p.get("author") == current_user]
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

    # 2. 📅 연간 일정 (SCHEDULE)
    elif menu == "연간 일정":
        st.subheader("📅 ANNUAL SCHEDULE (세곡 골프 클럽 연간 일정)")
        st.caption("시즌 Yr.26-27 (2026. 8. 1 ~ 2027. 7. 31) 주요 클럽 월례회 및 행사 일정")

        if is_admin:
            with st.expander("✍️ [OPERATOR] 연간 일정 추가 및 관리"):
                with st.form("add_schedule_form"):
                    st.markdown("##### ➕ 새로운 월별 일정 추가")
                    new_month = st.text_input("월/시즌 명칭", placeholder="예: 2026. 08 (Yr.26 AUG)")
                    new_field = st.text_input("필드 월례회 일정", placeholder="예: 2026-08-21 (금)")
                    new_screen = st.text_input("스크린 월례회 일정", placeholder="예: 2026-08-08 (토)")
                    new_etc = st.text_input("기타 메모 (선택)", placeholder="예: 🎉 송년회 겸사 (12/5)")
                    
                    add_sch_btn = st.form_submit_button("일정 추가하기", use_container_width=True)
                    if add_sch_btn:
                        if new_month:
                            annual_schedules.append({
                                "month": new_month,
                                "field": new_field if new_field else "-",
                                "screen": new_screen if new_screen else "-",
                                "etc": new_etc if new_etc else ""
                            })
                            save_data(db)
                            st.success("등록되었습니다!")
                            st.rerun()
                        else:
                            st.warning("월/시즌 명칭을 입력해 주세요.")

        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

        for s_idx, s in enumerate(annual_schedules):
            etc_badge = f"<span style='background:#FEF3C7; color:#92400E; padding:2px 8px; border-radius:6px; font-size:0.75rem; font-weight:700; margin-left:8px;'>{s['etc']}</span>" if s.get('etc') else ""
            
            st.markdown(f"""
            <div class="schedule-card">
                <h4 style="margin-bottom: 6px;">🗓️ {s['month']} {etc_badge}</h4>
                <div style="font-size: 0.88rem; color: #334155; line-height: 1.6;">
                    <div>⛳ <b>필드 월례회:</b> <span style="color: #1B4D33; font-weight: 600;">{s['field']}</span></div>
                    <div>🖥️ <b>스크린 월례회:</b> <span style="color: #2563EB; font-weight: 600;">{s['screen']}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if is_admin:
                with st.expander(f"✏️ [{s['month']}] 일정 수정/삭제"):
                    with st.form(f"edit_sch_form_{s_idx}"):
                        e_month = st.text_input("월/시즌 명칭", value=s['month'], key=f"e_m_{s_idx}")
                        e_field = st.text_input("필드 월례회 일정", value=s['field'], key=f"e_f_{s_idx}")
                        e_screen = st.text_input("스크린 월례회 일정", value=s['screen'], key=f"e_s_{s_idx}")
                        e_etc = st.text_input("기타 메모", value=s.get('etc', ''), key=f"e_e_{s_idx}")
                        
                        col_se1, col_se2 = st.columns(2)
                        with col_se1:
                            save_sch = st.form_submit_button("💾 수정 저장", use_container_width=True)
                        with col_se2:
                            del_sch = st.form_submit_button("🗑️ 일정 삭제", use_container_width=True)

                        if save_sch:
                            annual_schedules[s_idx] = {
                                "month": e_month,
                                "field": e_field,
                                "screen": e_screen,
                                "etc": e_etc
                            }
                            save_data(db)
                            st.success("수정되었습니다!")
                            st.rerun()
                        
                        if del_sch:
                            annual_schedules.pop(s_idx)
                            save_data(db)
                            st.success("수정되었습니다!")
                            st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("##### 📌 클럽 운영 및 참석 규정 노트")
        st.markdown("""
        <div style="background-color: #F8FAFC; border-left: 4px solid #1B4D33; padding: 14px 18px; border-radius: 8px; font-size: 0.85rem; color: #1E2923; line-height: 1.6;">
            • <b>필드 월례회:</b> 금요일과 토요일 격월로 번갈아 매월 3주 차에 진행합니다. (12월 제외)<br>
            • <b>스크린 월례회:</b> 매월 1주 차 토요일에 진행하며, 연휴 및 주요 행사(어버이날 등) 시 조정될 수 있습니다.<br>
            • <b>자율 모임:</b> 월례회 외의 사적인 라운드는 정기 횟수로 집계하지 않습니다.<br>
            • <b>참석 규정:</b> 특별한 사유(질병, 장기출장, 이주 등) 없이 3개월 이상 월례회 불참 시 운영진 회의를 통해 제명 처리될 수 있습니다.<br>
            • <b>동절기 운영 (11~3월):</b> 기상 악화 시 회원 투표를 거쳐 필드 월례회가 취소될 수 있습니다.<br>
            • <b>12월 송년 필드 월례회:</b> 12월 5일(토) 진행하며, 악천후 시 투표를 통해 스크린으로 대체됩니다.<br>
            • <b>모임 참석 권장:</b> 월례회가 있는 주는 월례회 참석을 우선하여 참석해 주시길 부탁드리며, 그 외 자율 모임은 적극 권장합니다.
        </div>
        """, unsafe_allow_html=True)

    # 3. 📢 클럽 공지사항
    elif menu == "클럽 공지사항":
        if notices:
            user_info["last_notice_seen"] = notices[0]["date"]
            save_data(db)
            
        st.subheader("📢 NOTICE (클럽 공지사항)")
        st.caption("세곡 골프클럽의 주요 소식과 안내 사항을 확인하세요.")
        
        if is_admin:
            with st.expander("✍️ [OPERATOR] 새 공지사항 등록하기 (사진/파일/투표 첨부)"):
                n_title = st.text_input("공지 제목", key="notice_title_input")
                n_content = st.text_area("공지 내용", key="notice_content_input")
                
                col_n_u1, col_n_u2 = st.columns(2)
                with col_n_u1:
                    n_uploaded_file = st.file_uploader("이미지 첨부 (선택)", type=["jpg", "png", "jpeg"], key="notice_img_up")
                with col_n_u2:
                    n_doc_file = st.file_uploader("문서/엑셀 파일 첨부 (선택)", type=["xlsx", "xls", "pdf", "txt", "csv"], key="notice_doc_up")
                
                n_use_poll = st.checkbox("📊 투표 생성하기", key="notice_use_poll")
                n_poll_question = ""
                n_poll_options = []
                n_poll_deadline = None
                n_allow_multiple = False
                n_is_anonymous = False
                
                if n_use_poll:
                    n_poll_question = st.text_input("투표 주제", placeholder="예: 8월 정기 라운딩 참석 투표", key="notice_poll_q")
                    n_allow_multiple = st.checkbox("복수 선택 허용 (최대 3개까지 선택 가능)", key="notice_poll_multi")
                    n_is_anonymous = st.checkbox("익명 투표", key="notice_poll_anon")
                    
                    st.markdown("##### ⏳ 투표 마감 기한 (데드라인) 설정")
                    col_nd1, col_nd2 = st.columns(2)
                    with col_nd1:
                        nd_date = st.date_input("마감 날짜", value=datetime.now().date(), key="notice_poll_date")
                    with col_nd2:
                        nd_time = st.time_input("마감 시간", value=time(23, 59), key="notice_poll_time")
                    n_poll_deadline = datetime.combine(nd_date, nd_time).strftime("%Y-%m-%d %H:%M")

                    if 'notice_poll_option_count' not in st.session_state:
                        st.session_state.notice_poll_option_count = 3
                    
                    if st.button("➕ 투표 항목 추가", key="notice_add_opt_btn"):
                        st.session_state.notice_poll_option_count += 1
                        st.rerun()
                    
                    st.caption("💡 원하시는 투표 선택 항목을 직접 입력하세요 (예: 1. 참석, 2. 불참, 3. 미정 등)")
                    for i in range(st.session_state.notice_poll_option_count):
                        opt_val = st.text_input(f"투표 항목 {i+1}", key=f"notice_poll_opt_input_{i}", placeholder=f"예: {i+1}. 항목 입력")
                        if opt_val:
                            n_poll_options.append(opt_val.strip())

                if st.button("공지 발행", type="primary", use_container_width=True, key="notice_submit_btn"):
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

                        n_poll_data = None
                        if n_use_poll and n_poll_question and len(n_poll_options) >= 2:
                            n_poll_data = {
                                "question": n_poll_question,
                                "deadline": n_poll_deadline,
                                "allow_multiple": n_allow_multiple,
                                "is_anonymous": n_is_anonymous,
                                "options": {opt: [] for opt in n_poll_options}
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
                        st.session_state.notice_poll_option_count = 3
                        save_data(db)
                        st.success("등록되었습니다!")
                        st.rerun()
                    else:
                        st.warning("제목과 내용을 모두 입력해 주세요 (투표 사용 시 주제와 최소 2개 이상의 항목 필수).")
                        
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
                    now_str_val = datetime.now().strftime("%Y-%m-%d %H:%M")
                    is_closed = deadline_str and (now_str_val > deadline_str)
                    allow_multi = n_poll.get("allow_multiple", False)
                    is_anon = n_poll.get("is_anonymous", False)

                    header_title = "🏁 [투표 최종 결과]" if is_closed else "📊 [투표]"
                    st.markdown(f"**{header_title} {n_poll['question']}**")
                    
                    if deadline_str:
                        st.caption(f"⏰ 마감 기한: {deadline_str}까지 {'(투표 마감됨 🔒)' if is_closed else ''}")
                    
                    mode_txt = "익명 투표" if is_anon else "실명 투표"
                    multi_txt = "복수 선택(최대 3개)" if allow_multi else "단일 선택"
                    st.caption(f"ℹ️ {mode_txt} | {multi_txt}")

                    my_voted_options = [opt for opt, voters in n_poll["options"].items() if current_user in voters]

                    for opt, voters in n_poll["options"].items():
                        voted_here = current_user in voters
                        btn_label = f"✓ {opt} ({len(voters)}표)" if voted_here else f"{opt} ({len(voters)}표)"
                        
                        if is_closed:
                            st.button(btn_label, key=f"notice_poll_closed_{notice['id']}_{opt}", disabled=True, use_container_width=True)
                        else:
                            if st.button(btn_label, key=f"notice_poll_{notice['id']}_{opt}", use_container_width=True):
                                if voted_here:
                                    voters.remove(current_user)
                                    save_data(db)
                                    st.rerun()
                                else:
                                    if not allow_multi:
                                        for o_key, o_list in n_poll["options"].items():
                                            if current_user in o_list:
                                                o_list.remove(current_user)
                                        voters.append(current_user)
                                    else:
                                        if len(my_voted_options) >= 3:
                                            st.warning("⚠️ 최대 3개까지만 선택할 수 있습니다!")
                                        else:
                                            voters.append(current_user)
                                    save_data(db)
                                    st.rerun()

                        if not is_anon and voters:
                            voter_names = [member_db.get(u, {}).get("nickname", u) for u in voters]
                            st.caption(f"ㄴ 투표자: {', '.join(voter_names)}")
                    
                    total_voters = len(set([user for v_list in n_poll["options"].values() for user in v_list]))
                    st.caption(f"총 참여 인원: {total_voters}명")

                st.markdown("</div>", unsafe_allow_html=True)

                if is_admin:
                    col_n_edit, col_n_del = st.columns(2)
                    with col_n_edit:
                        with st.expander("✏️ 공지 수정"):
                            edit_n_title = st.text_input("제목 수정", value=notice['title'], key=f"edit_n_title_{notice['id']}")
                            edit_n_content = st.text_area("내용 수정", value=notice['content'], key=f"edit_n_content_{notice['id']}")
                            
                            st.markdown("##### 🖼️ 이미지 변경/삭제")
                            cur_n_img = notice.get("media_path")
                            rm_n_img = False
                            if cur_n_img and os.path.exists(cur_n_img):
                                st.image(cur_n_img, width=150, caption="현재 이미지")
                                rm_n_img = st.checkbox("기존 이미지 삭제", key=f"edit_rm_n_img_{notice['id']}")
                            new_n_img_up = st.file_uploader("새 이미지 교체", type=["jpg", "png", "jpeg"], key=f"edit_new_n_img_{notice['id']}")

                            st.markdown("##### 📎 첨부파일 변경/삭제")
                            cur_n_file = notice.get("file_name")
                            rm_n_file = False
                            if cur_n_file:
                                st.write(f"현재 파일: {cur_n_file}")
                                rm_n_file = st.checkbox("기존 파일 삭제", key=f"edit_rm_n_file_{notice['id']}")
                            new_n_file_up = st.file_uploader("새 파일 교체", type=["xlsx", "xls", "pdf", "txt", "csv"], key=f"edit_new_n_file_{notice['id']}")

                            if st.button("수정 저장", key=f"btn_save_notice_{notice['id']}", use_container_width=True):
                                notice['title'] = edit_n_title
                                notice['content'] = edit_n_content

                                if rm_n_img:
                                    if notice.get("media_path") and os.path.exists(notice["media_path"]):
                                        try: os.remove(notice["media_path"])
                                        except: pass
                                    notice["media_path"] = None
                                    notice["media_type"] = None
                                if new_n_img_up is not None:
                                    if notice.get("media_path") and os.path.exists(notice["media_path"]):
                                        try: os.remove(notice["media_path"])
                                        except: pass
                                    fname = f"{int(datetime.now().timestamp())}_{new_n_img_up.name}"
                                    m_path = os.path.join(UPLOAD_DIR, fname)
                                    with open(m_path, "wb") as f:
                                        f.write(new_n_img_up.getbuffer())
                                    notice["media_path"] = m_path
                                    notice["media_type"] = "image"

                                if rm_n_file:
                                    if notice.get("file_path") and os.path.exists(notice["file_path"]):
                                        try: os.remove(notice["file_path"])
                                        except: pass
                                    notice["file_path"] = None
                                    notice["file_name"] = None
                                if new_n_file_up is not None:
                                    if notice.get("file_path") and os.path.exists(notice["file_path"]):
                                        try: os.remove(notice["file_path"])
                                        except: pass
                                    f_name = new_n_file_up.name
                                    f_path = os.path.join(UPLOAD_DIR, f"notice_doc_{int(datetime.now().timestamp())}_{f_name}")
                                    with open(f_path, "wb") as f:
                                        f.write(new_n_file_up.getbuffer())
                                    notice["file_path"] = f_path
                                    notice["file_name"] = f_name

                                save_data(db)
                                st.success("수정되었습니다!")
                                st.rerun()
                    with col_n_del:
                        with st.expander("🗑️ 공지 삭제"):
                            confirm_del = st.checkbox("정말로 이 공지사항을 삭제하시겠습니까?", key=f"conf_notice_{notice['id']}")
                            if confirm_del:
                                if st.button("⚠️ 최종 삭제 실행", key=f"del_notice_{notice['id']}", type="primary", use_container_width=True):
                                    notices.pop(n_idx)
                                    save_data(db)
                                    st.success("수정되었습니다!")
                                    st.rerun()

    # 4. 💬 클럽 라운지
    elif menu == "클럽 라운지":
        if feed_posts:
            user_info["last_lounge_seen"] = feed_posts[0]["date"]
            save_data(db)
            
        st.subheader("💬 CLUB LOUNGE (클럽 라운지)")
        
        with st.expander("✍️ 새 글 작성하기", expanded=True):
            l_content = st.text_area("내용 입력", placeholder="라운딩 후기, 소식 등을 자유롭게 남겨보세요...", key="new_lounge_content")
            
            col_lu1, col_lu2 = st.columns(2)
            with col_lu1:
                l_img = st.file_uploader("이미지 첨부 (선택)", type=["jpg", "png", "jpeg"], key="new_lounge_img")
            with col_lu2:
                l_doc = st.file_uploader("문서 파일 첨부 (선택)", type=["xlsx", "xls", "pdf", "txt", "csv"], key="new_lounge_doc")

            if st.button("게시물 등록", type="primary", use_container_width=True, key="new_lounge_btn"):
                if (l_content and l_content.strip() != "") or l_img is not None or l_doc is not None:
                    l_img_path = None
                    l_img_type = None
                    if l_img is not None:
                        img_fname = f"lounge_img_{int(datetime.now().timestamp())}_{l_img.name}"
                        l_img_path = os.path.join(UPLOAD_DIR, img_fname)
                        with open(l_img_path, "wb") as f:
                            f.write(l_img.getbuffer())
                        l_img_type = "image"
                    
                    l_doc_path = None
                    l_doc_name = None
                    if l_doc is not None:
                        l_doc_name = l_doc.name
                        l_doc_path = os.path.join(UPLOAD_DIR, f"lounge_doc_{int(datetime.now().timestamp())}_{l_doc_name}")
                        with open(l_doc_path, "wb") as f:
                            f.write(l_doc.getbuffer())

                    feed_posts.insert(0, {
                        "id": int(datetime.now().timestamp()),
                        "author": current_user,
                        "nickname": user_info.get("nickname", current_user),
                        "profile_img": user_info.get("profile_img", None),
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "content": l_content if l_content else "",
                        "media_path": l_img_path,
                        "media_type": l_img_type,
                        "file_path": l_doc_path,
                        "file_name": l_doc_name,
                        "poll": None,
                        "likes": 0,
                        "liked_users": [],
                        "comments": []
                    })
                    save_data(db)
                    st.success("등록되었습니다!")
                    st.rerun()
                else:
                    st.warning("내용, 이미지 또는 파일 중 하나 이상을 입력해 주세요.")

        st.markdown("---")

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
                            <strong style="color:#1E2923; font-size:0.9rem;">{p_nickname}</strong><br>
                            <span style="color:#64748B; font-size:0.7rem;">{post['date']}</span>
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
                        <p style="margin:0; color:#1E2923; word-break:break-all; white-space: pre-wrap; user-select: text;">{post['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
                    
                c_lk, c_edit, c_del = st.columns([1, 1, 1])
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

                if post['author'] == current_user:
                    with c_edit:
                        with st.expander("✏️ 글 수정"):
                            edit_post_text = st.text_area("내용 수정", value=post['content'], key=f"edit_post_txt_{post['id']}")
                            
                            st.markdown("##### 🖼️ 이미지 변경/삭제")
                            cur_img = post.get("media_path")
                            rm_img = False
                            if cur_img and os.path.exists(cur_img):
                                st.image(cur_img, width=150, caption="현재 이미지")
                                rm_img = st.checkbox("기존 이미지 삭제", key=f"edit_rm_img_{post['id']}")
                            new_img_up = st.file_uploader("새 이미지 교체", type=["jpg", "png", "jpeg"], key=f"edit_new_img_{post['id']}")

                            st.markdown("##### 📎 첨부파일 변경/삭제")
                            cur_file = post.get("file_name")
                            rm_file = False
                            if cur_file:
                                st.write(f"현재 파일: {cur_file}")
                                rm_file = st.checkbox("기존 파일 삭제", key=f"edit_rm_file_{post['id']}")
                            new_file_up = st.file_uploader("새 파일 교체", type=["xlsx", "xls", "pdf", "txt", "csv"], key=f"edit_new_file_{post['id']}")

                            if st.button("수정 저장", key=f"btn_save_post_{post['id']}", use_container_width=True):
                                post['content'] = edit_post_text if edit_post_text else ""
                                
                                if rm_img:
                                    if post.get("media_path") and os.path.exists(post["media_path"]):
                                        try: os.remove(post["media_path"])
                                        except: pass
                                    post["media_path"] = None
                                    post["media_type"] = None
                                if new_img_up is not None:
                                    if post.get("media_path") and os.path.exists(post["media_path"]):
                                        try: os.remove(post["media_path"])
                                        except: pass
                                    fname = f"{int(datetime.now().timestamp())}_{new_img_up.name}"
                                    m_path = os.path.join(UPLOAD_DIR, fname)
                                    with open(m_path, "wb") as f:
                                        f.write(new_img_up.getbuffer())
                                    post["media_path"] = m_path
                                    post["media_type"] = "image"

                                if rm_file:
                                    if post.get("file_path") and os.path.exists(post["file_path"]):
                                        try: os.remove(post["file_path"])
                                        except: pass
                                    post["file_path"] = None
                                    post["file_name"] = None
                                if new_file_up is not None:
                                    if post.get("file_path") and os.path.exists(post["file_path"]):
                                        try: os.remove(post["file_path"])
                                        except: pass
                                    f_name = new_file_up.name
                                    f_path = os.path.join(UPLOAD_DIR, f"lounge_doc_{int(datetime.now().timestamp())}_{f_name}")
                                    with open(f_path, "wb") as f:
                                        f.write(new_file_up.getbuffer())
                                    post["file_path"] = f_path
                                    post["file_name"] = f_name

                                save_data(db)
                                st.success("수정되었습니다!")
                                st.rerun()
                        
                if post['author'] == current_user or is_admin:
                    with c_del:
                        with st.expander("🗑️ 삭제"):
                            conf_post = st.checkbox("정말로 삭제하시겠습니까?", key=f"conf_post_{post['id']}")
                            if conf_post:
                                if st.button("⚠️ 삭제 실행", key=f"btn_del_post_{post['id']}", type="primary", use_container_width=True):
                                    feed_posts.pop(idx)
                                    save_data(db)
                                    st.success("수정되었습니다!")
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
                        st.success("등록되었습니다!")
                        st.rerun()

    # 5. ⛳ 티타임 조편성
    elif menu == "티타임 조편성":
        st.subheader("⛳ TEE-OFF MATCH (티타임 조편성)")
        if not is_admin:
            st.error("⛔ 조편성 기능은 운영진 전용 메뉴입니다.")
        else:
            st.success("👑 **운영자 권한 완료** | 부부 동반 옵션, 직전 라운드 제외, 1~3지망 희망 멤버, 성비 맞춤 조건으로 최적화합니다.")
            
            st.markdown("##### 📌 기본 라운드 정보 입력")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                r_date_input = st.date_input("라운드 일정 (날짜)")
            with col_t2:
                golf_location = st.text_input("골프장 장소", placeholder="예: 남서울CC")

            st.markdown("##### ⚙️ 고급 조편성 옵션 설정")
            col_op1, col_op2 = st.columns(2)
            with col_op1:
                couple_rule = st.radio("부부 동반 옵션", ["부부 분리 (같은 조 배치 안함)", "부부 라운딩 무관"])
                exclude_recent = st.checkbox("직전 라운드 동반자 제외 최적화", value=True)
            with col_op2:
                gender_rule = st.radio("성별 맞춤 옵션", ["기본 (핸디캡 균등)", "동성 위주 배치", "성비 맞춤 위주 (남녀 균등)"])

            approved_members = [k for k, v in member_db.items() if v.get("status", "approved") == "approved"]
            default_selected = approved_members[:16] if len(approved_members) >= 16 else approved_members
            selected_attendees = st.multiselect("오늘 참석자 선택", approved_members, default=default_selected)

            with st.expander("💌 회원별 동반 희망 멤버 (1, 2, 3지망) 설정"):
                if 'match_preferences' not in st.session_state:
                    st.session_state.match_preferences = {}
                
                pref_member = st.selectbox("희망 멤버를 설정할 회원 선택", ["선택하세요"] + selected_attendees, key="pref_mem_select")
                if pref_member != "선택하세요":
                    current_prefs = st.session_state.match_preferences.get(pref_member, ["", "", ""])
                    p1 = st.selectbox("1지망 희망 멤버", ["선택 안 함"] + [m for m in selected_attendees if m != pref_member], 
                                      index=([ "선택 안 함" ] + [m for m in selected_attendees if m != pref_member]).index(current_prefs[0]) if current_prefs[0] in selected_attendees else 0, key=f"pref_1_{pref_member}")
                    p2 = st.selectbox("2지망 희망 멤버", ["선택 안 함"] + [m for m in selected_attendees if m != pref_member], 
                                      index=([ "선택 안 함" ] + [m for m in selected_attendees if m != pref_member]).index(current_prefs[1]) if current_prefs[1] in selected_attendees else 0, key=f"pref_2_{pref_member}")
                    p3 = st.selectbox("3지망 희망 멤버", ["선택 안 함"] + [m for m in selected_attendees if m != pref_member], 
                                      index=([ "선택 안 함" ] + [m for m in selected_attendees if m != pref_member]).index(current_prefs[2]) if current_prefs[2] in selected_attendees else 0, key=f"pref_3_{pref_member}")
                    
                    if st.button("지망 사항 저장", key=f"save_pref_{pref_member}"):
                        val1 = "" if p1 == "선택 안 함" else p1
                        val2 = "" if p2 == "선택 안 함" else p2
                        val3 = "" if p3 == "선택 안 함" else p3
                        st.session_state.match_preferences[pref_member] = [val1, val2, val3]
                        st.success("수정되었습니다!")

            def generate_teams_smart_advanced(attendees, pair_hist, mem_db, couple_rule, exclude_recent, gender_rule, preferences, team_sz=4, iterations=1500):
                if not attendees:
                    return []
                
                couple_map = {}
                for m1, m2 in COUPLES_LIST:
                    if m1 in attendees and m2 in attendees:
                        couple_map[m1] = m2
                        couple_map[m2] = m1

                recent_pairs = set()
                if exclude_recent and rounds_data:
                    for r in rounds_data:
                        if r.get("teams"):
                            for t in r["teams"]:
                                for i in range(len(t)):
                                    for j in range(i+1, len(t)):
                                        recent_pairs.add(tuple(sorted([t[i], t[j]])))
                            break

                best_teams = []
                min_score = float('inf')

                for _ in range(iterations):
                    shuffled = attendees.copy()
                    random.shuffle(shuffled)
                    teams = [shuffled[i:i + team_sz] for i in range(0, len(shuffled), team_sz)]
                    
                    score = 0
                    
                    for t in teams:
                        if "분리" in couple_rule:
                            for i in range(len(t)):
                                for j in range(i+1, len(t)):
                                    if couple_map.get(t[i]) == t[j]:
                                        score += 150000
                        
                        if exclude_recent:
                            for i in range(len(t)):
                                for j in range(i+1, len(t)):
                                    if tuple(sorted([t[i], t[j]])) in recent_pairs:
                                        score += 2000

                        females_in_team = sum(1 for m in t if m in FEMALE_SET)
                        males_in_team = len(t) - females_in_team
                        if "동성" in gender_rule:
                            if females_in_team > 0 and males_in_team > 0:
                                score += 3000 * min(females_in_team, males_in_team)
                        elif "성비" in gender_rule:
                            ideal_f = team_sz / 2
                            score += abs(females_in_team - ideal_f) * 1500

                        for i in range(len(t)):
                            for j in range(i+1, len(t)):
                                score += (pair_hist.get(t[i], {}).get(t[j], 0) ** 2) * 10

                    pref_weights = [100000, 50000, 25000]
                    for u, choices in preferences.items():
                        if u in attendees:
                            u_team = next((t for t in teams if u in t), [])
                            for rank, target in enumerate(choices):
                                if target and target in attendees:
                                    if target not in u_team:
                                        score += pref_weights[rank]

                    if score < min_score:
                        min_score = score
                        best_teams = teams
                
                return best_teams

            if st.button("🎲 고급 조건 맞춤 조편성 실행하기", type="primary", use_container_width=True):
                user_prefs = st.session_state.get('match_preferences', {})
                teams = generate_teams_smart_advanced(selected_attendees, pair_history, member_db, couple_rule, exclude_recent, gender_rule, user_prefs)
                st.session_state.generated_teams = teams
                st.success("등록되었습니다!")

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
                        st.success("수정되었습니다!")
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
                                    
                    round_title_str = f"{r_date_input.month}월 정기 필드 월례회 ({golf_location or '필드'})"
                    round_entry = {
                        "id": int(datetime.now().timestamp()),
                        "title": round_title_str,
                        "date": date_str,
                        "location": golf_location or "필드",
                        "tee_times": group_tee_times,
                        "courses": group_courses,
                        "type": "필드 월례회",
                        "teams": teams,
                        "scores": {},
                        "completed": False,
                        "awards": {"medalist": "-", "longist": "-", "nearest": "-"}
                    }
                    rounds_data.insert(0, round_entry)
                    
                    match_logs.insert(0, {
                        "id": len(match_logs) + 1,
                        "date": date_str,
                        "location": golf_location or "필드",
                        "title": round_title_str,
                        "tee_times": group_tee_times,
                        "courses": group_courses,
                        "event_type": "필드 월례회",
                        "teams": teams
                    })
                    
                    save_data(db)
                    st.success("등록되었습니다!")

    # 6. 🏆 경기 결과 및 랭킹
    elif menu == "경기 결과 및 랭킹":
        st.subheader("🏆 RESULTS & RANKING (경기 결과 및 랭킹)")
        
        field_rounds = [r for r in rounds_data if "필드" in r.get("type", "")]
        
        all_years = sorted(list(set([r['date'][:4] for r in field_rounds if 'date' in r and len(r['date']) >= 4])), reverse=True)
        current_year_str = str(datetime.now().year)
        if current_year_str not in all_years:
            all_years.insert(0, current_year_str)
            
        selected_year = st.selectbox("📅 조회 연도 선택", all_years, index=0 if current_year_str in all_years else 0)
        
        year_field_rounds = [r for r in field_rounds if r.get('date', '').startswith(selected_year)]
        
        if not year_field_rounds:
            st.info(f"{selected_year}년도에 등록된 필드 경기 결과가 없습니다.")
        else:
            selected_round_title = st.selectbox(
                "조회할 라운드 선택", 
                [f"{r['date']} | {r['title']} ({'입력 완료' if r.get('completed') else '입력 대기'})" for r in year_field_rounds]
            )
            selected_r_idx = [f"{r['date']} | {r['title']} ({'입력 완료' if r.get('completed') else '입력 대기'})" for r in year_field_rounds].index(selected_round_title)
            r = year_field_rounds[selected_r_idx]
            
            is_done = r.get("completed", False)
            status_tag = "✅ 성적 입력 완료" if is_done else "⌛ 성적 입력 대기 중"
            
            st.markdown(f"""
            <div class="css-card" style="margin-top: 15px;">
                <h3 style="color:#0F2E1B; margin-top:0; font-size:1.1rem;">🚩 {r['date']} | {r['title']} [{status_tag}]</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if is_done:
                st.markdown(f"""
                <div class="css-card">
                    <h4 style="color:#92400E; margin-bottom:8px; font-size:1rem;">🏆 공식 시상 내역</h4>
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
                        approved_members = [k for k, v in member_db.items() if v.get("status", "approved") == "approved"]
                        sel_mems = st.multiselect("참석 회원 선택", approved_members, default=list(r.get("scores", {}).keys()), key=f"melsel_{r['id']}")
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
                                "raw_nearest_dist": nearest[1]['near'] if longist else 999
                            }
                            recalculate_all_stats(db)
                            save_data(db)
                            st.success("등록되었습니다!")
                            st.rerun()

                with st.expander("🗑️ 라운드 삭제 관리"):
                    conf_rnd = st.checkbox("정말로 이 라운드 기록을 삭제하시겠습니까?", key=f"conf_rnd_{r['id']}")
                    if conf_rnd:
                        if st.button(f"⚠️ 최종 라운드 삭제 실행", key=f"btn_del_rnd_{r['id']}", type="primary", use_container_width=True):
                            rounds_data.remove(r)
                            recalculate_all_stats(db)
                            save_data(db)
                            st.success("수정되었습니다!")
                            st.rerun()

        # --- 누적 통계 & 랭킹 ---
        st.divider()
        st.subheader(f"📊 {selected_year}년도 누적 통계 및 랭킹")
        
        completed_r_year = [r for r in year_field_rounds if r.get("completed")]
        
        if not completed_r_year:
            st.warning(f"{selected_year}년도에 완료된 필드 라운드가 없습니다.")
        else:
            medalist_records = []
            longist_records = []
            nearest_records = []
            attendance_counts = {}

            for r in completed_r_year:
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

    # 7. 👑 명예의 전당
    elif menu == "명예의 전당":
        st.subheader("👑 HALL OF FAME (명예의 전당)")
        st.caption("클럽 회원들의 연도별 라운딩 스코어 이력, 평균 타수 및 출석 현황을 확인합니다.")
        
        field_rounds_all = [r for r in rounds_data if "필드" in r.get("type", "")]
        all_hof_years = sorted(list(set([r['date'][:4] for r in field_rounds_all if 'date' in r and len(r['date']) >= 4])), reverse=True)
        current_year_str = str(datetime.now().year)
        if current_year_str not in all_hof_years:
            all_hof_years.insert(0, current_year_str)
            
        selected_hof_year = st.selectbox("📅 조회 연도 선택", all_hof_years, index=0 if current_year_str in all_hof_years else 0, key="hof_year_select")
        
        approved_members = [k for k, v in member_db.items() if v.get("status", "approved") == "approved"]
        selected_member_name = st.selectbox("🔍 조회할 회원 선택", approved_members)
        
        if selected_member_name:
            m_info = member_db.get(selected_member_name, {})
            m_nick = m_info.get("nickname", selected_member_name)
            
            year_completed_rounds = [r for r in field_rounds_all if r.get('date', '').startswith(selected_hof_year) and r.get("completed")]
            total_year_rounds_cnt = len(year_completed_rounds)
            
            year_scores = []
            year_attended_cnt = 0
            for r in year_completed_rounds:
                scores_dict = r.get("scores", {})
                if selected_member_name in scores_dict:
                    year_attended_cnt += 1
                    year_scores.append(scores_dict[selected_member_name]["score"])
                    
            year_avg_sc = round(sum(year_scores) / len(year_scores), 1) if year_scores else 0
            year_att_rate = round((year_attended_cnt / total_year_rounds_cnt) * 100) if total_year_rounds_cnt > 0 else 0
            year_hc = round(year_avg_sc - 72) if year_scores else 0

            st.markdown(f"""
            <div class="css-card" style="background: linear-gradient(135deg, #0F2E1B 0%, #1B4D33 100%); color: #FFFFFF; padding: 18px; border-radius: 12px; border: 1px solid #D4B475;">
                <h3 style="margin:0 0 8px 0; color: #E5C585; font-size:1.1rem;">👤 {selected_member_name} ({m_nick}) 회원님 [{selected_hof_year}년]</h3>
                <div style="font-size: 0.85rem; line-height: 1.6;">
                    🎯 <b>{selected_hof_year}년 핸디캡:</b> {year_hc} | 📈 <b>평균 스코어:</b> {year_avg_sc}타<br>
                    ⛳ <b>총 참석:</b> {year_attended_cnt}회 / {total_year_rounds_cnt}라운드 | 📅 <b>참석률:</b> {year_att_rate}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"##### 🏌️‍♂️ {selected_hof_year}년도 라운드별 상세 스코어 및 출석 내역")
            
            if not year_completed_rounds:
                st.info(f"{selected_hof_year}년도에 완료된 필드 라운드가 없습니다.")
            else:
                member_rounds_data = []
                for r in year_completed_rounds:
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

    # 8. 📁 역대 조편성 아카이브
    elif menu == "역대 조편성 아카이브":
        st.subheader("📁 ARCHIVE (조편성 아카이브)")
        
        with st.expander("✍️ [OPERATOR] 조편성 기록 수동 직접 등록하기"):
            m_date = st.date_input("라운드 날짜", value=datetime.now().date(), key="manual_archive_date")
            m_title = st.text_input("라운드 명칭", value="8월 정기 필드 월례회", key="manual_archive_title")
            m_loc = st.text_input("골프장 장소", value="남서울CC", key="manual_archive_loc")
            
            st.markdown("##### ⛳ 조별 구성원 입력 (최대 4개 조)")
            approved_members = [k for k, v in member_db.items() if v.get("status", "approved") == "approved"]
            
            m_teams = []
            m_tee_times = []
            m_courses = []
            
            for j_idx in range(4):
                st.markdown(f"**{j_idx+1}조 구성**")
                mc1, mc2, mc3 = st.columns([2, 1, 1])
                with mc1:
                    j_members = st.multiselect(f"{j_idx+1}조 멤버 선택", approved_members, key=f"manual_team_{j_idx}")
                with mc2:
                    j_time = st.text_input(f"{j_idx+1}조 시간", value=f"08:{(j_idx*8):02d}", key=f"manual_time_{j_idx}")
                with mc3:
                    j_course = st.text_input(f"{j_idx+1}조 코스", value="IN 코스" if j_idx%2==1 else "OUT 코스", key=f"manual_course_{j_idx}")
                
                if j_members:
                    m_teams.append(j_members)
                    m_tee_times.append(j_time)
                    m_courses.append(j_course)

            if st.button("💾 아카이브에 수동 등록 저장", type="primary", use_container_width=True):
                if m_title and m_teams:
                    date_str_val = m_date.strftime("%Y-%m-%d")
                    new_log = {
                        "id": int(datetime.now().timestamp()),
                        "date": date_str_val,
                        "title": m_title,
                        "location": m_loc,
                        "tee_times": m_tee_times,
                        "courses": m_courses,
                        "event_type": "필드 월례회",
                        "teams": m_teams
                    }
                    match_logs.insert(0, new_log)
                    save_data(db)
                    st.success("등록되었습니다!")
                    st.rerun()
                else:
                    st.warning("라운드 명칭과 최소 1개 조 이상의 멤버를 선택해 주세요.")

        st.markdown("---")

        if not match_logs:
            st.warning("아직 저장된 조편성 이력이 없습니다.")
        else:
            log_options = [f"{log.get('date', '날짜미상')} | {log.get('title', log.get('event_type', '필드 월례회'))} ({log.get('location', '장소미상')})" for log in match_logs]
            selected_log_label = st.selectbox("📂 조회할 조편성 이력 선택", log_options)
            selected_log_idx = log_options.index(selected_log_label)
            log = match_logs[selected_log_idx]
            
            log_date = log.get('date', '날짜미상')
            log_title = log.get('title', log.get('event_type', '필드 월례회'))
            log_loc = log.get('location', '장소미상')
            
            st.markdown(f"### 🗓️ {log_date} | {log_title} - 🏟️ {log_loc}")
            
            if is_admin:
                with st.expander("🗑️ 조편성 이력 삭제 관리"):
                    conf_log = st.checkbox("정말로 이 조편성 이력을 삭제하시겠습니까?", key=f"conf_log_{selected_log_idx}")
                    if conf_log:
                        if st.button("⚠️ 최종 이력 삭제 실행", key=f"btn_del_log_{selected_log_idx}", type="primary", use_container_width=True):
                            match_logs.pop(selected_log_idx)
                            save_data(db)
                            st.success("수정되었습니다!")
                            st.rerun()
                    
            st.markdown("---")
            teams_list = log.get('teams', [])
            tee_times_list = log.get('tee_times', [])
            courses_list = log.get('courses', [])

            for t_idx, team in enumerate(teams_list):
                t_time = tee_times_list[t_idx] if t_idx < len(tee_times_list) else ""
                c_info = courses_list[t_idx] if t_idx < len(courses_list) else ""
                meta_str = f" ({t_time} / {c_info})" if (t_time or c_info) else ""
                
                team_html = f"<div class='team-box'><h3>⛳ {t_idx+1}조{meta_str}</h3>" + "<br>".join([f"• <b>{m}</b> ({member_db.get(m, {}).get('handicap', 0)})" for m in team]) + "</div>"
                st.markdown(team_html, unsafe_allow_html=True)

    # 9. 👥 회원 리스트
    elif menu.startswith("회원 리스트") or menu.startswith("회원 명부"):
        st.subheader("👥 MEMBER LIST (클럽 회원 리스트)")
        
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
            st.subheader("👑 [OPERATOR] 신입회원 가입 승인 센터")
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
                            st.success("등록되었습니다!")
                            st.rerun()

            st.divider()
            st.subheader("🚫 [OPERATOR] 회원 강퇴 관리")
            expel_candidates = [k for k in member_db.keys() if k != current_user and member_db[k].get("status", "approved") == "approved"]
            if expel_candidates:
                target_expel = st.selectbox("강퇴할 회원 선택", expel_candidates, key="target_expel")
                with st.expander("⚠️ 회원 강퇴 실행"):
                    conf_expel = st.checkbox(f"정말로 '{target_expel}' 회원을 클럽에서 강퇴하시겠습니까?", key="conf_expel")
                    if conf_expel:
                        if st.button("🚨 최종 강퇴 실행", type="primary", key="btn_expel", use_container_width=True):
                            member_db.pop(target_expel, None)
                            save_data(db)
                            st.success("수정되었습니다!")
                            st.rerun()
            else:
                st.info("강퇴할 수 있는 회원이 없습니다.")

    # 10. 👤 마이페이지
    elif menu == "마이페이지":
        st.subheader("👤 MY PAGE (마이페이지)")
        st.info("💡 회원 성함, 닉네임, 비밀번호, 보안 질문 및 프로필 사진을 관리할 수 있습니다.")
        
        with st.form("edit_profile_form"):
            edit_name = st.text_input("회원 성함", value=current_user)
            edit_nickname = st.text_input("클럽 닉네임", value=user_info.get("nickname", current_user))
            edit_pw = st.text_input("비밀번호 변경", value=user_info.get("password", "1234"), type="password")
            edit_friend = st.text_input("보안 질문: 어렸을 적 가장 친한 친구 이름", value=user_info.get("secret_friend", "친구"), key="edit_profile_friend")
            
            p_img_file = st.file_uploader("프로필 아바타 등록 (선택)", type=["jpg", "png", "jpeg"])
            if user_info.get("profile_img"):
                st.image(base64.b64decode(user_info["profile_img"]), width=100, caption="Current Profile Photo")
                
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
                user_info['secret_friend'] = edit_friend.strip() if edit_friend else "친구"
                
                if p_img_file is not None:
                    img_bytes = p_img_file.getvalue()
                    user_info['profile_img'] = base64.b64encode(img_bytes).decode()
                    
                save_data(db)
                st.success("수정되었습니다!")
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
                    st.success("수정되었습니다!")
                    st.rerun()
