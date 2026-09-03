import streamlit as st
import yfinance as yf
import plotly.graph_objects as go


# --------------------------------------------------
# 페이지 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="주식 주가 조회",
    page_icon="📈",
    layout="wide"
)


# --------------------------------------------------
# 제목과 설명
# --------------------------------------------------
st.title("📈 주식 주가 조회")
st.write(
    "원하는 주식 종목 코드를 입력하면 최근 1년간의 주가 흐름과 "
    "현재가, 1년 등락률을 확인할 수 있습니다."
)


# --------------------------------------------------
# 종목 코드 입력
# --------------------------------------------------
ticker_input = st.text_input(
    "종목 코드를 입력하세요",
    value="005930.KS",
    placeholder="예: 005930.KS 또는 AAPL"
)

# 사용자가 입력한 종목 코드 앞뒤의 불필요한 공백 제거
ticker_symbol = ticker_input.strip().upper()


# --------------------------------------------------
# 주식 데이터 가져오기
# --------------------------------------------------
if ticker_symbol:

    try:
        # yfinance를 이용해 최근 1년간의 주가 데이터를 가져옵니다.
        stock = yf.Ticker(ticker_symbol)

        # 최근 1년 데이터 조회
        data = stock.history(period="1y")

        # 데이터가 없는 경우 안내 메시지 표시
        if data.empty:
            st.error(
                "해당 종목의 데이터를 찾을 수 없습니다. "
                "종목 코드를 다시 확인해주세요."
            )
            st.stop()

        # --------------------------------------------------
        # 현재가와 1년 전 가격 계산
        # --------------------------------------------------

        # 가장 최근 거래일의 종가
        current_price = float(data["Close"].iloc[-1])

        # 1년 전 거래일의 종가
        first_price = float(data["Close"].iloc[0])

        # 1년 동안의 등락률 계산
        change_rate = ((current_price - first_price) / first_price) * 100


        # --------------------------------------------------
        # 통화 단위 설정
        # --------------------------------------------------

        # 한국 주식이면 원화, 그 외에는 달러로 표시합니다.
        if ticker_symbol.endswith(".KS") or ticker_symbol.endswith(".KQ"):
            currency = "원"
        else:
            currency = "USD"


        # --------------------------------------------------
        # 지표 카드
        # --------------------------------------------------
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="현재가",
                value=f"{current_price:,.2f} {currency}"
            )

        with col2:
            st.metric(
                label="최근 1년 등락률",
                value=f"{change_rate:+.2f}%"
            )


        # --------------------------------------------------
        # 주가 그래프
        # --------------------------------------------------
        st.subheader("📊 최근 1년 주가 흐름")

        # Plotly 그래프 생성
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Close"],
                mode="lines",
                name="종가",
                line=dict(width=2)
            )
        )

        # 그래프 제목과 축 이름 설정
        fig.update_layout(
            title=f"{ticker_symbol} 최근 1년 주가",
            xaxis_title="날짜",
            yaxis_title=f"주가 ({currency})",
            hovermode="x unified",
            height=500,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        # 그래프 표시
        st.plotly_chart(
            fig,
            use_container_width=True
        )


        # --------------------------------------------------
        # 간단한 안내
        # --------------------------------------------------
        st.caption(
            "※ 주가는 최근 거래일의 종가를 기준으로 표시됩니다. "
            "실제 투자 판단을 위한 자료로 사용하기 전에 추가적인 정보를 확인하세요."
        )

    except Exception as e:
        # 종목 코드가 잘못되었거나 데이터를 가져오는 과정에서 오류가 발생한 경우
        st.error(
            "주식 데이터를 불러오는 중 문제가 발생했습니다. "
            "종목 코드를 확인해주세요."
        )

else:
    st.info("위 입력창에 주식 종목 코드를 입력해주세요.")
