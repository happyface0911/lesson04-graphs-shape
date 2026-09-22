import streamlit as st
import pandas as pd
import numpy as np
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
    df.loc[df["genre_main"].isin(["nan", "None", ""]), "genre_main"] = "정보 없음"

    # nation 열에 결측치나 숫자형 값이 섞여 있으면 그래프에서 타입 에러가 나므로 문자열로 통일
    df["nation"] = df["nation"].astype(str).str.strip()
    df.loc[df["nation"].isin(["nan", "None", ""]), "nation"] = "정보 없음"

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
# 구역 2. 장르 안에 영화 - 총 관객 트리맵
# ---------------------------------------------------------------------------
st.header("2. 장르별 영화의 총 관객 트리맵")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), "genre_main", "movieNm"],
    values="total_audi",
    custom_data=["movieNm", "total_audi"],
)
fig_treemap.update_traces(
    hovertemplate="영화명: %{customdata[0]}<br>총 관객: %{customdata[1]:,}명<extra></extra>",
)
fig_treemap.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.info("여기에 이 그래프를 보고 파악한 내용을 한 문장으로 적어 보세요.")

st.divider()

# ---------------------------------------------------------------------------
# 구역 3. 총 관객 히스토그램
# ---------------------------------------------------------------------------
st.header("3. 총 관객 분포")

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=20,
    labels={"total_audi": "총 관객 수"},
)
fig_hist.update_traces(
    hovertemplate="구간: %{x}<br>영화 수: %{y}편<extra></extra>",
)
fig_hist.update_layout(
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_hist, use_container_width=True)

# 가장 영화가 몰려 있는 구간 계산
counts, bin_edges = np.histogram(df["total_audi"].dropna(), bins=20)
mode_idx = counts.argmax()
mode_low, mode_high = bin_edges[mode_idx], bin_edges[mode_idx + 1]

# 총 관객이 가장 많은 영화 계산
top_row = df.loc[df["total_audi"].idxmax()]

st.markdown("**📊 데이터로 본 사실**")
st.write(
    f"- 대부분의 영화는 총 관객 **{mode_low:,.0f}명 ~ {mode_high:,.0f}명** "
    f"구간에 몰려 있습니다. (이 구간 영화 수: {counts[mode_idx]}편)"
)
st.write(
    f"- 총 관객이 가장 많은 영화는 **{top_row['movieNm']}**"
    f"(총 관객 {top_row['total_audi']:,.0f}명)입니다."
)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.info("여기에 이 그래프를 보고 파악한 내용을 한 문장으로 적어 보세요.")

st.divider()

# ---------------------------------------------------------------------------
# 구역 4. 개봉일 스크린수 vs 총 관객 산점도
# ---------------------------------------------------------------------------
st.header("4. 개봉일 스크린수와 총 관객의 관계")

fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre_main",
    custom_data=["movieNm"],
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객 수",
        "genre_main": "장르",
    },
)
fig_scatter.update_traces(
    hovertemplate="영화명: %{customdata[0]}<br>개봉일 스크린수: %{x:,}개<br>총 관객: %{y:,}명<extra></extra>",
)
fig_scatter.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.info("여기에 이 그래프를 보고 파악한 내용을 한 문장으로 적어 보세요.")

st.divider()

# ---------------------------------------------------------------------------
# 구역 5. 장르별 총 관객 상자 그림 (10편 이상 장르만)
# ---------------------------------------------------------------------------
st.header("5. 장르별 총 관객 분포 (영화 10편 이상 장르만)")

genre_movie_counts = df["genre_main"].value_counts()
major_genres = genre_movie_counts[genre_movie_counts >= 10].index
df_major = df[df["genre_main"].isin(major_genres)]

fig_box = px.box(
    df_major,
    x="genre_main",
    y="total_audi",
    color="genre_main",
    custom_data=["movieNm"],
    labels={"genre_main": "장르", "total_audi": "총 관객 수"},
)
fig_box.update_traces(
    hovertemplate="영화명: %{customdata[0]}<br>총 관객: %{y:,}명<extra></extra>",
)
fig_box.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객 수",
    showlegend=False,
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_box, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.info("여기에 이 그래프를 보고 파악한 내용을 한 문장으로 적어 보세요.")

st.divider()

# ---------------------------------------------------------------------------
# 구역 6. 개봉일 스크린수 vs 총 관객 버블 그래프 (크기: 첫 주 관객)
# ---------------------------------------------------------------------------
st.header("6. 개봉일 스크린수와 총 관객의 관계 (첫 주 관객 크기 반영)")

fig_bubble = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre_main",
    custom_data=["movieNm", "first_week_audi"],
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객 수",
        "genre_main": "장르",
    },
    size_max=40,
)
fig_bubble.update_traces(
    hovertemplate=(
        "영화명: %{customdata[0]}<br>"
        "개봉일 스크린수: %{x:,}개<br>"
        "총 관객: %{y:,}명<br>"
        "첫 주 관객: %{customdata[1]:,}명<extra></extra>"
    ),
)
fig_bubble.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.info("여기에 이 그래프를 보고 파악한 내용을 한 문장으로 적어 보세요.")

st.divider()

# ---------------------------------------------------------------------------
# 구역 7. 제작 국가 → 장르 선버스트 그래프
# ---------------------------------------------------------------------------
st.header("7. 제작 국가별 장르 구성")

nation_genre_counts = (
    df.groupby(["nation", "genre_main"]).size().reset_index(name="편수")
)

fig_sunburst = px.sunburst(
    nation_genre_counts,
    path=["nation", "genre_main"],
    values="편수",
)
fig_sunburst.update_traces(
    hovertemplate="%{label}<br>편수: %{value}편<extra></extra>",
)
fig_sunburst.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_sunburst, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.info("여기에 이 그래프를 보고 파악한 내용을 한 문장으로 적어 보세요.")

st.divider()

# ---------------------------------------------------------------------------
# 구역 8. 나라별 선호 장르 비교 (내 질문: 나라별로 선호하는 영화 종류가 다른가?)
# ---------------------------------------------------------------------------
st.header("8. 나라별 선호 장르 비교")

st.caption(
    "❓ 내 질문: 나라별로 선호하는 영화 종류가 다른가? → "
    "나라마다 장르 구성 비율을 한눈에 비교할 수 있는 **100% 누적 막대그래프**를 골랐습니다."
)

nation_movie_counts = df["nation"].value_counts()
major_nations = nation_movie_counts[nation_movie_counts >= 5].index
df_nation_major = df[df["nation"].isin(major_nations)]

nation_genre_pct = (
    df_nation_major.groupby(["nation", "genre_main"])
    .size()
    .reset_index(name="편수")
)

fig_nation_genre = px.bar(
    nation_genre_pct,
    x="nation",
    y="편수",
    color="genre_main",
    barnorm="percent",
    labels={"nation": "제작 국가", "편수": "비율(%)", "genre_main": "장르"},
)
fig_nation_genre.update_traces(
    hovertemplate="국가: %{x}<br>장르: %{fullData.name}<br>비율: %{y:.1f}%<extra></extra>",
)
fig_nation_genre.update_layout(
    xaxis_title="제작 국가",
    yaxis_title="장르 비율(%)",
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_nation_genre, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.info("여기에 이 그래프를 보고 파악한 내용을 한 문장으로 적어 보세요.")

st.divider()

# ---------------------------------------------------------------------------
# 구역 9. (다음 그래프를 위한 자리)
# ---------------------------------------------------------------------------
# st.header("9. ...")
# ...
# st.markdown("**📌 이 그래프로 알 수 있는 것**")
# st.info("여기에 이 그래프를 보고 파악한 내용을 한 문장으로 적어 보세요.")
