import streamlit as st
import pandas as pd
import numpy as np
import random
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="Segok Golf Club", 
    page_icon="⛳", 
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "club_data.json"

# 운영진 4명 지정
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
                return json.load(f)
        except Exception:
            pass
    
    # 초기 기록 0 설정 (상태: approved)
    member_db = {}
    for name in DEFAULT_MEMBERS:
        member_db[name] = {
            "password": "1234",
            "handicap": 0,
            "attendance": 0,
            "rounds_played": 0,
            "score_history": [],
            "status": "approved", # 기존 기본 회원은 승인 상태
            "is_admin": True if name in ADMIN_MEMBERS else False
        }
    pair_history = {m1: {m2: 0 for m2 in DEFAULT_MEMBERS} for m1 in DEFAULT_MEMBERS}
    feed_posts = [] # 깨끗한 피드 (하트 0개)
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
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'db_data' not in st.session_state:
    st.session_state.db_data = load_data()

db = st.session_state.db_data
member_db = db["member_db"]
pair_history = db["pair_history"]
feed_posts = db["feed_posts"]
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
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

if not st.session_state.logged_in_user:
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
                        st.error("⌛ 아직 운영진 가입 승인 대기 중입니다. 승인 후 로그인할 수 있습니다.")
                    elif login_pw == user.get("password", "1234"):
                        st.session_state.logged_in_user = login_name
                        st.success(f"{login_name}님 환영합니다!")
                        st.rerun()
                    else:
                        st.error("비밀번호가 올바르지 않습니다.")
                else:
                    st.warning("회원 이름을 선택해 주세요.")
                    
        with tab2:
            st.caption("가입 신청 후 운영진 승인을 거쳐 접속할 수 있습니다.")
            new_name = st.text_input("신입 회원 이름")
            new_pw = st.text_input("비밀번호 설정", type="password")
            
            if st.button("신규 회원 가입 신청하기", use_container_width=True):
                if new_name and new_pw:
                    if new_name in member_db:
                        st.error("이미 등록되어 있는 이름입니다.")
                    else:
                        member_db[new_name] = {
                            "password": new_pw,
                            "handicap": 0,
                            "attendance": 0,
                            "rounds_played": 0,
                            "score_history": [],
                            "status": "pending", # 가입 승인 대기 상태
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
user_info = member_db[current_user]

with st.sidebar:
    st.title("⛳ Segok Golf Club")
    
    admin_badge = '<span class="badge-admin">👑 운영진</span>' if user_info['is_admin'] else '<span class="badge-user">👤 일반회원</span>'
    st.markdown(f"""
    <div style="background-color:#FFFFFF; padding:15px; border-radius:12px; border:1px solid #D6CBBF; margin-top:10px; margin-bottom:15px;">
        <h4 style="margin:0; color:#1B3B2B;">{current_user} 님 {admin_badge}</h4>
        <hr style="margin:10px 0; border-top:1px solid #EAE3D9;">
        <span class="badge-hc">핸디캡 {user_info['handicap']}</span>
        <span class="badge-user">참석률 {user_info['attendance']}%</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()
        
    st.divider()
    
    pending_count = len([k for k, v in member_db.items() if v.get("status") == "pending"])
    menu_title_member = f"📊 회원 명부 & 승인 ({pending_count})" if pending_count > 0 and user_info['is_admin'] else "📊 회원 명부 & 승인"
    
    menu = st.radio("📱 메뉴 이동", [
        "📸 피드 (Segok Feed)", 
        "🎲 조편성기 (운영진)", 
        "🏆 라운드별 성적 & 시상", 
        "📜 지난 조편성 이력 관리",
        menu_title_member
    ])

# 1. 📸 피드
if menu == "📸 피드 (Segok Feed)":
    st.subheader("📸 Segok Member Feed")
    with st.expander("✍️ 새 라운딩 사진 및 소식 올리기", expanded=True):
        post_text = st.text_area("내용", placeholder="오늘의 라운딩 일상을 자유롭게 나눠보세요...")
        uploaded_img = st.file_uploader("사진 첨부 (선택)", type=["jpg", "png", "jpeg"])
        if st.button("피드 공유하기", type="primary", use_container_width=True):
            if post_text or uploaded_img:
                feed_posts.insert(0, {
                    "id": len(feed_posts) + 1,
                    "author": current_user,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "content": post_text,
                    "likes": 0, # 초기 하트 0개
                    "comments": []
                })
                save_data(db)
                st.success("피드가 작성되었습니다!")
                st.rerun()

    if not feed_posts:
        st.info("아직 등록된 피드가 없습니다. 첫 일상을 공유해 보세요!")
    else:
        for post in feed_posts:
            st.markdown(f"""
            <div class="css-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <strong style="color:#1B3B2B;">👤 {post['author']}</strong>
                    <span style="color:#A88B58; font-size:0.8rem;">{post['date']}</span>
                </div>
                <p style="font-size:1rem; margin-bottom:10px; color:#1B3B2B;">{post['content']}</p>
            </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns([1, 4])
            with c1:
                if st.button(f"❤️ {post['likes']}", key=f"lk_{post['id']}"):
                    post['likes'] += 1
                    save_data(db)
                    st.rerun()
            with st.expander(f"💬 댓글 ({len(post['comments'])})"):
                for c in post['comments']:
                    st.write(f"**{c['author']}**: {c['text']}")
                new_c = st.text_input("댓글 작성", key=f"nc_{post['id']}")
                if st.button("등록", key=f"btn_c_{post['id']}") and new_c:
                    post['comments'].append({"author": current_user, "text": new_c})
                    save_data(db)
                    st.rerun()

# 2. 🎲 조편성기 (자동 + 수동 변경 기능)
elif menu == "🎲 조편성기 (운영진)":
    st.subheader("🎲 중복 방지 & 실력 균등 조편성기")
    if not user_info['is_admin']:
        st.error("⛔ 조편성 기능은 운영진 전용 메뉴입니다.")
    else:
        st.success("👑 **운영자 권한 확인 완료** | 자동 조편성 후 수동으로 조 위치를 변경할 수 있습니다.")
        
        c_mode1, c_mode2 = st.columns(2)
        with c_mode1:
            event_type = st.radio("모임 구분", ["필드 월례회 ⛳", "스크린 월례회 🖥️"])
        with c_mode2:
            balance_rule = st.radio("조편성 방식", ["과거 동반 중복 방지 (기본)", "핸디캡 균등 배정 (고수+초보 믹스)"])
        
        approved_names = [k for k, v in member_db.items() if v.get("status", "approved") == "approved"]
        selected_attendees = st.multiselect("오늘 참석자 선택", approved_names, default=approved_names[:16])
        
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
            st.success("🎉 자동 조편성이 완료되었습니다! 아래에서 필요시 수동으로 조를 이동하세요.")

        if 'generated_teams' in st.session_state:
            teams = st.session_state.generated_teams
            e_type = st.session_state.get('current_event_type', event_type)
            
            # [운영진 조 수동 이동 변경 기능]
            with st.expander("✏️ [운영진 전용] 조 구성원 수동으로 변경하기"):
                st.info("특정 회원을 선택하여 원하는 조로 바꿀 수 있습니다.")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    move_mem = st.selectbox("이동시킬 회원 선택", selected_attendees)
                with col_m2:
                    target_team_num = st.selectbox("이동할 조 선택", [f"{i+1}조" for i in range(len(teams))])
                    
                if st.button("🔄 해당 회원을 선택한 조로 이동"):
                    # 기존 조에서 제거
                    for t in teams:
                        if move_mem in t:
                            t.remove(move_mem)
                    # 새 조에 추가
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
                    team_html = f"<div class='team-box'><h3>⛳ {idx+1}조</h3>" + "<br>".join([f"• <b>{m}</b> ({member_db[m]['handicap']})" for m in team]) + "</div>"
                    st.markdown(team_html, unsafe_allow_html=True)
                team_str = ", ".join([f"{m}({member_db[m]['handicap']})" for m in team])
                notice_text += f"🔹 {idx+1}조: {team_str}\n"
            
            notice_text += "-------------------------\n"
            notice_text += "즐거운 라운딩 되세요! 🏌️‍♂️✨"
            
            st.subheader("📱 카카오톡 공지문 복사")
            st.code(notice_text, language="text")
            
            if st.button("💾 이 조편성을 이력에 반영 및 최종 저장", use_container_width=True):
                for team in teams:
                    for i in range(len(team)):
                        for j in range(i + 1, len(team)):
                            m1, m2 = team[i], team[j]
                            if m1 in pair_history and m2 in pair_history[m1]:
                                pair_history[m1][m2] += 1
                                pair_history[m2][m1] += 1
                                
                match_logs.insert(0, {
                    "id": len(match_logs) + 1,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "event_type": e_type,
                    "teams": teams
                })
                save_data(db)
                st.success("🎉 최종 조편성 기록이 성공적으로 저장되었습니다!")

# 3. 🏆 라운드별 성적 & 시상
elif menu == "🏆 라운드별 성적 & 시상":
    st.subheader("🏆 라운드별 성적 입력 및 자동 시상 내역")
    
    if user_info['is_admin']:
        with st.expander("✍️ [운영진 전용] 새 라운딩 성적 입력하기", expanded=False):
            r_title = st.text_input("라운드 명칭", placeholder="예: 8월 필드 월례회 (남서울CC)")
            r_date = st.date_input("라운드 날짜").strftime("%Y-%m-%d")
            r_type = st.selectbox("구분", ["필드 월례회", "스크린 월례회"])
            
            approved_names = [k for k, v in member_db.items() if v.get("status", "approved") == "approved"]
            attendees_round = st.multiselect("참석 회원 선택", approved_names)
            
            st.markdown("---")
            st.markdown("##### 📝 회원별 성적 및 롱기/니어 기록 입력")
            
            player_scores = {}
            for m in attendees_round:
                c1, c2, c3 = st.columns([2, 2, 2])
                with c1:
                    score = st.number_input(f"[{m}] 스코어", min_value=50, max_value=140, value=85, key=f"sc_{m}")
                with c2:
                    long_dist = st.number_input(f"[{m}] 비거리(m)", min_value=0, max_value=350, value=0, key=f"ld_{m}")
                with c3:
                    near_dist = st.number_input(f"[{m}] 니어거리(m)", min_value=0.0, max_value=50.0, value=0.0, step=0.1, key=f"nd_{m}")
                player_scores[m] = {"score": score, "long": long_dist, "near": near_dist}
            
            if st.button("🏆 성적 저장 및 핸디/시상 자동 계산", type="primary", use_container_width=True):
                if attendees_round and r_title:
                    medalist = min(player_scores.items(), key=lambda x: x[1]["score"])
                    
                    valid_longs = {k: v for k, v in player_scores.items() if v["long"] > 0}
                    longist = max(valid_longs.items(), key=lambda x: x[1]["long"]) if valid_longs else None
                    
                    valid_nears = {k: v for k, v in player_scores.items() if v["near"] > 0}
                    nearest = min(valid_nears.items(), key=lambda x: x[1]["near"]) if valid_nears else None
                    
                    round_entry = {
                        "id": len(rounds_data) + 1,
                        "title": r_title,
                        "date": r_date,
                        "type": r_type,
                        "scores": player_scores,
                        "awards": {
                            "medalist": f"{medalist[0]} ({medalist[1]['score']})",
                            "longist": f"{longist[0]} ({longist[1]['long']}m)" if longist else "기록 없음",
                            "nearest": f"{nearest[0]} ({nearest[1]['near']}m)" if nearest else "기록 없음"
                        }
                    }
                    rounds_data.insert(0, round_entry)
                    db["total_events"] = db.get("total_events", 0) + 1
                    
                    for name, data in member_db.items():
                        if name in attendees_round:
                            sc = player_scores[name]["score"]
                            data.setdefault("score_history", []).append(sc)
                            data["rounds_played"] = data.get("rounds_played", 0) + 1
                            
                            recent_scores = data["score_history"][-5:]
                            avg_score = sum(recent_scores) / len(recent_scores)
                            data["handicap"] = round(avg_score - 72)
                            
                        if db["total_events"] > 0:
                            data["attendance"] = round((data.get("rounds_played", 0) / db["total_events"]) * 100)
                    
                    save_data(db)
                    st.success("🎉 성적 저장 완료! 핸디캡, 참석률, 시상 내역이 자동 업데이트 되었습니다.")
                    st.rerun()

    if not rounds_data:
        st.info("등록된 라운드 성적 내역이 없습니다. 라운딩 후 운영진이 성적을 등록하면 이곳에 자동으로 시상 카드가 생성됩니다.")
    else:
        for r in rounds_data:
            with st.expander(f"🚩 {r['date']} | {r['title']} (시상 결과 보기)", expanded=True):
                st.markdown(f"""
                <div class="css-card">
                    <h4 style="color:#A88B58; margin-bottom:10px;">🏆 월례회 공식 시상 내역</h4>
                    <p>🥇 <b>메달리스트 (최저타):</b> {r['awards']['medalist']}</p>
                    <p>💣 <b>롱기스트 (최장타):</b> {r['awards']['longist']}</p>
                    <p>🎯 <b>니어리스트 (최근접):</b> {r['awards']['nearest']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("##### 📊 회원별 성적 상세 표")
                score_table = []
                for p_name, p_info in r['scores'].items():
                    score_table.append({
                        "회원 이름": p_name,
                        "스코어": f"{p_info['score']}",
                        "드라이버 비거리": f"{p_info['long']}m" if p_info['long'] > 0 else "-",
                        "니어 거리에 근접": f"{p_info['near']}m" if p_info['near'] > 0 else "-"
                    })
                st.dataframe(pd.DataFrame(score_table), use_container_width=True)

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
                    if user_info['is_admin']:
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

# 5. 📊 회원 명부 & 승인 관리
elif menu.startswith("📊 회원 명부"):
    st.subheader("📊 Segok Golf Club 회원 명부")
    
    # 승인된 회원만 표에 표시
    df_data = [{
        "이름": k, 
        "자동 산출 핸디캡": v['handicap'], 
        "연간 참석률": f"{v['attendance']}%", 
        "총 라운드 참석": f"{v.get('rounds_played', 0)}회"
    } for k, v in member_db.items() if v.get("status", "approved") == "approved"]
    
    st.dataframe(pd.DataFrame(df_data), use_container_width=True)
    
    # [운영진 전용 신입회원 승인 센터]
    if user_info['is_admin']:
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
                        
    st.divider()
    st.subheader("✏️ 내 비밀번호 설정")
    new_pw_val = st.text_input("새 비밀번호 변경", value=user_info.get('password', '1234'), type="password")
    if st.button("비밀번호 변경 저장"):
        user_info['password'] = new_pw_val
        save_data(db)
        st.success("비밀번호가 업데이트되었습니다.")
