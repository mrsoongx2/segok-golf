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
                    if "notices" not in data:
                        data["notices"] = []
                    # 피드에 liked_users(좋아요 누른 유저 목록) 마이그레이션 보장
                    for post in data.get("feed_posts", []):
                        if "liked_users" not in post:
                            post["liked_users"] = []
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
            "is_admin": True if name in ADMIN_MEMBERS else False
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

if 'db_data' not in st.session_state:
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
    if query_user and query_user in member_db and member_db[query_user].get("status") == "approved":
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
    
    .stApp { background-color: #FAFAFA !important; font-family: 'Noto Sans KR', sans-serif; color: #262626; }
    
    .compact-header { background-color: #FFFFFF; padding: 12px 24px; border-bottom: 1px solid #DBDBDB; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
    .header-title { font-family: 'Playfair Display', serif; color: #1B3B2B; font-size: 1.5rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; cursor: pointer; }
    
    .logo-hero { text-align: center; padding: 40px 20px 30px 20px; background: linear-gradient(135deg, #1B3B2B 0%, #2C523D 100%); border-radius: 16px; color: #FFFFFF; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(27,59,43,0.15); }
    .logo-hero h1 { font-family: 'Playfair Display', serif; font-size: 2.8rem; margin: 10px 0 5px 0; color: #F8F5F0; }
    .logo-hero p { color: #D4B475; font-size: 0.9rem; letter-spacing: 4px; text-transform: uppercase; font-weight: 600; margin: 0; }
    
    .menu-card { background-color: #FFFFFF; border-radius: 14px; border: 1px solid #DBDBDB; padding: 24px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.03); transition: all 0.2s ease; margin-bottom: 20px; }
    .menu-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.08); border-color: #1B3B2B; }
    
    .insta-card { background-color: #FFFFFF; border-radius: 12px; border: 1px solid #DBDBDB; max-width: 650px; margin: 0 auto 24px auto; box-shadow: 0 2px 8px rgba(0,0,0,0.03); overflow: hidden; }
    .insta-header { display: flex; align-items: center; padding: 14px 16px; border-bottom: 1px solid #EFEFEF; background-color: #FFFFFF; }
    .insta-body { padding: 16px; font-size: 0.95rem; color: #262626; line-height: 1.5; }
    
    .team-box { background-color: #1B3B2B; color: #FFFFFF; padding: 18px; border-radius: 12px; margin-bottom: 14px; border: 1px solid #C5A059; }
    .team-box h3 { color: #E5C585 !important; font-family: 'Playfair Display', serif; margin-bottom: 10px; border-bottom: 1px solid #2C523D; padding-bottom: 6px; }
    .badge-admin { background-color: #1B3B2B; color: #FFFFFF; padding: 3px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 600; border: 1px solid #C5A059; }
    .badge-user { background-color: #EFEFEF; color: #262626; padding: 3px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 600; }
    .badge-hc { background-color: #FDF8F0; color: #B38F4E; padding: 3px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 700; border: 1px solid #E5DEC3; }
    .profile-avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; border: 1.5px solid #C5A059; margin-right: 12px; }
    
    .stButton>button { background-color: #1B3B2B !important; color: #FFFFFF !important; border-radius: 8px !important; border: none !important; font-weight: 600 !important; }
    .stButton>button:hover { background-color: #27523C !important; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN & SIGNUP ---
if not st.session_state.get('logged_in_user'):
    st.markdown("""
    <div style="text-align: center; padding: 45px 0 25px 0;">
        <div style="font-size: 3rem;">⛳</div>
        <h1 style="font-family: 'Playfair Display', serif; color: #1B3B2B; margin: 10px 0 0 0; font-size: 2.5rem;">Segok Golf Club</h1>
        <p style="color: #8E8E8E; font-size: 0.85rem; letter-spacing: 4px; text-transform: uppercase;">PREMIUM GOLF SOCIETY</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_login, _ = st.columns([2, 1])
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
                    if user.get("status") != "approved":
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
                            "is_admin": True if new_name in ADMIN_MEMBERS else False
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
user_info = member_db.get(current_user, {
    "nickname": current_user, "handicap": 0, "attendance": 0, "is_admin": False
})

is_admin = user_info.get('is_admin', False)
display_nickname = user_info.get('nickname', current_user)
admin_badge = '<span class="badge-admin">👑 운영진</span>' if is_admin else '<span class="badge-user">👤 정회원</span>'

# --- 상단 고정 헤더 ---
col_h1, col_h2 = st.columns([3, 2])
with col_h1:
    if st.button("⛳ Segok Golf Club", key="logo_home_btn"):
        set_menu("HOME")
        st.rerun()
with col_h2:
    hc_val = user_info.get('handicap', 0)
    att_val = user_info.get('attendance', 0)
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; align-items: center; gap: 10px; padding-top: 5px;">
        <span style="font-size:0.9rem;"><b>{display_nickname}</b>님 {admin_badge}</span>
        <span class="badge-hc">HC {hc_val}</span>
        <span class="badge-user">참석 {att_val}%</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 10px 0 20px 0; border-top: 1px solid #DBDBDB;'>", unsafe_allow_html=True)

if st.session_state.current_menu == "HOME":
    st.markdown("""
    <div class="logo-hero">
        <div style="font-size: 3.5rem; margin-bottom: 5px;">🏆</div>
        <h1>Segok Golf Club</h1>
        <p>PREMIUM GOLF SOCIETY & COMMUNITY</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="menu-card">
            <h3>💬 클럽 라운지</h3>
            <p style="color: #666; font-size: 0.9rem; margin-bottom: 15px;">라운딩 추억과 사진, 영상을 멤버들과 함께 공유하세요.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("클럽 라운지 입장", use_container_width=True, key="go_lounge"):
            set_menu("클럽 라운지")
            st.rerun()
            
        if is_admin:
            st.markdown("""
            <div class="menu-card" style="margin-top: 20px;">
                <h3>⛳ 티타임 조편성</h3>
                <p style="color: #666; font-size: 0.9rem; margin-bottom: 15px;">중복 방지 및 실력 균등 맞춤형 조편성을 실행합니다.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("티타임 조편성 입장", use_container_width=True, key="go_match"):
                set_menu("티타임 조편성")
                st.rerun()

    with c2:
        st.markdown("""
        <div class="menu-card">
            <h3>🏆 경기 결과 및 랭킹</h3>
            <p style="color: #666; font-size: 0.9rem; margin-bottom: 15px;">역대 필드 라운드 스코어, 공식 시상 및 누적 랭킹 TOP 10</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("경기 결과 및 랭킹 입장", use_container_width=True, key="go_result"):
            set_menu("경기 결과 및 랭킹")
            st.rerun()
            
        if is_admin:
            pending_cnt = len([k for k, v in member_db.items() if v.get("status") == "pending"])
            badge_txt = f" (승인대기 {pending_cnt})" if pending_cnt > 0 else ""
            st.markdown(f"""
            <div class="menu-card" style="margin-top: 20px;">
                <h3>👥 클럽 회원 명부{badge_txt}</h3>
                <p style="color: #666; font-size: 0.9rem; margin-bottom: 15px;">정회원 목록 관리 및 신입 회원 가입 승인 센터</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("클럽 회원 명부 입장", use_container_width=True, key="go_members"):
                set_menu("클럽 회원 명부")
                st.rerun()

    with c3:
        st.markdown("""
        <div class="menu-card">
            <h3>📁 역대 조편성 아카이브</h3>
            <p style="color: #666; font-size: 0.9rem; margin-bottom: 15px;">지난 날짜별 조편성 기록과 매칭 이력을 확인합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("역대 조편성 입장", use_container_width=True, key="go_archive"):
            set_menu("역대 조편성 아카이브")
            st.rerun()
            
        st.markdown("""
        <div class="menu-card" style="margin-top: 20px;">
            <h3>📢 클럽 공지사항</h3>
            <p style="color: #666; font-size: 0.9rem; margin-bottom: 15px;">운영진이 공지하는 주요 소식과 안내 사항 확인</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("클럽 공지사항 입장", use_container_width=True, key="go_notice"):
            set_menu("클럽 공지사항")
            st.rerun()

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        if st.button("👤 마이페이지 설정", use_container_width=True, key="go_mypage"):
            set_menu("마이페이지")
            st.rerun()
    with c_m2:
        if st.button("🚪 클럽 로그아웃", use_container_width=True, key="home_logout_btn"):
            st.session_state.logged_in_user = None
            set_menu("HOME")
            try:
                st.query_params.clear()
            except Exception:
                pass
            st.rerun()

else:
    menu_list = ["메인 홈", "💬 클럽 라운지", "🏆 경기 결과 및 랭킹", "📁 역대 조편성 아카이브", "📢 클럽 공지사항", "👤 마이페이지"]
    if is_admin:
        menu_list.insert(1, "⛳ 티타임 조편성")
        menu_list.append("👥 회원 명부")
        
    current_label_map = {
        "HOME": "메인 홈",
        "클럽 라운지": "💬 클럽 라운지",
        "티타임 조편성": "⛳ 티타임 조편성",
        "경기 결과 및 랭킹": "🏆 경기 결과 및 랭킹",
        "역대 조편성 아카이브": "📁 역대 조편성 아카이브",
        "클럽 공지사항": "📢 클럽 공지사항",
        "회원 명부": "👥 회원 명부",
        "마이페이지": "👤 마이페이지"
    }
    reverse_map = {v: k for k, v in current_label_map.items()}
    curr_label = current_label_map.get(st.session_state.current_menu, "💬 클럽 라운지")

    nav_c1, nav_c2, nav_c3 = st.columns([3, 3, 2])
    with nav_c1:
        selected_nav = st.selectbox("📌 빠른 메뉴 이동", menu_list, index=menu_list.index(curr_label) if curr_label in menu_list else 0)
        target_menu = reverse_map.get(selected_nav, "HOME")
        if target_menu != st.session_state.current_menu:
            set_menu(target_menu)
            st.rerun()
    with nav_c3:
        if st.button("🚪 로그아웃", use_container_width=True, key="top_logout"):
            st.session_state.logged_in_user = None
            set_menu("HOME")
            try:
                st.query_params.clear()
            except Exception:
                pass
            st.rerun()

    st.markdown("<hr style='margin: 15px 0 20px 0; border-top: 1px solid #DBDBDB;'>", unsafe_allow_html=True)
    
    menu = st.session_state.current_menu

    # 1. 💬 클럽 라운지 (인당 하트 1번 제한 기능 탑재)
    if menu == "클럽 라운지":
        st.subheader("💬 클럽 라운지 (Community Lounge)")
        with st.expander("✍️ 새 라운딩 소식 및 미디어 공유하기", expanded=True):
            post_text = st.text_area("내용 작성", placeholder="오늘의 멋진 라운딩 추억을 사진이나 영상과 함께 공유해 보세요...")
            uploaded_file = st.file_uploader("사진 또는 동영상 첨부 (선택)", type=["jpg", "png", "jpeg", "mp4", "mov", "avi"])
            
            if st.button("피드 발행하기", type="primary", use_container_width=True):
                if post_text or uploaded_file:
                    media_path = None
                    media_type = None
                    if uploaded_file is not None:
                        file_ext = uploaded_file.name.split('.')[-1].lower()
                        file_name = f"{int(datetime.now().timestamp())}_{uploaded_file.name}"
                        media_path = os.path.join(UPLOAD_DIR, file_name)
                        with open(media_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        media_type = "video" if file_ext in ["mp4", "mov", "avi"] else "image"
                    
                    feed_posts.insert(0, {
                        "id": int(datetime.now().timestamp()),
                        "author": current_user,
                        "nickname": user_info.get("nickname", current_user),
                        "profile_img": user_info.get("profile_img", None),
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "content": post_text,
                        "media_path": media_path,
                        "media_type": media_type,
                        "likes": 0,
                        "liked_users": [],
                        "comments": []
                    })
                    save_data(db)
                    st.success("피드가 발행되었습니다!")
                    st.rerun()

        if not feed_posts:
            st.info("아직 등록된 피드가 없습니다. 첫 소식을 공유해 보세요!")
        else:
            for idx, post in enumerate(feed_posts):
                p_author = post.get("author", "알수없음")
                author_info = member_db.get(p_author, {})
                p_nickname = author_info.get("nickname", post.get("nickname", p_author))
                p_img = author_info.get("profile_img", post.get("profile_img"))
                
                if p_img:
                    avatar_html = f'<img src="data:image/png;base64,{p_img}" class="profile-avatar">'
                else:
                    avatar_html = '<span style="font-size:1.5rem; margin-right:10px;">👤</span>'
                    
                st.markdown(f"""
                <div class="insta-card">
                    <div class="insta-header">
                        {avatar_html}
                        <div>
                            <strong style="color:#262626; font-size:0.95rem;">{p_nickname}</strong><br>
                            <span style="color:#8E8E8E; font-size:0.75rem;">{post['date']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                m_path = post.get("media_path")
                if m_path and os.path.exists(m_path):
                    if post.get("media_type") == "video":
                        st.video(m_path)
                    else:
                        st.image(m_path, use_column_width=True)

                if post.get('content'):
                    st.markdown(f"""
                    <div class="insta-body">
                        <p style="margin:0; color:#262626; word-break:break-all;">{post['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown("</div>", unsafe_allow_html=True)
                    
                c_lk, c_edit, c_del, _ = st.columns([1.8, 1.5, 1.5, 2.2])
                
                with c_lk:
                    liked_list = post.setdefault("liked_users", [])
                    has_liked = current_user in liked_list
                    heart_label = f"❤️ 좋아요 취소 ({post['likes']})" if has_liked else f"🤍 좋아요 ({post['likes']})"
                    
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
                        with st.expander("✏️ 수정"):
                            edited_content = st.text_area("내용 수정", value=post['content'], key=f"edt_txt_{post['id']}")
                            if st.button("저장", key=f"btn_edt_{post['id']}"):
                                post['content'] = edited_content
                                save_data(db)
                                st.success("수정되었습니다.")
                                st.rerun()

                if post['author'] == current_user or is_admin:
                    with c_del:
                        if st.button("🗑️ 삭제", key=f"del_post_{post['id']}"):
                            feed_posts.pop(idx)
                            save_data(db)
                            st.success("게시글이 삭제되었습니다.")
                            st.rerun()

                with st.expander(f"💬 댓글 ({len(post.get('comments', []))})"):
                    for c in post.get('comments', []):
                        c_author = c.get('author', '')
                        c_nick = member_db.get(c_author, {}).get("nickname", c_author)
                        st.write(f"**{c_nick}**: {c['text']}")
                    new_c = st.text_input("댓글 작성", key=f"nc_{post['id']}")
                    if st.button("등록", key=f"btn_c_{post['id']}") and new_c:
                        post.setdefault('comments', []).append({"author": current_user, "text": new_c})
                        save_data(db)
                        st.rerun()

    # 2. ⛳ 티타임 조편성
    elif menu == "티타임 조편성":
        st.subheader("⛳ 티타임 조편성 및 매칭 시스템")
        if not is_admin:
            st.error("⛔ 조편성 기능은 운영진 전용 메뉴입니다.")
        else:
            st.success("👑 **운영자 권한 확인 완료** | 중복 방지 및 균등 조편성을 실행할 수 있습니다.")
            
            c_mode1, c_mode2 = st.columns(2)
            with c_mode1:
                event_type = st.radio("모임 구분", ["필드 월례회 ⛳", "스크린 월례회 🖥️"])
            with c_mode2:
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
                st.session_state.current_event_type = event_type
                st.success("🎉 자동 조편성이 완료되었습니다!")

            if 'generated_teams' in st.session_state and st.session_state.generated_teams:
                teams = st.session_state.generated_teams
                e_type = st.session_state.get('current_event_type', event_type)
                
                with st.expander("✏️ 조 구성원 수동으로 변경하기"):
                    st.info("특정 회원을 선택하여 원하는 조로 바꿀 수 있습니다.")
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        move_mem = st.selectbox("이동시킬 회원 선택", selected_attendees)
                    with col_m2:
                        target_team_num = st.selectbox("이동할 조 선택", [f"{i+1}조" for i in range(len(teams))])
                        
                    if st.button("🔄 해당 회원을 선택한 조로 이동"):
                        for t in teams:
                            if move_mem in t:
                                t.remove(move_mem)
                        target_idx = int(target_team_num.replace("조", "")) - 1
                        teams[target_idx].append(move_mem)
                        st.session_state.generated_teams = teams
                        st.success(f"{move_mem} 회원이 {target_team_num}로 이동되었습니다.")
                        st.rerun()

                cols = st.columns(min(len(teams), 4))
                notice_text = f"📢 Segok Golf Club [{e_type}] 조편성 안내\n"
                notice_text += f"🗓️ 참석 인원: 총 {len(selected_attendees)}명 ({len(teams)}개 조)\n"
                notice_text += "-------------------------\n"
                
                for idx, team in enumerate(teams):
                    with cols[idx % 4]:
                        team_html = f"<div class='team-box'><h3>⛳ {idx+1}조</h3>" + "<br>".join([f"• <b>{m}</b> ({member_db.get(m, {}).get('handicap', 0)})" for m in team]) + "</div>"
                        st.markdown(team_html, unsafe_allow_html=True)
                    team_str = ", ".join([f"{m}({member_db.get(m, {}).get('handicap', 0)})" for m in team])
                    notice_text += f"🔹 {idx+1}조: {team_str}\n"
                
                notice_text += "-------------------------\n"
                notice_text += "즐거운 라운딩 되세요! 🏌️‍♂️✨"
                
                st.subheader("📱 카카오톡 공지문 복사")
                st.code(notice_text, language="text")
                
                btn_msg = "💾 이 조편성을 최종 확정 및 경기 결과 카드 생성" if "필드" in e_type else "💾 이 조편성 저장 (스크린은 경기결과 미포함)"
                if st.button(btn_msg, use_container_width=True):
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
                        "event_type": e_type,
                        "teams": teams
                    })
                    
                    if "필드" in e_type:
                        round_entry = {
                            "id": int(datetime.now().timestamp()),
                            "title": f"{datetime.now().month}월 정기 {e_type}",
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "type": e_type,
                            "teams": teams,
                            "scores": {},
                            "completed": False,
                            "awards": {"medalist": "-", "longist": "-", "nearest": "-"}
                        }
                        rounds_data.insert(0, round_entry)
                        st.success("🎉 조편성이 최종 확정되었으며, [경기 결과 및 랭킹] 메뉴에 결과 입력 카드가 생성되었습니다!")
                    else:
                        st.success("🎉 스크린 조편성 이력이 저장되었습니다. (스크린은 공식 경기결과 대상에서 제외됩니다)")
                    
                    save_data(db)

    # 3. 🏆 경기 결과 및 랭킹 (요청하신 클릭 가능한 테이블 형식 개편 적용)
    elif menu == "경기 결과 및 랭킹":
        st.subheader("🏆 경기 결과 및 클럽 랭킹 통계")
        
        field_rounds = [r for r in rounds_data if "필드" in r.get("type", "")]
        
        if not field_rounds:
            st.info("등록된 필드 경기 결과가 없습니다. 운영진이 필드 조편성을 확정하면 입력 카드가 생성됩니다.")
        else:
            st.markdown("##### 📋 역대 필드 라운드 목록 (표에서 확인하고 조회할 라운드를 선택하세요)")
            
            summary_list = []
            for idx, r in enumerate(field_rounds):
                summary_list.append({
                    "선택 번호": idx + 1,
                    "날짜": r['date'],
                    "라운드 명칭": r['title'],
                    "상태": "✅ 입력 완료" if r.get('completed') else "⌛ 입력 대기",
                    "메달리스트": r['awards']['medalist'],
                    "롱기스트": r['awards']['longist'],
                    "니어리스트": r['awards']['nearest']
                })
            df_summary = pd.DataFrame(summary_list)
            st.table(df_summary)
            
            # 라운드 선택 넘버 셀렉터
            chosen_num = st.selectbox("🔍 위 표에서 확인하실 라운드 번호를 선택하세요", [item["선택 번호"] for item in summary_list])
            selected_r_idx = chosen_num - 1
            r = field_rounds[selected_r_idx]
            
            is_done = r.get("completed", False)
            status_tag = "✅ 성적 입력 완료" if is_done else "⌛ 성적 입력 대기 중"
            
            st.markdown(f"""
            <div class="css-card" style="margin-top: 15px;">
                <h3 style="color:#1B3B2B; margin-top:0;">🚩 [선택된 라운드] {r['date']} | {r['title']} [{status_tag}]</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if is_done:
                st.markdown(f"""
                <div class="css-card">
                    <h4 style="color:#A88B58; margin-bottom:10px;">🏆 공식 시상 내역</h4>
                    <p>🥇 <b>메달리스트 (최저타):</b> {r['awards']['medalist']}</p>
                    <p>💣 <b>롱기스트 (최장타):</b> {r['awards']['longist']}</p>
                    <p>🎯 <b>니어리스트 (최근접):</b> {r['awards']['nearest']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("##### 📊 회원별 스코어 기록표")
                score_table = []
                for p_name, p_info in r['scores'].items():
                    score_table.append({
                        "회원 성함(닉네임)": f"{p_name} ({member_db.get(p_name, {}).get('nickname', p_name)})",
                        "스코어": f"{p_info['score']}타",
                        "드라이버 비거리": f"{p_info['long']}m" if p_info['long'] > 0 else "-",
                        "니어 근접거리": f"{p_info['near']}m" if p_info['near'] > 0 else "-"
                    })
                st.table(pd.DataFrame(score_table))
                
            if is_admin:
                st.markdown("---")
                col_a1, col_a2 = st.columns(2)
                with col_a1:
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

                        if st.button("🏆 성적 최종 저장 및 시상 자동 계산", key=f"sv_rnd_{r['id']}", type="primary"):
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

                with col_a2:
                    if st.button(f"🗑️ 현재 선택한 라운드 삭제", key=f"del_rnd_{r['id']}"):
                        rounds_data.remove(r)
                        recalculate_all_stats(db)
                        save_data(db)
                        st.success("해당 라운드가 삭제되었습니다.")
                        st.rerun()

        # --- 누적 통계 & 랭킹 ---
        st.divider()
        st.subheader("📊 클럽 누적 통계 & TOP 10 랭킹")
        st.caption("💡 필드 공식 라운드 기록 및 달성된 골프장/날짜 정보를 포함한 종합 통계입니다.")
        
        completed_r = [r for r in field_rounds if r.get("completed")]
        
        if not completed_r:
            st.warning("아직 완료된 필드 라운드가 없어 통계 집계 데이터가 없습니다.")
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

            col_st1, col_st2 = st.columns(2)
            
            with col_st1:
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
                else:
                    st.info("기록 없음")

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
                else:
                    st.info("기록 없음")

            with col_st2:
                st.markdown("##### 🎯 니어리스트(최근접) 랭킹")
                if nearest_records:
                    n_df_raw = pd.DataFrame(nearest_records)
                    n_agg = n_df_raw.groupby("member").agg(
                        달성횟수=("dist", "count"),
                        최단거리=("dist", "min"),
                        달성라운드=("round", lambda x: ", ".join(x))
                    ).reset_index().sort_values(by=["달성횟수", "최단거리"], ascending=[False, True]).head(10)
                    
                    n_agg["회원"] = n_agg["member"].apply(lambda x: member_db.get(x, {}).get("nickname", x))
                    display_n = n_agg[["회원", "달성횟수", "최단거리", "달성라운드"]].copy()
                    display_n["달성 횟수"] = display_n["달성횟수"].astype(str) + "회"
                    display_n["최단 거리"] = display_n["최단거리"].astype(str) + "m"
                    display_n = display_n.drop(columns=["달성횟수", "최단거리"])
                    display_n.index += 1
                    st.table(display_n)
                else:
                    st.info("기록 없음")

                st.markdown("##### 📅 총 출석 라운드 횟수 TOP 10")
                if attendance_counts:
                    att_list = [{"회원": member_db.get(k, {}).get("nickname", k), "참석 횟수": f"{v}회"} for k, v in attendance_counts.items()]
                    df_att = pd.DataFrame(att_list).sort_values(by="참석 횟수", ascending=False).head(10).reset_index(drop=True)
                    df_att.index += 1
                    st.table(df_att)
                else:
                    st.info("기록 없음")

    # 4. 📁 역대 조편성 아카이브
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
                if st.button("🗑️ 선택한 조편성 이력 삭제하기", type="primary"):
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

    # 5. 📢 클럽 공지사항
    elif menu == "클럽 공지사항":
        st.subheader("📢 클럽 공지사항")
        st.caption("세곡 골프클럽의 주요 소식과 안내 사항을 확인하세요.")
        
        if is_admin:
            with st.expander("✍️ [운영진] 새 공지사항 등록하기"):
                n_title = st.text_input("공지 제목")
                n_content = st.text_area("공지 내용")
                if st.button("공지 발행", type="primary"):
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
                <div class="insta-card" style="padding: 20px; max-width: 100%;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <h4 style="color:#1B3B2B; margin:0;">📌 {notice['title']}</h4>
                        <span style="color:#8E8E8E; font-size:0.85rem;">{notice['date']}</span>
                    </div>
                    <hr style="margin:10px 0; border-top:1px solid #EFEFEF;">
                    <p style="color:#262626; font-size:1rem; line-height:1.6; white-space: pre-wrap; margin:0;">{notice['content']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if is_admin:
                    if st.button("🗑️ 공지 삭제", key=f"del_notice_{notice['id']}"):
                        notices.pop(n_idx)
                        save_data(db)
                        st.success("공지사항이 삭제되었습니다.")
                        st.rerun()

    # 6. 👥 회원 명부 (운영진 전용)
    elif menu.startswith("회원 명부"):
        st.subheader("👥 클럽 회원 명부")
        
        df_data = [{
            "성함": k, 
            "닉네임": v.get('nickname', k),
            "핸디캡": v.get('handicap', 0), 
            "연간 참석률": f"{v.get('attendance', 0)}%", 
            "총 라운드 참석": f"{v.get('rounds_played', 0)}회"
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
                        if st.button(f"✅ {p_name} 승인", key=f"app_{p_name}"):
                            member_db[p_name]["status"] = "approved"
                            save_data(db)
                            st.success(f"🎉 {p_name} 회원의 가입이 최종 승인되었습니다!")
                            st.rerun()

    # 7. 👤 마이페이지
    elif menu == "마이페이지":
        st.subheader("👤 마이페이지 & 프로필 설정")
        st.info("💡 회원 성함, 닉네임, 비밀번호 및 프로필 사진을 직접 관리할 수 있습니다.")
        
        with st.form("edit_profile_form"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                edit_name = st.text_input("회원 성함", value=current_user)
                edit_nickname = st.text_input("클럽 닉네임", value=user_info.get("nickname", current_user))
                edit_pw = st.text_input("비밀번호 변경", value=user_info.get("password", "1234"), type="password")
            with col_f2:
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
