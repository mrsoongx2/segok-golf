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

# 운영진 4명 지정: 이승환, 김성모, 김경수, 김지윤
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
            "password": "1234", # 기본 초기 비밀번호
            "handicap": random.randint(12, 28),
            "attendance": random.randint(70, 100),
            "is_admin": True if name in ADMIN_MEMBERS else False
        }
    pair_history = {m1: {m2: 0 for m2 in DEFAULT_MEMBERS} for m1 in DEFAULT_MEMBERS}
    feed_posts = [
        {
            "id": 1,
            "author": "이승환",
            "date": "2026-07-26 18:30",
            "content": "⛳ 오늘 Segok Golf Club 라운딩 날씨 완벽했네요! 다들 수고 많으셨습니다.",
            "likes": 12,
            "comments": [{"author": "김동숙", "text": "클래식하고 멋진 명문 모임입니다!"}]
        }
    ]
    finances = [
        {"date": "2026-07-20", "type": "수입", "category": "월례회비", "desc": "7월 필드 월례회 참가비 (16명)", "amount": 800000},
        {"date": "2026-07-21", "type": "지출", "category": "골프장 정산", "desc": "그린피/카트비 단체 정산", "amount": 640000}
    ]
    awards = [
        {"month": "2026년 7월", "medalist": "이승환 (75타)", "winner": "김동숙 (Net 71타)", "longist": "나승환 (260m)", "nearest": "김현태 (1.2m)"}
    ]
    match_logs = [
        {
            "id": 1,
            "date": "2026-07-20 09:00",
            "event_type": "필드 월례회 ⛳",
            "teams": [
                ["이승환", "김성모", "김동숙", "나승환"],
                ["김경수", "김지윤", "김현태", "최승락"]
            ]
        }
    ]
    return {
        "member_db": member_db,
        "pair_history": pair_history,
        "feed_posts": feed_posts,
        "finances": finances,
        "awards": awards,
        "match_logs": match_logs
    }

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'db_data' not in st.session_state:
    st.session_state.db_data = load_data()

member_db = st.session_state.db_data["member_db"]
pair_history = st.session_state.db_data["pair_history"]
feed_posts = st.session_state.db_data["feed_posts"]
finances = st.session_state.db_data["finances"]
awards = st.session_state.db_data["awards"]
match_logs = st.session_state.db_data.setdefault("match_logs", [])

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

# --- LOGIN & SIGNUP SYSTEM ---
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
            new_hc = st.number_input("현재 핸디캡(타수)", min_value=0, max_value=40, value=20)
            
            if st.button("신규 회원 가입하기", use_container_width=True):
                if new_name and new_pw:
                    if new_name in member_db:
                        st.error("이미 등록되어 있는 이름입니다.")
                    else:
                        member_db[new_name] = {
                            "password": new_pw,
                            "handicap": new_hc,
                            "attendance": 100,
                            "is_admin": True if new_name in ADMIN_MEMBERS else False
                        }
                        pair_history[new_name] = {m: 0 for m in member_db.keys()}
                        for m in member_db.keys():
                            pair_history[m][new_name] = 0
                            
                        save_data(st.session_state.db_data)
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
        "📜 지난 조편성 이력 관리",
        "📊 회원 명부 & 핸디/참석률", 
        "💸 회비/정산 내역", 
        "🏆 월간 시상 & 명예의 전당",
        "⛳ 매너 & 규칙 안내"
    ])

# 1. 피드
if menu == "📸 피드 (Segok Feed)":
    st.subheader("📸 Segok Member Feed")
    with st.expander("✍️ 새 라운딩 사진/소식 올리기"):
        post_text = st.text_area("내용", placeholder="오늘의 라운딩 일상을 나눠보세요...")
        uploaded_img = st.file_uploader("사진 첨부", type=["jpg", "png", "jpeg"])
        if st.button("업로드", type="primary"):
            if post_text or uploaded_img:
                feed_posts.insert(0, {
                    "id": len(feed_posts) + 1,
                    "author": current_user,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "content": post_text,
                    "likes": 0,
                    "comments": []
                })
                save_data(st.session_state.db_data)
                st.rerun()

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
                save_data(st.session_state.db_data)
                st.rerun()
        with st.expander(f"💬 댓글 ({len(post['comments'])})"):
            for c in post['comments']:
                st.write(f"**{c['author']}**: {c['text']}")
            new_c = st.text_input("댓글 쓰기", key=f"nc_{post['id']}")
            if st.button("등록", key=f"btn_c_{post['id']}") and new_c:
                post['comments'].append({"author": current_user, "text": new_c})
                save_data(st.session_state.db_data)
                st.rerun()

# 2. 조편성기
elif menu == "🎲 조편성기 (운영진)":
    st.subheader("🎲 중복 방지 & 실력 균등 조편성기")
    if not user_info['is_admin']:
        st.error("⛔ 조편성 기능은 운영진(이승환, 김성모, 김경수, 김지윤) 전용 메뉴입니다.")
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
            
            if st.button("💾 이 조편성을 이력에 영구 반영하기 (데이터 파일 누적 저장)", use_container_width=True):
                for team in teams:
                    for i in range(len(team)):
                        for j in range(i + 1, len(team)):
                            m1, m2 = team[i], team[j]
                            if m1 in pair_history and m2 in pair_history[m1]:
                                pair_history[m1][m2] += 1
                                pair_history[m2][m1] += 1
                                
                new_log_id = len(match_logs) + 1
                match_logs.insert(0, {
                    "id": new_log_id,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "event_type": e_type,
                    "teams": teams
                })
                save_data(st.session_state.db_data)
                st.success("🎉 이번 조편성 기록 및 과거 이력이 `club_data.json` 파일에 성공적으로 영구 저장되었습니다!")

# 3. 지난 조편성 이력 관리
elif menu == "📜 지난 조편성 이력 관리":
    st.subheader("📜 Segok Golf Club 지난 라운딩/스크린 조편성 이력")
    st.info("💡 과거 진행했던 조편성 이력을 조회하고, 불필요한 이력은 삭제/관리할 수 있습니다.")
    
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
                            save_data(st.session_state.db_data)
                            st.success("해당 조편성 이력이 삭제되었습니다.")
                            st.rerun()
                
                cols = st.columns(min(len(log['teams']), 4))
                for t_idx, team in enumerate(log['teams']):
                    with cols[t_idx % 4]:
                        team_names = ", ".join([f"{m}({member_db.get(m, {}).get('handicap', '20')}타)" for m in team])
                        st.markdown(f"**⛳ {t_idx+1}조:** {team_names}")
                st.divider()

# 4. 회원 명부
elif menu == "📊 회원 명부 & 핸디/참석률":
    st.subheader("📊 Segok Golf Club 회원 명부")
    df_data = [{"이름": k, "핸디캡": f"{v['handicap']}타", "참석률": f"{v['attendance']}%", "직책": "운영진" if v['is_admin'] else "회원"} for k, v in member_db.items()]
    st.dataframe(pd.DataFrame(df_data), use_container_width=True)
    
    st.divider()
    st.subheader("✏️ 내 비밀번호 및 핸디캡 변경")
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        new_hc_val = st.number_input("내 핸디캡 수정", min_value=0, max_value=40, value=user_info['handicap'])
    with c_p2:
        new_pw_val = st.text_input("새 비밀번호 설정", value=user_info.get('password', '1234'), type="password")
        
    if st.button("내 정보 저장하기"):
        user_info['handicap'] = new_hc_val
        user_info['password'] = new_pw_val
        save_data(st.session_state.db_data)
        st.success("내 정보가 업데이트되었습니다.")
        st.rerun()

    # --- 운영진 전용 회원 핸디캡 및 참석률 수정 기능 ---
    if user_info['is_admin']:
        st.divider()
        st.subheader("👑 [운영진 전용] 통합 회원 정보 관리 Center")
        st.info("💡 이승환 님(운영진)은 회원별 핸디캡(타수)과 연간 참석률(%)을 한 곳에서 즉시 수정할 수 있습니다.")
        
        admin_c1, admin_c2, admin_c3 = st.columns(3)
        with admin_c1:
            target_member = st.selectbox("수정할 회원 선택", list(member_db.keys()))
        with admin_c2:
            new_target_hc = st.number_input(f"[{target_member}] 핸디캡(타수)", min_value=0, max_value=40, value=member_db[target_member]['handicap'])
        with admin_c3:
            new_target_att = st.number_input(f"[{target_member}] 연간 참석률(%)", min_value=0, max_value=100, value=member_db[target_member].get('attendance', 100))
            
        if st.button(f"👑 {target_member} 회원 정보 저장하기", type="primary", use_container_width=True):
            member_db[target_member]['handicap'] = new_target_hc
            member_db[target_member]['attendance'] = new_target_att
            save_data(st.session_state.db_data)
            st.success(f"👑 {target_member}님의 핸디캡({new_target_hc}타) 및 참석률({new_target_att}%) 변경 완료!")
            st.rerun()

# 5. 회비/정산 내역
elif menu == "💸 회비/정산 내역":
    st.subheader("💸 투명 회비 및 정산 현황")
    
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
                save_data(st.session_state.db_data)
                st.success("정산 내역이 기록되었습니다!")
                st.rerun()

# 6. 월간 시상식
elif menu == "🏆 월간 시상 & 명예의 전당":
    st.subheader("🏆 Segok Golf Club 명예의 전당")
    for aw in awards:
        st.markdown(f"""
        <div class="css-card">
            <h3 style="color:#A88B58; font-family:'Playfair Display'; margin-bottom:10px;">🥇 {aw['month']} 월례회 시상 결과</h3>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                <div><b>🥇 메달리스트 (최저타):</b> {aw['medalist']}</div>
                <div><b>🎯 신페리오 우승:</b> {aw['winner']}</div>
                <div><b>💣 롱기스트 (최장타):</b> {aw['longist']}</div>
                <div><b>🎯 니어리스트 (최근접):</b> {aw['nearest']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 7. 매너 & 규칙
elif menu == "⛳ 매너 & 규칙 안내":
    st.subheader("⛳ Segok Golf Club 라운딩 에티켓 & 수칙")
    st.markdown("""
    <div class="css-card">
        <h4>📌 모임 참석 및 라운드 매너</h4>
        <ul>
            <li><b>티오프 30분 전 도착:</b> 골프장 클럽하우스 도착 및 옷 갈아입기 완료</li>
            <li><b>컨시드(OK) 기준:</b> 퍼터 그립 연결선 이내 (상대방 배려)</li>
            <li><b>신속한 진행 (Pace of Play):</b> 다음 샷 준비는 자기 차례 전에 미리 하기</li>
            <li><b>월례회 규칙:</b> 무단 3개월 불참 시 회원 자격 재검토</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
