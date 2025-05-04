import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="T-base", page_icon=":bar_chart:", layout='wide')

st.title(":bar_chart: T-base Dashboard")
st.markdown("<style>div.block-container{padding-top: 2rem;}</style>", unsafe_allow_html=True)
f1=st.file_uploader(":file_folder: Upload file", type=(["csv", "xlsx", "xls","txt"]))
if f1 is not None:
    filename=f1.name
    st.write(filename)
    df=pd.read_excel(filename,)
else:
    os.chdir(r"https://docs.google.com/spreadsheets/d/1sdESfx8Ouzgoa96PkSelguM6fpIA962P/edit?usp=drive_link&ouid=116202969749852348106&rtpof=true&sd=true")
    df=ps.read_csv("Salesallc.xlsx")
df["SALEDATE"] = pd.to_datetime(df["SALEDATE"])

# Get min and max date from SALEDATE
StartDate = df["SALEDATE"].min()
EndDate = df["SALEDATE"].max()

with col1:
    date1 = st.date_input("Start Date", StartDate)

with col2:
    date2 = st.date_input("End Date", EndDate)

# Filter data between the selected dates
df = df[(df["SALEDATE"] >= pd.to_datetime(date1)) & (df["SALEDATE"] <= pd.to_datetime(date2))].copy()

st.sidebar.header("Choose your filter")

# channel filter 
Channel=st.sidebar.multiselect("Pick your channel",df["Channel"].unique())

if not Channel:
    df2=df.copy()
else:
    df2=df[df["Channel"].isin(Channel)]

# BRAN_NAME filter
BRAN_NAME=st.sidebar.multiselect("Pick your Store",df2["BRAN_NAME"].unique())

if not BRAN_NAME:
    df3=df2.copy()
else:
    df3=df2[df2["BRAN_NAME"].isin(BRAN_NAME)]

# ITEM_DESC_SECONDARY filter(if not here in tute)

ITEM_DESC_SECONDARY=st.sidebar.multiselect("Pick your Product",df3["ITEM_DESC_SECONDARY"].unique())

#if not ITEM_DESC_SECONDARY:
#    df4=df3.copy()
#else:
#    df4=df3[df3["ITEM_DESC_SECONDARY"].isin(ITEM_DESC_SECONDARY)]

# filter the data base on channel Brand name and Item desc

if not Channel and not BRAN_NAME and not ITEM_DESC_SECONDARY:
    filtered_df=df
elif not BRAN_NAME and not ITEM_DESC_SECONDARY:
    filtered_df=df[df["Channel"].isin(Channel)]
elif not Channel and not ITEM_DESC_SECONDARY:
    filtered_df=df[df["BRAN_NAME"].isin(BRAN_NAME)]
elif BRAN_NAME and ITEM_DESC_SECONDARY:
    filtered_df=df3[df["BRAN_NAME"].isin(BRAN_NAME)]
elif Channel and ITEM_DESC_SECONDARY:
    filtered_df=df3[df["BRAN_NAME"].isin(Channel)]
elif BRAN_NAME and Channel:
    filtered_df=df3[df["Channel"].isin(Channel)]
elif ITEM_DESC_SECONDARY:
    filtered_df=df3[df["ITEM_DESC_SECONDARY"].isin(ITEM_DESC_SECONDARY)]
else:
    filtered_df=df3[df3["Channel"].isin(Channel) & df3["BRAN_NAME"].isin(BRAN_NAME) & df3['ITEM_DESC_SECONDARY']]

style_df = filtered_df.groupby(by = ["SHORT_DESC"], as_index = False)["Sales QTY"].sum()

with col1:
    st.subheader("Stylwise sales")
    fig=px.bar(style_df, x = "SHORT_DESC", y="Sales QTY", text= ['{:,.0f}'.format(x) for x in style_df["Sales QTY"]], template="seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.header("Channel wise sales")
    fig= px.pie(filtered_df, values = "Sales QTY", names= "Channel", hole= 0.5)
    fig.update_traces(text = filtered_df["Channel"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns(2)


with cl1:
    with st.expander("Stylewise_ViewData"):
        st.write(style_df.style.background_gradient(cmap="Greens"))
        csv = style_df.to_csv(index = False)
        st.download_button("Download Data", data = csv, file_name="Style.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Channelwise_ViewData"):
        Channel_df = filtered_df.groupby(by = "Channel", as_index = False)["Sales QTY"].sum()
        st.write(Channel_df.style.background_gradient(cmap="Oranges"))
        csv = Channel_df.to_csv(index = False)
        st.download_button("Download Data", data = csv, file_name="Channel.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

# Date series Analysis line chart

filtered_df["month_year"] = filtered_df["SALEDATE"].dt.to_period("M")
st.subheader("Monthwise Sales Analysis")

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales QTY"].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales QTY", labels={"Month":"Quantity"}, height=500, width=900, template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View data of Monthwise Sales"):
    st.write(linechart.T.style.background_gradient(cmap="Greys"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button("Download Data", data = csv, file_name="Monthwise Sales.csv", mime= 'text/csv')

# Create a treemap based on Channel, (Region	Category	ITEM_DESC_SECONDARY)

st.subheader("Hierarchiacal view Region, Category, Sub-Category")
fig3=px.treemap(filtered_df, path = ["Region","Category","ITEM_DESC_SECONDARY"], values = "Sales QTY", hover_data = ["Sales QTY"],
                color = "ITEM_DESC_SECONDARY")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3,use_container_width=True)

# Category wise pie chart

Chart1, chart2 = st.columns((2))
with Chart1:
    st.subheader("Productwise Contribution")
    fig = px.pie(filtered_df, values= "Sales QTY", names= "ITEM_DESC_SECONDARY", template= "plotly_dark")
    fig.update_traces(text = filtered_df["ITEM_DESC_SECONDARY"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

# orange color also predefined example  "plotly_dark"above, below gridon

with chart2:
    st.subheader("Productwise Contribution")
    fig = px.pie(filtered_df, values= "Sales QTY", names= "Region", template= "gridon")
    fig.update_traces(text = filtered_df["Region"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

#sample data plotly.figure factory use create a table (can create database just see pivot table etc.)(actualy not required)


import plotly.figure_factory as ff
#st.subheader("👉Sample Data")
#with st.expander("Details"):
#   df_sample = df[0:5][["Channel", "file generation", "SALEDATE", "NO.", "BRAN_NAME", "NO2", "EAN", "PRODUCT DES", "SHORT_DESC", "Region", "Category", "ITEM_DESC_SECONDARY", "GROUP2", "BRAND TBASE", "COMP ", "COLOR_DESC", "SIZE_DESC", "Sales QTY", "SALRRP", "TAX", "SALNOT", "SALMRP"]]
#    fig = ff.create_table(df_sample, colorscale = "Cividis")
#   st.plotly_chart(fig, use_container_width=True)

st.markdown("Prductwise & Monthwise sales")
filtered_df["month"]=filtered_df["SALEDATE"].dt.strftime("%m - %b")
sub_category_year = pd.pivot_table(data = filtered_df, values="Sales QTY", index = ["ITEM_DESC_SECONDARY"],columns = "month",aggfunc="sum",fill_value=0)
st.write(sub_category_year.style.background_gradient(cmap="Oranges"))

#alter view data filter ilock :500,1:20
st.subheader("👉Data")
with st.expander("👉View Sample data"):
    st.write(filtered_df.iloc[:500,1:20].style.background_gradient(cmap="Greens"))

# download data

csv = df.to_csv(index=False)
st.download_button("Download Data", data = csv, file_name="Data.csv", mime="text/xlsx" )
