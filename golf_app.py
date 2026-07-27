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
    initial_sidebar_state="expanded"
)

DB_FILE = "club_data.json"

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
    
    return {
        "total_events": 0,
        "member_db": member_db,
        "pair_history": pair_history,
        "feed_posts": feed_posts,
        "rounds_data": rounds_data,
        "match_logs": match_logs
    }

def save_data(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def recalculate_all_stats(db_obj):
    r_list = db_obj.get("rounds_data", [])
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

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,600&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    .stApp { background-color: #F7F4EF !important; font-family: 'Noto Sans KR', sans-serif; color: #1B3B2B; }
    .brand-header { background-color: #F7F4EF; text-align: center; padding: 20px 10px; border-bottom: 2px solid #D6CBBF; margin-bottom: 25px; }
    .brand-title { font-family: 'Playfair Display', serif; color: #1B3B2B; font-size: 2.2rem; font-weight: 700; margin: 5px 0 0 0; }
    .brand-subtitle { color: #A88B58; font-size: 0.9rem; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; }
    .css-card { background-color: #FFFFFF; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 4px 15px rgba(27, 59, 43, 0.05); border: 1px solid #E5DEC3; }
    .team-box { background-color: #1B3B2B; color: #F7F4EF; padding: 18px; border-radius: 12px; margin-bottom: 14px; border: 1px solid #A88B58; box-shadow: 0 4px 10px rgba(0,0,0,0.08); }
    .team-box h3 { color: #D4B475 !important; font-family: 'Playfair Display', serif; margin-bottom: 10px; border-bottom: 1px solid #325843; padding-bottom: 6px; }
    .badge-admin { background-color: #1B3B2B; color: #F7F4EF; padding: 4px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: 600; }
    .badge-user { background-color: #EAE3D9; color: #1B3B2B; padding: 4px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: 600; }
    .badge-hc { background-color: #F3EBDD; color: #A88B58; padding: 4px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: 700; border: 1px solid #D6CBBF; }
    .profile-avatar { width: 38px; height: 38px; border-radius: 50%; object-fit: cover; border: 2px solid #A88B58; margin-right: 10px; }
    .stButton>button { background-color: #1B3B2B !important; color: #F7F4EF !important; border-radius: 8px !important; border: 1px solid #A88B58 !important; font-weight: 600 !important; }
    .stButton>button:hover { background-color: #27523C !important; color: #FFFFFF !important; }
    section[data-testid="stSidebar"] { background-color: #EFE9E0 !important; border-right: 1px solid #D6CBBF; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand-header">
    <div style="font-size: 2.5rem;">🚩</div>
    <div class="brand-title">Segok Golf Club</div>
    <div class="brand-subtitle">GOLF SOCIETY</div>
</div>
""", unsafe_allow_html=True)

# --- LOGIN & SIGNUP ---
if not st.session_state.get('logged_in_user'):
    col_login, _ = st.columns([2, 1])
    with col_login:
        tab1, tab2 = st.tabs(["🔑 회원 로그인", "✨ 초간단 신입회원 가입"])
        
        with tab1:
            st.caption("초기 비밀번호는 '1234' 입니다.")
            approved_members = [k for k, v in member_db.items() if v.get("status", "approved") == "approved"]
            login_name = st.selectbox("회원 이름 선택", ["선택하세요"] + approved_members)
            login_pw = st.text_input("비밀번호 입력", type="password")
            
            if st.button("로그인", type="primary", use_container_width=True):
                if login_name in member_db:
                    user = member_db[login_name]
                    if user.get("status") != "approved":
                        st.error("⌛ 아직 운영진 가입 승인 대기 중입니다.")
                    elif login_pw == user.get("password", "1234"):
                        st.session_state.logged_in_user = login_name
                        st.success(f"{login_name}님 환영합니다!")
                        st.rerun()
                    else:
                        st.error("비밀번호가 올바르지 않습니다.")
                else:
                    st.warning("회원 이름을 선택해 주세요.")
                    
        with tab2:
            st.caption("외부 신규 회원은 가입 신청 후 운영진 승인을 거쳐 접속할 수 있습니다.")
            new_name = st.text_input("신입 회원 이름")
            new_nick = st.text_input("닉네임 설정 (선택)")
            new_pw = st.text_input("비밀번호 설정", type="password")
            
            if st.button("신규 회원 가입 신청하기", use_container_width=True):
                if new_name and new_pw:
                    if new_name in member_db:
                        st.error("이미 등록되어 있는 이름입니다.")
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
                        st.success(f"🎉 {new_name}님 가입 신청 완료! 운영진 승인 후 로그인하실 수 있습니다.")
                else:
                    st.warning("이름과 비밀번호를 모두 입력해 주세요.")
    st.stop()

current_user = st.session_state.logged_in_user
user_info = member_db.get(current_user, {
    "nickname": current_user, "handicap": 0, "attendance": 0, "is_admin": False
})

is_admin = user_info.get('is_admin', False)

with st.sidebar:
    st.title("⛳ Segok Golf Club")
    
    admin_badge = '<span class="badge-admin">👑 운영진</span>' if is_admin else '<span class="badge-user">👤 일반회원</span>'
    display_nickname = user_info.get('nickname', current_user)
    
    st.markdown(f"""
    <div style="background-color:#FFFFFF; padding:15px; border-radius:12px; border:1px solid #D6CBBF; margin-top:10px; margin-bottom:15px;">
        <h4 style="margin:0; color:#1B3B2B;">{display_nickname} 님 {admin_badge}</h4>
        <hr style="margin:10px 0; border-top:1px solid #EAE3D9;">
        <span class="badge-hc">핸디캡 {user_info.get('handicap', 0)}</span>
        <span class="badge-user">참석률 {user_info.get('attendance', 0)}%</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()
        
    st.divider()
    
    menu_options = ["📸 피드 (Segok Feed)"]
    if is_admin:
        menu_options.append("🎲 조편성기 (운영진)")
        
    menu_options.append("🏆 라운드별 성적 & 시상")
    menu_options.append("📜 지난 조편성 이력 관리")
    
    if is_admin:
        pending_count = len([k for k, v in member_db.items() if v.get("status") == "pending"])
        m_label = f"📊 회원 명부 & 승인 ({pending_count})" if pending_count > 0 else "📊 회원 명부 & 승인"
        menu_options.append(m_label)
        
    menu_options.append("⚙️ 내 정보 / 프로필 수정")
    
    menu = st.radio("📱 메뉴 이동", menu_options)

# 1. 📸 피드
if menu == "📸 피드 (Segok Feed)":
    st.subheader("📸 Segok Member Feed")
    with st.expander("✍️ 새 라운딩 사진 및 소식 올리기", expanded=True):
        post_text = st.text_area("내용", placeholder="오늘의 라운딩 일상을 자유롭게 나눠보세요...")
        uploaded_img = st.file_uploader("사진 첨부 (선택)", type=["jpg", "png", "jpeg"])
        
        if st.button("피드 공유하기", type="primary", use_container_width=True):
            if post_text or uploaded_img:
                img_b64 = None
                if uploaded_img is not None:
                    bytes_data = uploaded_img.getvalue()
                    img_b64 = base64.b64encode(bytes_data).decode()
                
                feed_posts.insert(0, {
                    "id": int(datetime.now().timestamp()),
                    "author": current_user,
                    "nickname": user_info.get("nickname", current_user),
                    "profile_img": user_info.get("profile_img", None),
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "content": post_text,
                    "image": img_b64,
                    "likes": 0,
                    "comments": []
                })
                save_data(db)
                st.success("피드가 작성되었습니다!")
                st.rerun()

    if not feed_posts:
        st.info("아직 등록된 피드가 없습니다. 첫 일상을 공유해 보세요!")
    else:
        for idx, post in enumerate(feed_posts):
            p_author = post.get("author", "알수없음")
            author_info = member_db.get(p_author, {})
            p_nickname = author_info.get("nickname", post.get("nickname", p_author))
            p_img = author_info.get("profile_img", post.get("profile_img"))
            
            if p_img:
                avatar_html = f'<img src="data:image/png;base64,{p_img}" class="profile-avatar">'
            else:
                avatar_html = '<span style="font-size:1.5rem; margin-right:8px;">👤</span>'
                
            st.markdown(f"""
            <div class="css-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div style="display:flex; align-items:center;">
                        {avatar_html}
                        <strong style="color:#1B3B2B; font-size:1.05rem;">{p_nickname}</strong>
                    </div>
                    <span style="color:#A88B58; font-size:0.8rem;">{post['date']}</span>
                </div>
                <p style="font-size:1rem; margin-bottom:10px; color:#1B3B2B;">{post['content']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if post.get("image"):
                st.image(base64.b64decode(post["image"]), use_column_width=True)
                
            c_lk, c_edit, c_del, _ = st.columns([1.5, 1.5, 1.5, 2.5])
            
            with c_lk:
                if st.button(f"❤️ {post['likes']}", key=f"lk_{post['id']}"):
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

# 2. 🎲 조편성기
elif menu == "🎲 조편성기 (운영진)":
    st.subheader("🎲 중복 방지 & 실력 균등 조편성기")
    if not is_admin:
        st.error("⛔ 조편성 기능은 운영진 전용 메뉴입니다.")
    else:
        st.success("👑 **운영자 권한 확인 완료** | 자동 조편성 후 수동으로 조 위치를 변경할 수 있습니다.")
        
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
            
            with st.expander("✏️ [운영진 전용] 조 구성원 수동으로 변경하기"):
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
            
            if st.button("💾 이 조편성을 최종 확정 및 성적 입력 카드 자동 생성", use_container_width=True):
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
                
                save_data(db)
                st.success("🎉 조편성이 최종 확정되었으며, [🏆 라운드별 성적 & 시상] 메뉴에 성적 입력 카드가 자동으로 생성되었습니다!")

# 3. 🏆 라운드별 성적 & 시상 (개선된 깔끔한 통계 통틀어 표기)
elif menu == "🏆 라운드별 성적 & 시상":
    st.subheader("🏆 라운드별 성적 및 자동 시상 내역")
    
    if not rounds_data:
        st.info("등록된 라운드가 없습니다. 운영진이 조편성을 확정하면 성적 입력 카드가 자동 생성됩니다.")
    else:
        for r_idx, r in enumerate(rounds_data):
            is_done = r.get("completed", False)
            status_tag = "✅ 성적 입력 완료" if is_done else "⌛ 성적 입력 대기 중"
            
            with st.expander(f"🚩 {r['date']} | {r['title']} [{status_tag}]", expanded=not is_done):
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
                            "회원 이름": member_db.get(p_name, {}).get("nickname", p_name),
                            "스코어": f"{p_info['score']}타",
                            "드라이버 비거리": f"{p_info['long']}m" if p_info['long'] > 0 else "-",
                            "니어 거리에 근접": f"{p_info['near']}m" if p_info['near'] > 0 else "-"
                        })
                    st.dataframe(pd.DataFrame(score_table), use_container_width=True)
                    
                if is_admin:
                    st.markdown("---")
                    col_a1, col_a2 = st.columns(2)
                    with col_a1:
                        btn_label = "✏️ 성적 수정하기" if is_done else "✍️ 스코어/롱기/니어 바로 입력하기"
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
                                    st.success("🎉 라운드 성적이 성공적으로 등록되었습니다!")
                                    st.rerun()

                    with col_a2:
                        if st.button(f"🗑️ 라운드 전체 삭제", key=f"del_rnd_{r['id']}"):
                            rounds_data.pop(r_idx)
                            recalculate_all_stats(db)
                            save_data(db)
                            st.success("해당 라운드가 삭제되었습니다.")
                            st.rerun()

    # --- 깔끔하게 정돈된 누적 통계 & TOP 10 랭킹 구역 ---
    st.divider()
    st.subheader("📊 클럽 누적 통계 & TOP 10 랭킹")
    st.caption("💡 진행된 모든 라운드 공식 기록을 바탕으로 산출된 통계입니다.")
    
    completed_r = [r for r in rounds_data if r.get("completed")]
    
    if not completed_r:
        st.warning("아직 완료된 라운드가 없어 통계 집계 데이터가 없습니다.")
    else:
        # 데이터 수집
        medalist_data = {} # {member: [count, min_score]}
        longist_data = {}  # {member: [count, max_long]}
        nearest_data = {}  # {member: [count, min_near]}
        attendance_counts = {}

        for r in completed_r:
            awards = r.get("awards", {})
            raw_m = awards.get("raw_medalist")
            raw_l = awards.get("raw_longist")
            raw_n = awards.get("raw_nearest")
            
            m_score = awards.get("raw_medalist_score", 0)
            l_dist = awards.get("raw_longist_dist", 0)
            n_dist = awards.get("raw_nearest_dist", 999)

            if raw_m:
                if raw_m not in medalist_data: medalist_data[raw_m] = [0, 999]
                medalist_data[raw_m][0] += 1
                if m_score < medalist_data[raw_m][1]: medalist_data[raw_m][1] = m_score
                
            if raw_l:
                if raw_l not in longist_data: longist_data[raw_l] = [0, 0]
                longist_data[raw_l][0] += 1
                if l_dist > longist_data[raw_l][1]: longist_data[raw_l][1] = l_dist
                
            if raw_n:
                if raw_n not in nearest_data: nearest_data[raw_n] = [0, 999.0]
                nearest_data[raw_n][0] += 1
                if n_dist < nearest_data[raw_n][1]: nearest_data[raw_n][1] = n_dist

            for m_name in r.get("scores", {}).keys():
                attendance_counts[m_name] = attendance_counts.get(m_name, 0) + 1

        col_st1, col_st2 = st.columns(2)
        
        with col_st1:
            st.markdown("##### 🥇 최저타(메달리스트) TOP 10")
            if medalist_data:
                med_list = []
                for m, val in medalist_data.items():
                    nick = member_db.get(m, {}).get("nickname", m)
                    med_list.append({"회원": nick, "우승 횟수": val[0], "최소 타수": f"{val[1]}타"})
                df_med = pd.DataFrame(med_list).sort_values(by=["우승 횟수", "최소 타수"], ascending=[False, True]).head(10).reset_index(drop=True)
                df_med.index += 1
                st.dataframe(df_med, use_container_width=True)
            else:
                st.info("기록 없음")

            st.markdown("##### 💣 롱기스트(최장타) TOP 10")
            if longist_data:
                long_list = []
                for m, val in longist_data.items():
                    nick = member_db.get(m, {}).get("nickname", m)
                    long_list.append({"회원": nick, "달성 횟수": val[0], "최고 비거리": f"{val[1]}m"})
                df_long = pd.DataFrame(long_list).sort_values(by=["달성 횟수", "최고 비거리"], ascending=[False, False]).head(10).reset_index(drop=True)
                df_long.index += 1
                st.dataframe(df_long, use_container_width=True)
            else:
                st.info("기록 없음")

        with col_st2:
            st.markdown("##### 🎯 니어리스트(최근접) TOP 10")
            if nearest_data:
                near_list = []
                for m, val in nearest_data.items():
                    nick = member_db.get(m, {}).get("nickname", m)
                    near_list.append({"회원": nick, "달성 횟수": val[0], "최단 거리": f"{val[1]}m"})
                df_near = pd.DataFrame(near_list).sort_values(by=["달성 횟수", "최단 거리"], ascending=[False, True]).head(10).reset_index(drop=True)
                df_near.index += 1
                st.dataframe(df_near, use_container_width=True)
            else:
                st.info("기록 없음")

            st.markdown("##### 📅 총 출석 라운드 횟수 TOP 10")
            if attendance_counts:
                att_list = [{"회원": member_db.get(k, {}).get("nickname", k), "참석 횟수": v} for k, v in attendance_counts.items()]
                df_att = pd.DataFrame(att_list).sort_values(by="참석 횟수", ascending=False).head(10).reset_index(drop=True)
                df_att.index += 1
                st.dataframe(df_att, use_container_width=True)
            else:
                st.info("기록 없음")

# 4. 📜 지난 조편성 이력 관리
elif menu == "📜 지난 조편성 이력 관리":
    st.subheader("📜 Segok Golf Club 지난 조편성 이력")
    if not match_logs:
        st.warning("아직 저장된 지난 조편성 이력이 없습니다.")
    else:
        for idx, log in enumerate(match_logs):
            with st.container():
                col_head1, col_head2 = st.columns([4, 1])
                with col_head1:
                    st.markdown(f"### 🗓️ {log['date']} | {log['event_type']}")
                with col_head2:
                    if is_admin:
                        if st.button(f"🗑️ 이력 삭제", key=f"del_log_{idx}"):
                            match_logs.pop(idx)
                            save_data(db)
                            st.success("해당 조편성 이력이 삭제되었습니다.")
                            st.rerun()
                
                cols = st.columns(min(len(log['teams']), 4))
                for t_idx, team in enumerate(log['teams']):
                    with cols[t_idx % 4]:
                        team_names = ", ".join([f"{m}({member_db.get(m, {}).get('handicap', '0')})" for m in team])
                        st.markdown(f"**⛳ {t_idx+1}조:** {team_names}")
                st.divider()

# 5. 📊 회원 명부 & 승인 관리 (운영진 전용)
elif menu.startswith("📊 회원 명부"):
    st.subheader("📊 Segok Golf Club 회원 명부")
    
    df_data = [{
        "이름": k, 
        "닉네임": v.get('nickname', k),
        "자동 산출 핸디캡": v.get('handicap', 0), 
        "연간 참석률": f"{v.get('attendance', 0)}%", 
        "총 라운드 참석": f"{v.get('rounds_played', 0)}회"
    } for k, v in member_db.items() if v.get("status", "approved") == "approved"]
    
    st.dataframe(pd.DataFrame(df_data), use_container_width=True)
    
    if is_admin:
        st.divider()
        st.subheader("👑 [운영진 전용] 신입회원 가입 승인 센터")
        pending_members = [k for k, v in member_db.items() if v.get("status") == "pending"]
        
        if not pending_members:
            st.info("현재 가입 승인 대기 중인 신입 회원이 없습니다.")
        else:
            for p_name in pending_members:
                col_p1, col_p2 = st.columns([3, 1])
                with col_p1:
                    st.write(f"👤 **신입 신청 회원:** `{p_name}`")
                with col_p2:
                    if st.button(f"✅ {p_name} 가입 승인", key=f"app_{p_name}"):
                        member_db[p_name]["status"] = "approved"
                        save_data(db)
                        st.success(f"🎉 {p_name} 회원의 가입 승인이 완료되었습니다!")
                        st.rerun()

# 6. ⚙️ 내 정보 / 프로필 수정
elif menu == "⚙️ 내 정보 / 프로필 수정":
    st.subheader("⚙️ 개인정보 및 프로필 수정")
    st.info("💡 이름, 닉네임, 비밀번호, 프로필 사진을 직접 변경할 수 있습니다.")
    
    with st.form("edit_profile_form"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            edit_name = st.text_input("회원 성함", value=current_user)
            edit_nickname = st.text_input("닉네임", value=user_info.get("nickname", current_user))
            edit_pw = st.text_input("비밀번호 변경", value=user_info.get("password", "1234"), type="password")
        with col_f2:
            p_img_file = st.file_uploader("프로필 사진 등록 (선택)", type=["jpg", "png", "jpeg"])
            if user_info.get("profile_img"):
                st.image(base64.b64decode(user_info["profile_img"]), width=100, caption="현재 등록된 프로필 사진")
            
        submit_btn = st.form_submit_button("💾 정보 저장하기", type="primary", use_container_width=True)
        
        if submit_btn:
            if edit_name != current_user:
                if edit_name in member_db:
                    st.error("이미 존재하는 회원 이름입니다.")
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
            st.success("🎉 개인정보 및 프로필 사진이 성공적으로 수정되었습니다!")
            st.rerun()
