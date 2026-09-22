import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일(8자리 숫자) -> 날짜 타입으로 변환
    df["openDt"] = pd.to_datetime(df["openDt"].astype(str), format="%Y%m%d", errors="coerce")

    # 장르에 세로막대(|) 기호로 여러 개가 적힌 경우 첫 번째 장르만 사용
    df["genre_main"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    return df


df = load_data()

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "최근 1년간 박스오피스 10위권에 든 영화 가운데, 해당 기간에 개봉한 216편의 데이터를 살펴봅니다."
)

with st.expander("데이터 미리보기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# 구역 1. 장르별 영화 편수
# ---------------------------------------------------------------------------
st.header("1. 장르별 영화 편수")

genre_counts = df["genre_main"].value_counts().reset_index()
genre_counts.columns = ["장르", "편수"]

fig_genre = px.pie(
    genre_counts,
    names="장르",
    values="편수",
    hole=0.5,
)
fig_genre.update_traces(
    textinfo="label+percent",
    hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig_genre.update_layout(
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_genre, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.info("여기에 이 그래프를 보고 파악한 내용을 한 문장으로 적어 보세요.")

st.divider()

# ---------------------------------------------------------------------------
# 구역 2. (다음 그래프를 위한 자리)
# ---------------------------------------------------------------------------
# st.header("2. ...")
# ...
# st.markdown("**📌 이 그래프로 알 수 있는 것**")
# st.info("여기에 이 그래프를 보고 파악한 내용을 한 문장으로 적어 보세요.")
