import streamlit as st
import pandas as pd

st.set_page_config(page_title="자동 데이터 대시보드", layout="wide")

st.title("📊 CSV 업로드 자동 대시보드")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # 데이터 불러오기
    df = pd.read_csv(uploaded_file)
    st.subheader("데이터 미리보기")
    st.dataframe(df.head())

    # 기본 정보
    st.subheader("데이터 기본 정보")
    st.write("행 개수:", df.shape[0])
    st.write("열 개수:", df.shape[1])
    st.write("결측치 개수:")
    st.write(df.isnull().sum())

    # 기술통계
    st.subheader("기술 통계 요약")
    st.write(df.describe())

    # 수치형 컬럼 선택
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    if len(numeric_cols) > 0:
        st.subheader("📈 히스토그램 / 시각화")
        col = st.selectbox("시각화할 컬럼 선택", numeric_cols)
        st.bar_chart(df[col].value_counts())

        st.subheader("📉 상관관계")
        corr = df[numeric_cols].corr()
        st.dataframe(corr.style.background_gradient(cmap="coolwarm"))
    else:
        st.warning("수치형 컬럼이 없습니다.")

else:
    st.info("CSV 파일을 업로드하면 자동으로 분석 결과가 표시됩니다.")
