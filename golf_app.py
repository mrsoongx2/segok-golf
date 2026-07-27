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
    
    member_db = {}
    for name in DEFAULT_MEMBERS:
        member_db[name] = {
            "password": "1234",
            "handicap": 20,
            "attendance": 100,
            "rounds_played": 0,
            "score_history": [],
            "is_admin": True if name in ADMIN_MEMBERS else False
        }
    pair_history = {m1: {m2: 0 for m2 in DEFAULT_MEMBERS} for m1 in DEFAULT_MEMBERS}
    feed_posts = [] # 깨끗한 피드로 시작
    finances = []
    rounds_data = [] # 라운드별 시상 및 성적 데이터 저장소
    match_logs = []
    
    return {
        "total_events": 0,
        "member_db": member_db,
        "pair_history": pair_history,
        "feed_posts": feed_posts,
        "finances": finances,
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
finances = db["finances"]
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
            login_name = st.selectbox("회원 이름 선택", ["선택하세요"] + list(member_db.keys()))
            login_pw = st.text_input("비밀번호 입력", type="password")
            
            if st.button("로그인", type="primary", use_container_width=True):
                if login_name in member_db:
                    if login_pw == member_db[login_name].get("password", "1234"):
                        st.session_state.logged_in_user = login_name
                        st.success(f"{login_name}님 환영합니다!")
                        st.rerun()
                    else:
                        st.error("비밀번호가 올바르지 않습니다.")
                else:
                    st.warning("회원 이름을 선택해 주세요.")
                    
        with tab2:
            st.caption("성함과 원하시는 비밀번호, 현재 핸디캡을 입력하시면 즉시 가입됩니다.")
            new_name = st.text_input("신입 회원 이름")
            new_pw = st.text_input("비밀번호 설정", type="password")
            new_hc = st.number_input("초기 핸디캡(타수)", min_value=0, max_value=40, value=20)
            
            if st.button("신규 회원 가입하기", use_container_width=True):
                if new_name and new_pw:
                    if new_name in member_db:
                        st.error("이미 등록되어 있는 이름입니다.")
                    else:
                        member_db[new_name] = {
                            "password": new_pw,
                            "handicap": new_hc,
                            "attendance": 100,
                            "rounds_played": 0,
                            "score_history": [],
                            "is_admin": True if new_name in ADMIN_MEMBERS else False
                        }
                        pair_history[new_name] = {m: 0 for m in member_db.keys()}
                        for m in member_db.keys():
                            pair_history[m][new_name] = 0
                            
                        save_data(db)
                        st.success(f"🎉 {new_name}님 가입을 축하합니다! 바로 로그인해 주세요.")
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
        <span class="badge-hc">핸디캡 {user_info['handicap']}타</span>
        <span class="badge-user">참석률 {user_info['attendance']}%</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()
        
    st.divider()
    menu = st.radio("📱 메뉴 이동", [
        "📸 피드 (Segok Feed)", 
        "🎲 조편성기 (운영진)", 
        "🏆 라운드별 성적 & 시상", 
        "📜 지난 조편성 이력 관리",
        "📊 회원 명부 & 자동 핸디", 
        "💸 회비/정산 내역"
    ])

# 1. 📸 피드 (누구나 자유 업로드)
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
                    "likes": 0,
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

# 2. 🎲 조편성기
elif menu == "🎲 조편성기 (운영진)":
    st.subheader("🎲 중복 방지 & 실력 균등 조편성기")
    if not user_info['is_admin']:
        st.error("⛔ 조편성 기능은 운영진 전용 메뉴입니다.")
    else:
        st.success("👑 **운영자 권한 확인 완료** | 모임 선택 및 조편성을 진행해 주세요.")
        
        c_mode1, c_mode2 = st.columns(2)
        with c_mode1:
            event_type = st.radio("모임 구분", ["필드 월례회 ⛳", "스크린 월례회 🖥️"])
        with c_mode2:
            balance_rule = st.radio("조편성 방식", ["과거 동반 중복 방지 (기본)", "핸디캡 균등 배정 (고수+초보 믹스)"])
        
        selected_attendees = st.multiselect("오늘 참석자 선택", list(member_db.keys()), default=list(member_db.keys())[:16])
        
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

        if st.button("🎲 최적 조편성 실행하기", type="primary", use_container_width=True):
            teams = generate_teams_smart(selected_attendees, pair_history, member_db, balance_rule)
            st.session_state.generated_teams = teams
            st.session_state.current_event_type = event_type
            st.success("🎉 최적의 조편성이 완료되었습니다!")
            
        if 'generated_teams' in st.session_state:
            teams = st.session_state.generated_teams
            e_type = st.session_state.get('current_event_type', event_type)
            cols = st.columns(min(len(teams), 4))
            
            notice_text = f"📢 Segok Golf Club [{e_type}] 조편성 안내\n"
            notice_text += f"🗓️ 참석 인원: 총 {len(selected_attendees)}명 ({len(teams)}개 조)\n"
            notice_text += "-------------------------\n"
            
            for idx, team in enumerate(teams):
                with cols[idx % 4]:
                    team_html = f"<div class='team-box'><h3>⛳ {idx+1}조</h3>" + "<br>".join([f"• <b>{m}</b> ({member_db[m]['handicap']}타)" for m in team]) + "</div>"
                    st.markdown(team_html, unsafe_allow_html=True)
                team_str = ", ".join([f"{m}({member_db[m]['handicap']}타)" for m in team])
                notice_text += f"🔹 {idx+1}조: {team_str}\n"
            
            notice_text += "-------------------------\n"
            notice_text += "즐거운 라운딩 되세요! 🏌️‍♂️✨"
            
            st.subheader("📱 카카오톡 공지문 복사")
            st.code(notice_text, language="text")
            
            if st.button("💾 이 조편성을 이력에 반영 및 저장", use_container_width=True):
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
                st.success("🎉 조편성 기록이 성공적으로 저장되었습니다!")

# 3. 🏆 라운드별 성적 & 시상 (수동 입력 ➔ 자동 핸디/시상 계산)
elif menu == "🏆 라운드별 성적 & 시상":
    st.subheader("🏆 라운드별 성적 입력 및 자동 시상 내역")
    
    # [운영진 수동 성적 입력 창]
    if user_info['is_admin']:
        with st.expander("✍️ [운영진 전용] 새 라운딩 성적 입력하기", expanded=False):
            r_title = st.text_input("라운드 명칭", placeholder="예: 8월 필드 월례회 (남서울CC)")
            r_date = st.date_input("라운드 날짜").strftime("%Y-%m-%d")
            r_type = st.selectbox("구분", ["필드 월례회", "스크린 월례회"])
            
            attendees_round = st.multiselect("참석 회원 선택", list(member_db.keys()))
            
            st.markdown("---")
            st.markdown("##### 📝 회원별 성적 및 롱기/니어 기록 입력")
            
            player_scores = {}
            for m in attendees_round:
                c1, c2, c3 = st.columns([2, 2, 2])
                with c1:
                    score = st.number_input(f"[{m}] 타수", min_value=50, max_value=140, value=85, key=f"sc_{m}")
                with c2:
                    long_dist = st.number_input(f"[{m}] 비거리(m)", min_value=0, max_value=350, value=0, key=f"ld_{m}")
                with c3:
                    near_dist = st.number_input(f"[{m}] 니어거리(m)", min_value=0.0, max_value=50.0, value=0.0, step=0.1, key=f"nd_{m}")
                player_scores[m] = {"score": score, "long": long_dist, "near": near_dist}
            
            if st.button("🏆 성적 저장 및 핸디/시상 자동 계산", type="primary", use_container_width=True):
                if attendees_round and r_title:
                    # 1. 시상자 자동 계산
                    medalist = min(player_scores.items(), key=lambda x: x[1]["score"])
                    
                    # 롱기스트 (비거리 최고)
                    valid_longs = {k: v for k, v in player_scores.items() if v["long"] > 0}
                    longist = max(valid_longs.items(), key=lambda x: x[1]["long"]) if valid_longs else None
                    
                    # 니어리스트 (거리 최저)
                    valid_nears = {k: v for k, v in player_scores.items() if v["near"] > 0}
                    nearest = min(valid_nears.items(), key=lambda x: x[1]["near"]) if valid_nears else None
                    
                    round_entry = {
                        "id": len(rounds_data) + 1,
                        "title": r_title,
                        "date": r_date,
                        "type": r_type,
                        "scores": player_scores,
                        "awards": {
                            "medalist": f"{medalist[0]} ({medalist[1]['score']}타)",
                            "longist": f"{longist[0]} ({longist[1]['long']}m)" if longist else "기록 없음",
                            "nearest": f"{nearest[0]} ({nearest[1]['near']}m)" if nearest else "기록 없음"
                        }
                    }
                    rounds_data.insert(0, round_entry)
                    db["total_events"] = db.get("total_events", 0) + 1
                    
                    # 2. 회원별 핸디캡 & 참석률 자동 업데이트
                    for name, data in member_db.items():
                        if name in attendees_round:
                            sc = player_scores[name]["score"]
                            data.setdefault("score_history", []).append(sc)
                            data["rounds_played"] = data.get("rounds_played", 0) + 1
                            
                            # 최근 성적 기반 핸디캡 자동 계산 (기준 72타 대비 평균 오버파)
                            recent_scores = data["score_history"][-5:] # 최근 최대 5게임 평균
                            avg_score = sum(recent_scores) / len(recent_scores)
                            data["handicap"] = round(avg_score - 72)
                            
                        # 참석률 자동 계산
                        if db["total_events"] > 0:
                            data["attendance"] = round((data.get("rounds_played", 0) / db["total_events"]) * 100)
                    
                    save_data(db)
                    st.success("🎉 성적 저장 완료! 핸디캡, 참석률, 시상 내역이 자동 업데이트 되었습니다.")
                    st.rerun()

    # [라운드별 시상 조회 목록 (클릭시 확장)]
    if not rounds_data:
        st.info("등록된 라운드 성적 내역이 없습니다. 운영진이 라운딩 후 성적을 등록하면 이곳에 자동으로 시상 카드가 생성됩니다.")
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
                        "스코어(타수)": f"{p_info['score']}타",
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
                        team_names = ", ".join([f"{m}({member_db.get(m, {}).get('handicap', '20')}타)" for m in team])
                        st.markdown(f"**⛳ {t_idx+1}조:** {team_names}")
                st.divider()

# 5. 📊 회원 명부 & 자동 핸디
elif menu == "📊 회원 명부 & 자동 핸디":
    st.subheader("📊 Segok Golf Club 회원 명부 (자동 연동)")
    st.caption("💡 핸디캡과 참석률은 라운딩 성적 입력 시 자동으로 실시간 계산 및 갱신됩니다.")
    
    df_data = [{
        "이름": k, 
        "자동 산출 핸디캡": f"{v['handicap']}타", 
        "연간 참석률": f"{v['attendance']}%", 
        "총 라운드 참석": f"{v.get('rounds_played', 0)}회",
        "구분": "운영진" if v['is_admin'] else "회원"
    } for k, v in member_db.items()]
    
    st.dataframe(pd.DataFrame(df_data), use_container_width=True)
    
    st.divider()
    st.subheader("✏️ 내 비밀번호 설정")
    new_pw_val = st.text_input("새 비밀번호 변경", value=user_info.get('password', '1234'), type="password")
    if st.button("비밀번호 변경 저장"):
        user_info['password'] = new_pw_val
        save_data(db)
        st.success("비밀번호가 업데이트되었습니다.")

# 6. 💸 회비/정산 내역
elif menu == "💸 회비/정산 내역":
    st.subheader("💸 투명 회비 및 정산 현황")
    
    if not finances:
        st.info("등록된 정산 내역이 없습니다.")
    else:
        df_fin = pd.DataFrame(finances)
        total_in = df_fin[df_fin['type']=='수입']['amount'].sum()
        total_out = df_fin[df_fin['type']=='지출']['amount'].sum()
        balance = total_in - total_out
        
        col1, col2, col3 = st.columns(3)
        col1.metric("총 수입", f"{total_in:,}원")
        col2.metric("총 지출", f"{total_out:,}원")
        col3.metric("현재 잔액", f"{balance:,}원")
        
        st.divider()
        st.dataframe(df_fin, use_container_width=True)
    
    if user_info['is_admin']:
        with st.expander("✍️ [운영진] 정산 내역 추가 입력"):
            f_date = st.date_input("날짜").strftime("%Y-%m-%d")
            f_type = st.selectbox("구분", ["수입", "지출"])
            f_cat = st.text_input("항목", placeholder="예: 월례회비 / 그린피 정산 / 음료 지원")
            f_desc = st.text_input("상세 내용")
            f_amt = st.number_input("금액(원)", min_value=0, step=10000)
            if st.button("내역 저장"):
                finances.insert(0, {"date": f_date, "type": f_type, "category": f_cat, "desc": f_desc, "amount": f_amt})
                save_data(db)
                st.success("정산 내역이 기록되었습니다!")
                st.rerun()
