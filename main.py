import streamlit as st
import yfinance as yf
import plotly.graph_objects as go


# --------------------------------------------------
# 페이지 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="주식 비교 분석",
    page_icon="📈",
    layout="wide"
)


# --------------------------------------------------
# 제목과 설명
# --------------------------------------------------
st.title("📈 주식 비교 분석")
st.write(
    "최대 2개의 주식 종목을 선택하여 원하는 기간의 주가 흐름을 "
    "비교하고 주요 가격 정보를 확인해보세요."
)


# --------------------------------------------------
# 종목 입력창
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    ticker1 = st.text_input(
        "첫 번째 종목",
        value="005930.KS",
        placeholder="예: 005930.KS"
    )

with col2:
    ticker2 = st.text_input(
        "두 번째 종목 (선택)",
        value="AAPL",
        placeholder="예: AAPL"
    )


# 입력한 종목 코드의 앞뒤 공백 제거 및 대문자 변환
ticker1 = ticker1.strip().upper()
ticker2 = ticker2.strip().upper()


# --------------------------------------------------
# 기간 선택 버튼
# --------------------------------------------------
st.subheader("📅 조회 기간")

period_options = {
    "1개월": "1mo",
    "6개월": "6mo",
    "1년": "1y",
    "5년": "5y"
}

# 기본 선택 기간
if "selected_period" not in st.session_state:
    st.session_state.selected_period = "1년"


# 버튼을 가로로 배치
period_cols = st.columns(4)

for i, period_name in enumerate(period_options.keys()):
    with period_cols[i]:
        if st.button(
            period_name,
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.selected_period == period_name
                else "secondary"
            )
        ):
            st.session_state.selected_period = period_name


selected_period_name = st.session_state.selected_period
selected_period = period_options[selected_period_name]

st.caption(f"현재 선택된 기간: **{selected_period_name}**")


# --------------------------------------------------
# 주식 데이터 가져오는 함수
# --------------------------------------------------
def get_stock_data(ticker):
    """
    yfinance를 이용해 선택한 기간의 주가 데이터를 가져옵니다.
    """

    stock = yf.Ticker(ticker)

    # 선택한 기간의 주가 데이터를 가져옵니다.
    data = stock.history(period=selected_period)

    # 데이터가 없는 경우 None을 반환합니다.
    if data.empty:
        return None

    return data


# --------------------------------------------------
# 통화 단위 확인 함수
# --------------------------------------------------
def get_currency(ticker):
    """
    한국 주식은 원화, 그 외의 종목은 달러로 표시합니다.
    """

    if ticker.endswith(".KS") or ticker.endswith(".KQ"):
        return "원"

    return "USD"


# --------------------------------------------------
# 가격 통계 카드 표시 함수
# --------------------------------------------------
def show_statistics(data, ticker):
    """
    최고가, 최저가, 평균가를 카드 형태로 표시합니다.
    """

    # 해당 기간의 최고가
    highest = float(data["Close"].max())

    # 해당 기간의 최저가
    lowest = float(data["Close"].min())

    # 해당 기간의 평균 종가
    average = float(data["Close"].mean())

    currency = get_currency(ticker)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "최고가",
            f"{highest:,.2f} {currency}"
        )

    with col2:
        st.metric(
            "최저가",
            f"{lowest:,.2f} {currency}"
        )

    with col3:
        st.metric(
            "평균가",
            f"{average:,.2f} {currency}"
        )


# --------------------------------------------------
# 입력된 종목 확인
# --------------------------------------------------
if not ticker1:
    st.warning("첫 번째 종목 코드를 입력해주세요.")
    st.stop()


# --------------------------------------------------
# 첫 번째 종목 데이터 가져오기
# --------------------------------------------------
try:
    data1 = get_stock_data(ticker1)

    if data1 is None:
        st.error(
            f"'{ticker1}' 종목의 데이터를 찾을 수 없습니다. "
            "종목 코드를 확인해주세요."
        )
        st.stop()

except Exception:
    st.error(
        f"'{ticker1}' 데이터를 불러오는 중 문제가 발생했습니다."
    )
    st.stop()


# --------------------------------------------------
# 두 번째 종목 데이터 가져오기
# --------------------------------------------------
data2 = None

if ticker2:

    try:
        data2 = get_stock_data(ticker2)

        if data2 is None:
            st.warning(
                f"'{ticker2}' 종목의 데이터를 찾을 수 없습니다. "
                "두 번째 종목은 그래프에서 제외됩니다."
            )

    except Exception:
        st.warning(
            f"'{ticker2}' 데이터를 불러오지 못했습니다."
        )


# --------------------------------------------------
# 현재가와 기간 등락률 계산
# --------------------------------------------------
current_price1 = float(data1["Close"].iloc[-1])
start_price1 = float(data1["Close"].iloc[0])

change_rate1 = (
    (current_price1 - start_price1)
    / start_price1
) * 100

currency1 = get_currency(ticker1)


# --------------------------------------------------
# 첫 번째 종목 기본 정보 카드
# --------------------------------------------------
st.subheader(f"💰 {ticker1}")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "현재가",
        f"{current_price1:,.2f} {currency1}"
    )

with col2:
    st.metric(
        f"{selected_period_name} 등락률",
        f"{change_rate1:+.2f}%"
    )


# --------------------------------------------------
# 두 번째 종목 기본 정보 카드
# --------------------------------------------------
if data2 is not None:

    current_price2 = float(data2["Close"].iloc[-1])
    start_price2 = float(data2["Close"].iloc[0])

    change_rate2 = (
        (current_price2 - start_price2)
        / start_price2
    ) * 100

    currency2 = get_currency(ticker2)

    st.subheader(f"💰 {ticker2}")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "현재가",
            f"{current_price2:,.2f} {currency2}"
        )

    with col2:
        st.metric(
            f"{selected_period_name} 등락률",
            f"{change_rate2:+.2f}%"
        )


# --------------------------------------------------
# 주가 그래프
# --------------------------------------------------
st.subheader(f"📊 {selected_period_name} 주가 흐름")


fig = go.Figure()


# 첫 번째 종목 그래프
fig.add_trace(
    go.Scatter(
        x=data1.index,
        y=data1["Close"],
        mode="lines",
        name=ticker1,
        line=dict(width=2)
    )
)


# 두 번째 종목 그래프
if data2 is not None:

    fig.add_trace(
        go.Scatter(
            x=data2.index,
            y=data2["Close"],
            mode="lines",
            name=ticker2,
            line=dict(width=2)
        )
    )


# 그래프 설정
fig.update_layout(
    title=f"{ticker1}"
          + (f" vs {ticker2}" if data2 is not None else "")
          + f" - 최근 {selected_period_name}",
    xaxis_title="날짜",
    yaxis_title="주가",
    hovermode="x unified",
    height=500,
    margin=dict(
        l=20,
        r=20,
        t=60,
        b=20
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)


# 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 통계 카드
# --------------------------------------------------
st.subheader("📌 주요 가격 정보")

# 첫 번째 종목 통계
st.write(f"**{ticker1}**")
show_statistics(data1, ticker1)


# 두 번째 종목 통계
if data2 is not None:

    st.write(f"**{ticker2}**")
    show_statistics(data2, ticker2)


# --------------------------------------------------
# 안내 문구
# --------------------------------------------------
st.caption(
    "※ 주가는 yfinance에서 제공하는 데이터를 기반으로 표시됩니다. "
    "시장 상황에 따라 실제 거래 가격과 차이가 있을 수 있습니다."
)
