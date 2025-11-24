import streamlit as st

# 1. 로그인 상태 확인 함수
def check_password():
    """비밀번호 확인 및 로그인 상태 관리"""
    # 이미 로그인 성공한 상태라면 True 반환
    if st.session_state.get('password_correct', False):
        return True

    # 로그인 화면 UI
    st.title("🔒 퀀트 대시보드 로그인")
    
    # ID/PW 입력 폼 생성
    with st.form("credentials"):
        username = st.text_input("아이디 (ID)", key="username")
        password = st.text_input("비밀번호 (Password)", type="password", key="password")
        submit_btn = st.form_submit_button("로그인", type="primary")

    # 로그인 버튼 클릭 시 로직
    if submit_btn:
        if username in st.secrets["passwords"] and password == st.secrets["passwords"][username]:
            st.session_state['password_correct'] = True
            st.rerun()  # 화면을 새로고침하여 메인 앱 로드
        else:
            st.error("😕 아이디 또는 비밀번호가 올바르지 않습니다.")
            
    return False

# 2. 메인 앱 실행 로직
if not check_password():
    st.stop()  # 로그인이 안 되면 여기서 코드 실행을 멈춤 (아래 내용 안 보임)

# ------------------------------------------------------------------
# ▼▼▼ 여기부터 기존 대시보드 코드가 시작되면 됩니다 ▼▼▼
# ------------------------------------------------------------------

st.title("📈 퀀트 3콤보 분석 대시보드")
st.write("로그인에 성공했습니다! 이제 데이터를 볼 수 있습니다.")



# ============================================================
# FRED API 퀀트 3콤보 분석 대시보드 (Streamlit Version)
# Net Liquidity / Dollar Index / HY Spread vs BTC/NASDAQ/S&P500
# ============================================================

import streamlit as st
from fredapi import Fred
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(
    page_title="퀀트 3콤보 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 사이드바 설정
# ============================================================
st.sidebar.title("⚙️ 분석 설정")
st.sidebar.markdown("---")

# API 키 (Streamlit Secrets에서 로드)
try:
    FRED_API_KEY = st.secrets["FRED_API_KEY"]
except Exception as e:
    st.error("⚠️ API 키를 찾을 수 없습니다. .streamlit/secrets.toml 파일을 확인하세요.")
    st.stop()

# 분석 기간 선택
period_options = {
    "최근 1년": 365,
    "최근 2년": 365*2,
    "최근 3년": 365*3,
    "최근 5년": 365*5
}
selected_period = st.sidebar.selectbox(
    "📅 분석 기간",
    list(period_options.keys()),
    index=2  # 기본값: 3년
)
days = period_options[selected_period]

# 롤링 윈도우 설정
window = st.sidebar.slider(
    "📈 상관계수 롤링 윈도우 (일)",
    min_value=30,
    max_value=180,
    value=90,
    step=10
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 대시보드 정보")
st.sidebar.info("""
**분석 지표:**
- Net Liquidity (Fed 유동성)
- Dollar Index (달러 강도)
- HY Spread (신용 스프레드)
- Bitcoin, NASDAQ, S&P 500

**데이터 출처:** FRED API
""")

# ============================================================
# 메인 타이틀
# ============================================================
st.title("📊 퀀트 3콤보 분석 대시보드")
st.markdown("""
**Fed 유동성, 달러 인덱스, HY Spread를 통한 리스크 자산 분석**  
실시간 FRED 데이터 기반 인터랙티브 대시보드
""")
st.markdown("---")

# ============================================================
# 데이터 로딩 함수
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def load_data(api_key, days):
    """FRED API에서 데이터 로드"""
    try:
        fred = Fred(api_key=api_key)
        start_date = datetime.now() - timedelta(days=days)
        
        # Net Liquidity 구성 요소
        walcl = fred.get_series('WALCL', observation_start=start_date)
        tga = fred.get_series('WTREGEN', observation_start=start_date)
        rrp = fred.get_series('RRPONTSYD', observation_start=start_date)
        
        # 달러 인덱스
        dxy = fred.get_series('DTWEXAFEGS', observation_start=start_date)
        
        # High Yield Spread
        hy_spread = fred.get_series('BAMLH0A0HYM2', observation_start=start_date)
        
        # 자산 가격
        btc = fred.get_series('CBBTCUSD', observation_start=start_date)
        nasdaq = fred.get_series('NASDAQCOM', observation_start=start_date)
        sp500 = fred.get_series('SP500', observation_start=start_date)
        
        return {
            'walcl': walcl, 'tga': tga, 'rrp': rrp,
            'dxy': dxy, 'hy_spread': hy_spread,
            'btc': btc, 'nasdaq': nasdaq, 'sp500': sp500
        }
    except Exception as e:
        st.error(f"❌ 데이터 로딩 실패: {str(e)}")
        return None

# ============================================================
# 데이터 처리 함수
# ============================================================
def process_data(raw_data):
    """Net Liquidity 계산 및 데이터 통합"""
    try:
        # Net Liquidity 계산
        df_liq = pd.DataFrame({
            'WALCL_Mn': raw_data['walcl'],
            'TGA_Mn': raw_data['tga'],
            'RRP_Bn': raw_data['rrp']
        })
        
        # 단위 통일
        df_liq['RRP_Mn'] = df_liq['RRP_Bn'] * 1000
        df_liq = df_liq.fillna(method='ffill').dropna()
        
        # Net Liquidity
        df_liq['NetLiquidity'] = (
            df_liq['WALCL_Mn'] - df_liq['TGA_Mn'] - df_liq['RRP_Mn']
        )
        
        # 전체 데이터 통합
        df_all = pd.DataFrame({
            'NetLiq': df_liq['NetLiquidity'],
            'DXY': raw_data['dxy'],
            'HYSpread': raw_data['hy_spread'],
            'BTC': raw_data['btc'],
            'NASDAQ': raw_data['nasdaq'],
            'SP500': raw_data['sp500']
        })
        
        df_all = df_all.fillna(method='ffill').dropna()
        return df_all
        
    except Exception as e:
        st.error(f"❌ 데이터 처리 실패: {str(e)}")
        return None

def zscore(series):
    """Z-score 정규화"""
    return (series - series.mean()) / series.std()

# ============================================================
# 데이터 로드
# ============================================================
with st.spinner("🔄 FRED 데이터 다운로드 중..."):
    raw_data = load_data(FRED_API_KEY, days)

if raw_data is None:
    st.error("데이터를 불러올 수 없습니다. API 키와 네트워크 연결을 확인하세요.")
    st.stop()

df_recent = process_data(raw_data)

if df_recent is None:
    st.error("데이터 처리 중 오류가 발생했습니다.")
    st.stop()

# 데이터 로드 성공 메시지
st.success(f"✅ 데이터 로드 완료: {df_recent.index[0].date()} ~ {df_recent.index[-1].date()} ({len(df_recent)}개 포인트)")

# ============================================================
# 최신 지표 요약 (상단 메트릭)
# ============================================================
latest = df_recent.iloc[-1]
netliq_60d = df_recent['NetLiq'].pct_change(periods=60).iloc[-1] * 100

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Net Liquidity",
        f"${latest['NetLiq']/1e6:.2f}T",
        f"{netliq_60d:+.2f}% (60일)"
    )

with col2:
    btc_change = df_recent['BTC'].pct_change(periods=30).iloc[-1] * 100
    st.metric(
        "₿ Bitcoin",
        f"${latest['BTC']:,.0f}",
        f"{btc_change:+.2f}% (30일)"
    )

with col3:
    dxy_change = df_recent['DXY'].pct_change(periods=30).iloc[-1] * 100
    st.metric(
        "💵 Dollar Index",
        f"{latest['DXY']:.2f}",
        f"{dxy_change:+.2f}% (30일)"
    )

with col4:
    hy_status = "🚨 위험" if latest['HYSpread'] > 5 else "✅ 정상"
    st.metric(
        "⚠️ HY Spread",
        f"{latest['HYSpread']:.2f}%",
        hy_status
    )

st.markdown("---")

# ============================================================
# 탭 구성
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 콤보 1: Net Liquidity",
    "💵 콤보 2: Dollar Index",
    "⚠️ 콤보 3: HY Spread",
    "🎯 종합 대시보드",
    "📊 트레이딩 시그널"
])

# ============================================================
# TAB 1: Net Liquidity 분석
# ============================================================
with tab1:
    st.header("📈 콤보 1: Net Liquidity 분석")
    st.markdown("**Fed 총자산 - 재무부 계좌 - 역RP = Net Liquidity**")
    
    # Z-score 정규화
    df_z1 = df_recent[['NetLiq', 'BTC', 'NASDAQ']].apply(zscore)
    
    # 롤링 상관계수
    ret = df_recent[['NetLiq', 'BTC', 'NASDAQ']].pct_change().dropna()
    corr_btc = ret['NetLiq'].rolling(window).corr(ret['BTC'])
    corr_nasdaq = ret['NetLiq'].rolling(window).corr(ret['NASDAQ'])
    
    # Net Liquidity 변화율
    netliq_change = df_recent['NetLiq'].pct_change(periods=60) * 100
    
    # 서브플롯 생성
    fig1 = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            'Net Liquidity vs BTC/NASDAQ (Z-score)',
            f'Net Liquidity 상관계수 ({window}일 롤링)',
            'Net Liquidity 60일 변화율 (유동성 확장/축소)'
        ),
        vertical_spacing=0.08,
        row_heights=[0.35, 0.3, 0.35]
    )
    
    # Z-score 오버레이
    fig1.add_trace(
        go.Scatter(x=df_z1.index, y=df_z1['NetLiq'],
                   name='Net Liquidity', line=dict(color='#2E86AB', width=2.5)),
        row=1, col=1
    )
    fig1.add_trace(
        go.Scatter(x=df_z1.index, y=df_z1['BTC'],
                   name='Bitcoin', line=dict(color='#F77F00', width=2.5)),
        row=1, col=1
    )
    fig1.add_trace(
        go.Scatter(x=df_z1.index, y=df_z1['NASDAQ'],
                   name='NASDAQ', line=dict(color='#06A77D', width=2.5)),
        row=1, col=1
    )
    fig1.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1)
    
    # 롤링 상관계수
    fig1.add_trace(
        go.Scatter(x=corr_btc.index, y=corr_btc,
                   name='Corr(NetLiq, BTC)',
                   line=dict(color='#F77F00', width=2.5),
                   fill='tozeroy', fillcolor='rgba(247, 127, 0, 0.2)'),
        row=2, col=1
    )
    fig1.add_trace(
        go.Scatter(x=corr_nasdaq.index, y=corr_nasdaq,
                   name='Corr(NetLiq, NASDAQ)',
                   line=dict(color='#06A77D', width=2.5),
                   fill='tozeroy', fillcolor='rgba(6, 167, 125, 0.2)'),
        row=2, col=1
    )
    fig1.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)
    
    # Net Liquidity 변화율
    expansion = netliq_change[netliq_change > 0]
    fig1.add_trace(
        go.Scatter(x=expansion.index, y=expansion,
                   name='확장 구간 🟢',
                   line=dict(color='#06A77D', width=0),
                   fill='tozeroy', fillcolor='rgba(6, 167, 125, 0.4)'),
        row=3, col=1
    )
    
    contraction = netliq_change[netliq_change <= 0]
    fig1.add_trace(
        go.Scatter(x=contraction.index, y=contraction,
                   name='축소 구간 🔴',
                   line=dict(color='#D62828', width=0),
                   fill='tozeroy', fillcolor='rgba(214, 40, 40, 0.4)'),
        row=3, col=1
    )
    
    fig1.add_trace(
        go.Scatter(x=netliq_change.index, y=netliq_change,
                   name='변화율', line=dict(color='black', width=2),
                   showlegend=False),
        row=3, col=1
    )
    fig1.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=3, col=1)
    
    fig1.update_layout(
        height=1200,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )
    
    fig1.update_yaxes(title_text="Z-score", row=1, col=1)
    fig1.update_yaxes(title_text="Correlation", row=2, col=1)
    fig1.update_yaxes(title_text="변화율 (%)", row=3, col=1)
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 인사이트
    st.markdown("### 📌 분석 인사이트")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"""
        **최근 상관계수**
        - NetLiq ↔ BTC: {corr_btc.iloc[-1]:.3f}
        - NetLiq ↔ NASDAQ: {corr_nasdaq.iloc[-1]:.3f}
        """)
    with col2:
        signal = "🟢 확장 (리스크 온)" if netliq_60d > 0 else "🔴 축소 (리스크 오프)"
        st.warning(f"""
        **현재 유동성 상태**
        - 60일 변화: {netliq_60d:+.2f}%
        - 시그널: {signal}
        """)

# ============================================================
# TAB 2: Dollar Index vs BTC
# ============================================================
with tab2:
    st.header("💵 콤보 2: Dollar Index vs Bitcoin 분석")
    st.markdown("**달러 강세 = 비트코인 약세 (역상관 관계)**")
    
    # DXY 반전 vs BTC
    df_z2 = pd.DataFrame({
        'DXY_Inverted': zscore(-df_recent['DXY']),
        'BTC': zscore(df_recent['BTC'])
    })
    
    # 롤링 상관계수
    ret2 = df_recent[['DXY', 'BTC']].pct_change().dropna()
    corr_dxy_btc = ret2['DXY'].rolling(window).corr(ret2['BTC'])
    
    fig2 = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            'Dollar Index (반전) vs BTC (Z-score)',
            f'Dollar Index vs BTC 상관계수 ({window}일 롤링)'
        ),
        vertical_spacing=0.12,
        row_heights=[0.5, 0.5]
    )
    
    # DXY 반전 vs BTC
    fig2.add_trace(
        go.Scatter(x=df_z2.index, y=df_z2['DXY_Inverted'],
                   name='Dollar Index (반전)',
                   line=dict(color='#D62828', width=2.5)),
        row=1, col=1
    )
    fig2.add_trace(
        go.Scatter(x=df_z2.index, y=df_z2['BTC'],
                   name='Bitcoin',
                   line=dict(color='#F77F00', width=2.5)),
        row=1, col=1
    )
    fig2.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1)
    
    # 롤링 상관계수
    fig2.add_trace(
        go.Scatter(x=corr_dxy_btc.index, y=corr_dxy_btc,
                   name='Correlation',
                   line=dict(color='#9D4EDD', width=2.5),
                   fill='tozeroy', fillcolor='rgba(157, 78, 221, 0.3)'),
        row=2, col=1
    )
    fig2.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)
    
    fig2.update_layout(
        height=900,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )
    
    fig2.update_yaxes(title_text="Z-score", row=1, col=1)
    fig2.update_yaxes(title_text="Correlation", row=2, col=1)
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # 인사이트
    st.markdown("### 📌 분석 인사이트")
    if corr_dxy_btc.iloc[-1] < -0.5:
        st.success(f"""
        ✅ **강한 역상관 감지** (상관계수: {corr_dxy_btc.iloc[-1]:.3f})
        - 달러 약세 시 비트코인 강세 예상
        - DXY 하락 구간에서 BTC 매수 기회
        """)
    else:
        st.info(f"""
        ⏸️ **역상관 약화** (상관계수: {corr_dxy_btc.iloc[-1]:.3f})
        - 달러와 비트코인의 연관성 감소
        - 다른 요인이 가격에 더 큰 영향
        """)

# ============================================================
# TAB 3: HY Spread 분석
# ============================================================
with tab3:
    st.header("⚠️ 콤보 3: High Yield Spread 분석")
    st.markdown("**HY Spread 상승 = 신용 위험 증가 = 주식 시장 위험**")
    
    # 롤링 상관계수
    ret3 = df_recent[['HYSpread', 'SP500']].pct_change().dropna()
    corr_hy_sp = ret3['HYSpread'].rolling(window).corr(ret3['SP500'])
    
    # Divergence 감지
    sp_ret = df_recent['SP500'].pct_change(periods=20)
    hy_change = df_recent['HYSpread'].diff(periods=20)
    divergence = (sp_ret > 0) & (hy_change > 0)
    
    fig3 = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            'High Yield Spread vs S&P 500',
            f'HY Spread vs S&P 500 상관계수 ({window}일 롤링)',
            'Divergence 감지: S&P 상승 + HY Spread 상승 (매도 신호)'
        ),
        specs=[[{"secondary_y": True}],
               [{"secondary_y": False}],
               [{"secondary_y": False}]],
        vertical_spacing=0.08,
        row_heights=[0.35, 0.3, 0.35]
    )
    
    # HY Spread vs S&P 500 (이중 축)
    fig3.add_trace(
        go.Scatter(x=df_recent.index, y=df_recent['SP500'],
                   name='S&P 500',
                   line=dict(color='#2E86AB', width=2.5)),
        row=1, col=1, secondary_y=False
    )
    fig3.add_trace(
        go.Scatter(x=df_recent.index, y=df_recent['HYSpread'],
                   name='HY Spread',
                   line=dict(color='#D62828', width=2.5)),
        row=1, col=1, secondary_y=True
    )
    
    # 위험 구간
    danger_zone = df_recent[df_recent['HYSpread'] > 5.0]
    if len(danger_zone) > 0:
        fig3.add_hline(y=5.0, line_dash="dash", line_color="darkred",
                       line_width=2.5, opacity=0.8,
                       annotation_text="위기 임계점 (5%)",
                       annotation_position="right",
                       row=1, col=1, secondary_y=True)
    
    # 롤링 상관계수
    fig3.add_trace(
        go.Scatter(x=corr_hy_sp.index, y=corr_hy_sp,
                   name='Correlation',
                   line=dict(color='#A4133C', width=2.5),
                   fill='tozeroy', fillcolor='rgba(164, 19, 60, 0.3)'),
        row=2, col=1
    )
    fig3.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)
    
    # Divergence 감지
    fig3.add_trace(
        go.Scatter(x=df_recent.index, y=df_recent['SP500'],
                   name='S&P 500',
                   line=dict(color='#2E86AB', width=2), opacity=0.6),
        row=3, col=1
    )
    fig3.add_trace(
        go.Scatter(x=df_recent[divergence].index,
                   y=df_recent.loc[divergence, 'SP500'],
                   name='Divergence 경고 ⚠️',
                   mode='markers',
                   marker=dict(color='red', size=10, symbol='diamond')),
        row=3, col=1
    )
    
    fig3.update_layout(
        height=1200,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )
    
    fig3.update_yaxes(title_text="S&P 500", row=1, col=1, secondary_y=False)
    fig3.update_yaxes(title_text="HY Spread (%)", row=1, col=1, secondary_y=True)
    fig3.update_yaxes(title_text="Correlation", row=2, col=1)
    fig3.update_yaxes(title_text="S&P 500", row=3, col=1)
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # 인사이트
    st.markdown("### 📌 분석 인사이트")
    recent_divergence = divergence.tail(5).sum()
    
    col1, col2 = st.columns(2)
    with col1:
        if latest['HYSpread'] > 5.0:
            st.error(f"""
            🚨 **위기 임계점 초과**
            - 현재 HY Spread: {latest['HYSpread']:.2f}%
            - 신용 시장 경색 신호
            - 주식 매도/방어 전략 권장
            """)
        elif latest['HYSpread'] > 4.0:
            st.warning(f"""
            ⚠️ **경계 구간**
            - 현재 HY Spread: {latest['HYSpread']:.2f}%
            - 주의 필요, 포지션 축소 고려
            """)
        else:
            st.success(f"""
            ✅ **정상 구간**
            - 현재 HY Spread: {latest['HYSpread']:.2f}%
            - 신용 시장 안정
            """)
    
    with col2:
        if recent_divergence > 0:
            st.warning(f"""
            ⚠️ **Divergence 경고**
            - 최근 5일 중 {recent_divergence}일 발생
            - S&P 상승 + HY Spread 상승
            - 허위 랠리 가능성, 매도 신호
            """)
        else:
            st.info("✅ 최근 Divergence 없음")

# ============================================================
# TAB 4: 종합 대시보드
# ============================================================
with tab4:
    st.header("🎯 종합 대시보드")
    
    # 상관계수 매트릭스
    corr_matrix = df_recent[['NetLiq', 'DXY', 'HYSpread', 'BTC', 'NASDAQ', 'SP500']].corr()
    
    fig_dashboard = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Net Liquidity + BTC/NASDAQ (Z-score)',
            '상관계수 히트맵',
            'Dollar Index (반전) vs BTC',
            'High Yield Spread vs S&P 500'
        ),
        specs=[
            [{"type": "xy"}, {"type": "heatmap"}],
            [{"type": "xy"}, {"type": "xy", "secondary_y": True}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )
    
    # Net Liquidity + BTC/NASDAQ
    df_z_all = df_recent[['NetLiq', 'BTC', 'NASDAQ']].apply(zscore)
    fig_dashboard.add_trace(
        go.Scatter(x=df_z_all.index, y=df_z_all['NetLiq'],
                   name='Net Liquidity', line=dict(color='#2E86AB', width=2)),
        row=1, col=1
    )
    fig_dashboard.add_trace(
        go.Scatter(x=df_z_all.index, y=df_z_all['BTC'],
                   name='Bitcoin', line=dict(color='#F77F00', width=2)),
        row=1, col=1
    )
    fig_dashboard.add_trace(
        go.Scatter(x=df_z_all.index, y=df_z_all['NASDAQ'],
                   name='NASDAQ', line=dict(color='#06A77D', width=2)),
        row=1, col=1
    )
    fig_dashboard.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1)
    
    # 상관계수 히트맵
    fig_dashboard.add_trace(
        go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdYlGn',
            zmid=0,
            zmin=-1,
            zmax=1,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ),
        row=1, col=2
    )
    
    # Dollar Index (반전) vs BTC
    fig_dashboard.add_trace(
        go.Scatter(x=df_z2.index, y=df_z2['DXY_Inverted'],
                   name='DXY (반전)', line=dict(color='#D62828', width=2)),
        row=2, col=1
    )
    fig_dashboard.add_trace(
        go.Scatter(x=df_z2.index, y=df_z2['BTC'],
                   name='BTC', line=dict(color='#F77F00', width=2)),
        row=2, col=1
    )
    fig_dashboard.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)
    
    # HY Spread vs S&P 500
    fig_dashboard.add_trace(
        go.Scatter(x=df_recent.index, y=df_recent['SP500'],
                   name='S&P 500', line=dict(color='#2E86AB', width=2)),
        row=2, col=2, secondary_y=False
    )
    fig_dashboard.add_trace(
        go.Scatter(x=df_recent.index, y=df_recent['HYSpread'],
                   name='HY Spread', line=dict(color='#D62828', width=2)),
        row=2, col=2, secondary_y=True
    )
    
    fig_dashboard.update_layout(
        height=1000,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )
    
    fig_dashboard.update_yaxes(title_text="Z-score", row=1, col=1)
    fig_dashboard.update_yaxes(title_text="Z-score", row=2, col=1)
    fig_dashboard.update_yaxes(title_text="S&P 500", row=2, col=2, secondary_y=False)
    fig_dashboard.update_yaxes(title_text="HY Spread (%)", row=2, col=2, secondary_y=True)
    
    st.plotly_chart(fig_dashboard, use_container_width=True)
    
    # 상관계수 테이블
    st.markdown("### 📊 상관계수 매트릭스")
    st.dataframe(corr_matrix.round(3), use_container_width=True)

# ============================================================
# TAB 5: 트레이딩 시그널
# ============================================================
with tab5:
    st.header("🎯 현재 트레이딩 시그널")
    st.markdown("**퀀트 3콤보 기반 매매 신호**")
    
    st.markdown("---")
    
    # 시그널 1: Net Liquidity
    st.subheader("📈 시그널 1: Net Liquidity")
    if netliq_60d > 2:
        st.success(f"""
        ✅ **Net Liquidity 강한 확장** (+{netliq_60d:.2f}%)
        - Fed 유동성 공급 증가
        - 리스크 자산 상승 환경
        - **추천**: BTC/NASDAQ 매수 고려
        """)
    elif netliq_60d < -2:
        st.error(f"""
        ⚠️ **Net Liquidity 강한 축소** ({netliq_60d:.2f}%)
        - Fed 유동성 회수 진행
        - 리스크 자산 하락 압력
        - **추천**: 리스크 자산 매도/경계
        """)
    else:
        st.info(f"""
        ⏸️ **Net Liquidity 중립 구간** ({netliq_60d:+.2f}%)
        - 유동성 변화 미미
        - 다른 요인 주시 필요
        """)
    
    st.markdown("---")
    
    # 시그널 2: DXY vs BTC
    st.subheader("💵 시그널 2: Dollar Index vs Bitcoin")
    if corr_dxy_btc.iloc[-1] < -0.5:
        st.success(f"""
        ✅ **DXY-BTC 강한 역상관** (상관계수: {corr_dxy_btc.iloc[-1]:.3f})
        - 달러 약세 = 비트코인 강세
        - **추천**: DXY 하락 시 BTC 매수 기회
        """)
    elif corr_dxy_btc.iloc[-1] > 0:
        st.warning(f"""
        ⚠️ **DXY-BTC 양의 상관** (상관계수: {corr_dxy_btc.iloc[-1]:.3f})
        - 비정상적 동행
        - 리스크 회피 모드 가능성
        """)
    else:
        st.info(f"""
        ⏸️ **DXY-BTC 역상관 약화** (상관계수: {corr_dxy_btc.iloc[-1]:.3f})
        - 상관관계 불명확
        - 독립적 움직임
        """)
    
    st.markdown("---")
    
    # 시그널 3: HY Spread
    st.subheader("⚠️ 시그널 3: High Yield Spread")
    if latest['HYSpread'] > 5.0:
        st.error(f"""
        🚨 **HY Spread 위기 임계점 초과** ({latest['HYSpread']:.2f}%)
        - 신용 시장 경색
        - 기업 파산 위험 증가
        - **추천**: 주식 시장 위험! 매도/방어 전략
        """)
    elif latest['HYSpread'] > 4.0:
        st.warning(f"""
        ⚠️ **HY Spread 경계 구간** ({latest['HYSpread']:.2f}%)
        - 신용 위험 상승 중
        - **추천**: 주의 필요, 포지션 축소 고려
        """)
    else:
        st.success(f"""
        ✅ **HY Spread 정상 구간** ({latest['HYSpread']:.2f}%)
        - 신용 시장 안정
        - 주식 시장 건강
        """)
    
    # Divergence 경고
    if recent_divergence > 0:
        st.markdown("---")
        st.error(f"""
        🚨 **Divergence 경고**
        - 최근 5일 중 {recent_divergence}일 Divergence 발생
        - S&P 500 상승 + HY Spread 상승
        - 허위 랠리 가능성 (Bear Market Rally)
        - **추천**: 매도 신호, 이익실현 고려
        """)
    
    st.markdown("---")
    
    # 종합 점수
    st.subheader("🎯 종합 신호 점수")
    
    score = 0
    if netliq_60d > 2:
        score += 1
    elif netliq_60d < -2:
        score -= 1
    
    if corr_dxy_btc.iloc[-1] < -0.5:
        score += 1
    elif corr_dxy_btc.iloc[-1] > 0:
        score -= 1
    
    if latest['HYSpread'] < 4.0:
        score += 1
    elif latest['HYSpread'] > 5.0:
        score -= 2
    
    if recent_divergence > 0:
        score -= 1
    
    col1, col2, col3 = st.columns(3)
    
    with col2:
        if score >= 2:
            st.success(f"""
            ### 🟢 강한 매수 신호
            **점수: +{score}/4**
            - 리스크 온 환경
            - BTC/주식 매수 고려
            """)
        elif score == 1:
            st.info(f"""
            ### 🟡 약한 매수 신호
            **점수: +{score}/4**
            - 중립적 환경
            - 선별적 매수
            """)
        elif score == 0:
            st.warning(f"""
            ### ⚪ 중립 신호
            **점수: {score}/4**
            - 관망 추천
            """)
        elif score == -1:
            st.warning(f"""
            ### 🟡 약한 매도 신호
            **점수: {score}/4**
            - 주의 필요
            - 포지션 축소 고려
            """)
        else:
            st.error(f"""
            ### 🔴 강한 매도 신호
            **점수: {score}/4**
            - 리스크 오프 환경
            - 현금 보유 권장
            """)

# ============================================================
# 푸터
# ============================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>📊 FRED API 퀀트 3콤보 대시보드 | 데이터 출처: Federal Reserve Economic Data</p>
    <p>⚠️ 본 대시보드는 투자 참고용이며, 투자 권유가 아닙니다.</p>
</div>
""", unsafe_allow_html=True)
