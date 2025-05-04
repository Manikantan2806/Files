import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="T-base", page_icon=":bar_chart:", layout='wide')
st.title(":bar_chart: T-base Dashboard")
st.markdown("<style>div.block-container{padding-top: 2rem;}</style>", unsafe_allow_html=True)

f1 = st.file_uploader(":file_folder: Upload file", type=(["csv", "xlsx", "xls", "txt"]))

if f1 is not None:
    filename = f1.name
    st.write("Loaded file:", filename)

    if filename.endswith(".csv") or filename.endswith(".txt"):
        df = pd.read_csv(f1)
    else:
        df = pd.read_excel(f1)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Check for SALEDATE
    if "SALEDATE" not in df.columns:
        st.error("❌ Column 'SALEDATE' not found in uploaded file. Please check your file headers.")
        st.stop()

    # Convert SALEDATE to datetime
    df["SALEDATE"] = pd.to_datetime(df["SALEDATE"], errors='coerce')
    df.dropna(subset=["SALEDATE"], inplace=True)

    # Sidebar filters layout
    col1, col2 = st.columns(2)

    StartDate = df["SALEDATE"].min()
    EndDate = df["SALEDATE"].max()

    with col1:
        date1 = st.date_input("Start Date", StartDate)

    with col2:
        date2 = st.date_input("End Date", EndDate)

    df = df[(df["SALEDATE"] >= pd.to_datetime(date1)) & (df["SALEDATE"] <= pd.to_datetime(date2))].copy()

    st.sidebar.header("Choose your filter")

    Channel = st.sidebar.multiselect("Pick your channel", df["Channel"].unique())
    df2 = df[df["Channel"].isin(Channel)] if Channel else df.copy()

    BRAN_NAME = st.sidebar.multiselect("Pick your Store", df2["BRAN_NAME"].unique())
    df3 = df2[df2["BRAN_NAME"].isin(BRAN_NAME)] if BRAN_NAME else df2.copy()

    ITEM_DESC_SECONDARY = st.sidebar.multiselect("Pick your Product", df3["ITEM_DESC_SECONDARY"].unique())

    # Final filtering
    filtered_df = df3.copy()
    if ITEM_DESC_SECONDARY:
        filtered_df = filtered_df[filtered_df["ITEM_DESC_SECONDARY"].isin(ITEM_DESC_SECONDARY)]

    # Style-wise Sales Chart
    style_df = filtered_df.groupby(by=["SHORT_DESC"], as_index=False)["Sales QTY"].sum()

    with col1:
        st.subheader("Stylewise sales")
        fig = px.bar(style_df, x="SHORT_DESC", y="Sales QTY", text=style_df["Sales QTY"].apply(lambda x: f'{x:,.0f}'), template="seaborn")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.header("Channel wise sales")
        fig = px.pie(filtered_df, values="Sales QTY", names="Channel", hole=0.5)
        fig.update_traces(text=filtered_df["Channel"], textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    cl1, cl2 = st.columns(2)

    with cl1:
        with st.expander("Stylewise_ViewData"):
            st.write(style_df.style.background_gradient(cmap="Greens"))
            csv = style_df.to_csv(index=False)
            st.download_button("Download Data", data=csv, file_name="Style.csv", mime="text/csv")

    with cl2:
        with st.expander("Channelwise_ViewData"):
            channel_df = filtered_df.groupby(by="Channel", as_index=False)["Sales QTY"].sum()
            st.write(channel_df.style.background_gradient(cmap="Oranges"))
            csv = channel_df.to_csv(index=False)
            st.download_button("Download Data", data=csv, file_name="Channel.csv", mime="text/csv")

    # Month-wise Line Chart
    filtered_df["month_year"] = filtered_df["SALEDATE"].dt.to_period("M")
    st.subheader("Monthwise Sales Analysis")
    linechart = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales QTY"].sum().reset_index()
    fig2 = px.line(linechart, x="month_year", y="Sales QTY", height=500, width=900, template="gridon")
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("View data of Monthwise Sales"):
        st.write(linechart.T.style.background_gradient(cmap="Greys"))
        csv = linechart.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data", data=csv, file_name="Monthwise_Sales.csv", mime="text/csv")

    # Treemap
    st.subheader("Hierarchiacal view Region, Category, Sub-Category")
    fig3 = px.treemap(filtered_df, path=["Region", "Category", "ITEM_DESC_SECONDARY"], values="Sales QTY", color="ITEM_DESC_SECONDARY")
    fig3.update_layout(width=800, height=650)
    st.plotly_chart(fig3, use_container_width=True)

    # Productwise Pie Charts
    Chart1, chart2 = st.columns(2)

    with Chart1:
        st.subheader("Productwise Contribution")
        fig = px.pie(filtered_df, values="Sales QTY", names="ITEM_DESC_SECONDARY", template="plotly_dark")
        fig.update_traces(text=filtered_df["ITEM_DESC_SECONDARY"], textposition="inside")
        st.plotly_chart(fig, use_container_width=True)

    with chart2:
        st.subheader("Productwise Contribution")
        fig = px.pie(filtered_df, values="Sales QTY", names="Region", template="gridon")
        fig.update_traces(text=filtered_df["Region"], textposition="inside")
        st.plotly_chart(fig, use_container_width=True)

    # Pivot Table
    st.markdown("Productwise & Monthwise sales")
    filtered_df["month"] = filtered_df["SALEDATE"].dt.strftime("%m - %b")
    pivot_df = pd.pivot_table(filtered_df, values="Sales QTY", index=["ITEM_DESC_SECONDARY"], columns="month", aggfunc="sum", fill_value=0)
    st.write(pivot_df.style.background_gradient(cmap="Oranges"))

    # View Sample Data
    st.subheader("👉Data")
    with st.expander("👉View Sample data"):
        st.write(filtered_df.iloc[:500, 1:20].style.background_gradient(cmap="Greens"))

    # Download full filtered data
    csv = df.to_csv(index=False)
    st.download_button("Download Data", data=csv, file_name="Data.csv", mime="text/csv")
