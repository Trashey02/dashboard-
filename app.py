
import base64
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="E-Commerce AI Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "ecommerce_data.xlsx"
BG_PATH = Path(__file__).parent / "assets" / "ai_blue_background.jpg"

AI_BLUE = "#16C7F9"
CYAN = "#00E5FF"
DEEP = "#02081F"
PANEL = "rgba(5, 20, 52, 0.84)"
GRID = "rgba(87, 189, 255, 0.14)"
TEXT = "#EAF9FF"
MUTED = "#8FB8D1"
BAR_COLORS = ["#00E5FF", "#278CFF", "#7B61FF", "#00C2A8", "#FF7A59", "#FFD166", "#F45BFF", "#49E0A5", "#7DD3FC", "#B9F2FF"]

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    if "Month" not in df:
        df["Month"] = df["Date"].dt.to_period("M").astype(str)
    return df

def background_css():
    encoded = base64.b64encode(BG_PATH.read_bytes()).decode()
    return f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background:
          linear-gradient(90deg, rgba(1,6,25,.96) 0%, rgba(1,8,32,.90) 48%, rgba(2,10,36,.82) 100%),
          url("data:image/jpeg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(2,9,35,.98), rgba(3,24,61,.96));
        border-right: 1px solid rgba(0,229,255,.20);
    }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    .block-container {{ padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1500px; }}
    h1, h2, h3, p, label {{ color: {TEXT} !important; }}
    .hero {{
        padding: 1.5rem 1.7rem;
        border: 1px solid rgba(0,229,255,.28);
        background: linear-gradient(110deg, rgba(5,20,52,.92), rgba(4,37,78,.60));
        border-radius: 22px;
        box-shadow: 0 0 28px rgba(0,185,255,.10);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }}
    .hero h1 {{
        font-size: 2.4rem !important;
        margin: 0 !important;
        letter-spacing: .5px;
        text-shadow: 0 0 20px rgba(0,229,255,.32);
    }}
    .hero p {{ color: {MUTED} !important; margin-bottom: 0 !important; }}
    .metric-card {{
        padding: 1rem 1.1rem;
        min-height: 112px;
        background: linear-gradient(145deg, rgba(8,31,70,.88), rgba(3,17,48,.88));
        border: 1px solid rgba(0,229,255,.22);
        border-radius: 18px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.04), 0 10px 28px rgba(0,0,0,.18);
        transition: transform .2s ease, box-shadow .2s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 0 24px rgba(0,229,255,.15);
    }}
    .metric-label {{ color: {MUTED}; font-size: .82rem; text-transform: uppercase; letter-spacing: 1px; }}
    .metric-value {{ color: white; font-size: 1.65rem; font-weight: 700; margin-top: .35rem; }}
    .metric-note {{ color: #73E5FF; font-size: .78rem; margin-top: .3rem; }}
    div[data-testid="stPlotlyChart"] {{
        background: linear-gradient(145deg, rgba(5,20,52,.82), rgba(3,13,40,.76));
        border: 1px solid rgba(54,185,255,.15);
        border-radius: 18px;
        padding: .35rem;
        box-shadow: 0 12px 30px rgba(0,0,0,.14);
    }}
    .stButton>button {{
        border-radius: 12px; border: 1px solid rgba(0,229,255,.35);
        background: linear-gradient(90deg, #075a93, #0a8cc7);
        color: white; transition: all .2s ease;
    }}
    .stButton>button:hover {{ box-shadow: 0 0 18px rgba(0,229,255,.35); transform: translateY(-1px); }}
    [data-testid="stRadio"] label {{ padding: .25rem 0; }}
    .insight {{
        background: rgba(0,229,255,.06); border-left: 3px solid {CYAN};
        padding: .9rem 1rem; border-radius: 10px; color: {TEXT};
        margin: .6rem 0 1rem 0;
    }}
    </style>
    """

st.markdown(background_css(), unsafe_allow_html=True)
df = load_data()

def apply_theme(fig, title=None, height=380):
    fig.update_layout(
        title=dict(text=title or "", font=dict(color=TEXT, size=18)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(2,10,32,.28)",
        font=dict(color=TEXT),
        height=height,
        margin=dict(l=35, r=25, t=55, b=35),
        hoverlabel=dict(bgcolor="#061B42", font_color=TEXT),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, title_font_color=MUTED)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, title_font_color=MUTED)
    return fig

# Sidebar: smooth two-page navigation and global filters
st.sidebar.markdown("## ✦ AI BLUE ANALYTICS")
page = st.sidebar.radio("Navigate", ["Dashboard", "Research Analysis"], index=0)
st.sidebar.markdown("---")
st.sidebar.markdown("### Interactive Filters")

min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input("Order date range", (min_date, max_date), min_value=min_date, max_value=max_date)
categories = st.sidebar.multiselect("Product category", sorted(df["Product_Category"].dropna().unique()), default=sorted(df["Product_Category"].dropna().unique()))
cities = st.sidebar.multiselect("City", sorted(df["City"].dropna().unique()), default=sorted(df["City"].dropna().unique()))
devices = st.sidebar.multiselect("Device", sorted(df["Device_Type"].dropna().unique()), default=sorted(df["Device_Type"].dropna().unique()))

filtered = df.copy()
if len(date_range) == 2:
    filtered = filtered[(filtered["Date"].dt.date >= date_range[0]) & (filtered["Date"].dt.date <= date_range[1])]
filtered = filtered[
    filtered["Product_Category"].isin(categories)
    & filtered["City"].isin(cities)
    & filtered["Device_Type"].isin(devices)
]

if filtered.empty:
    st.warning("No records match the selected filters. Please broaden your selections.")
    st.stop()

if page == "Research Analysis":
    st.markdown("""
    <div class="hero">
      <h1>Research Analysis</h1>
      <p>Interactive summary of the E-Commerce Customer Behaviour study, built from the cleaned 1,000-order dataset.</p>
    </div>
    """, unsafe_allow_html=True)

    total_rev = filtered["Total_Amount"].sum()
    median_order = filtered["Total_Amount"].median()
    electronics_share = (filtered.loc[filtered["Product_Category"]=="Electronics", "Total_Amount"].sum() / total_rev * 100) if total_rev else 0

    c1,c2,c3,c4 = st.columns(4)
    for col, label, value, note in [
        (c1, "Orders analysed", f"{len(filtered):,}", "Interactive filtered sample"),
        (c2, "Revenue", f"Nu. {total_rev:,.0f}", "Total order value"),
        (c3, "Typical order", f"Nu. {median_order:,.0f}", "Median is more robust to skew"),
        (c4, "Electronics share", f"{electronics_share:.1f}%", "Share of filtered revenue"),
    ]:
        col.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

    st.markdown("### Study overview")
    st.markdown("""
    <div class="insight">
    The source analysis cleaned the raw data, checked missing values, duplicates, data types, label consistency,
    value ranges, internal amount consistency and outliers before exploratory analysis and hypothesis testing.
    The dataset contains customer demographics, product behaviour, spending, browsing, delivery and rating variables.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Key research findings")
    findings = [
        ("What drives revenue?", "Product category is the strongest visible differentiator. High-value categories contribute much more revenue than their order counts alone would suggest."),
        ("What is a typical order?", "Order value is strongly right-skewed, so the median is a more representative description of a typical order than the mean."),
        ("Do customer characteristics change spending?", "Age, gender, device and returning-customer status show much smaller differences in spending than product category."),
        ("Does browsing predict spending?", "Session duration and pages viewed have very weak relationships with order value in the source analysis."),
        ("What happens over time?", "Order counts are comparatively steady, while revenue varies more because a small number of high-value purchases can move weekly totals."),
    ]
    for title, text in findings:
        with st.expander(title, expanded=False):
            st.write(text)

    st.markdown("### Research questions represented in the dashboard")
    st.write("""
    **H1:** Product category and order value  
    **H2:** Session engagement and order value  
    **H3:** Age group and order value  
    **H4:** Returning versus new customers  
    **H5:** Delivery time and customer rating
    """)

else:
    st.markdown("""
    <div class="hero">
      <h1>E-Commerce Intelligence Dashboard</h1>
      <p>AI-blue interactive analytics • hover for details • use the sidebar filters to explore the dataset</p>
    </div>
    """, unsafe_allow_html=True)

    revenue = filtered["Total_Amount"].sum()
    orders = len(filtered)
    avg_order = filtered["Total_Amount"].mean()
    returning = filtered["Is_Returning_Customer"].mean() * 100

    m1,m2,m3,m4 = st.columns(4)
    cards = [
        ("Total Revenue", f"Nu. {revenue:,.0f}", "Filtered sales value"),
        ("Total Orders", f"{orders:,}", "Customer transactions"),
        ("Average Order", f"Nu. {avg_order:,.0f}", "Mean order value"),
        ("Returning Customers", f"{returning:.1f}%", "Customer loyalty indicator"),
    ]
    for col,(label,value,note) in zip([m1,m2,m3,m4],cards):
        col.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

    st.markdown("## Revenue & Product Performance")
    cat = filtered.groupby("Product_Category", as_index=False).agg(Revenue=("Total_Amount","sum"), Orders=("Total_Amount","size"))
    cat = cat.sort_values("Revenue", ascending=False)
    f1 = px.bar(cat, x="Product_Category", y="Revenue", color="Product_Category", color_discrete_sequence=BAR_COLORS, title="Revenue by Product Category")
    f1.update_layout(showlegend=False)
    st.plotly_chart(apply_theme(f1), use_container_width=True)

    a,b = st.columns(2)
    f2 = px.pie(cat, names="Product_Category", values="Orders", hole=.56, color_discrete_sequence=BAR_COLORS, title="Order Distribution by Product Category")
    f2.update_traces(textinfo="percent+label")
    a.plotly_chart(apply_theme(f2, height=380), use_container_width=True)

    monthly = filtered.groupby(filtered["Date"].dt.to_period("M").astype(str), as_index=False).agg(Revenue=("Total_Amount","sum"), Orders=("Total_Amount","size"))
    monthly.columns = ["Month","Revenue","Orders"]
    f3 = px.line(monthly, x="Month", y="Revenue", markers=True, title="Revenue Trend Over Time")
    f3.update_traces(line=dict(color=CYAN, width=3), marker=dict(size=8, color="#7B61FF"))
    b.plotly_chart(apply_theme(f3, height=380), use_container_width=True)

    st.markdown("## Customer & Demographic Behaviour")
    c,d = st.columns(2)
    age = filtered.groupby("Age_Group", as_index=False).agg(Revenue=("Total_Amount","sum"), Orders=("Total_Amount","size"))
    age["Age_Group"] = pd.Categorical(age["Age_Group"], categories=["18-24","25-34","35-44","45-54","55+"], ordered=True)
    age = age.sort_values("Age_Group")
    f4 = px.bar(age, x="Age_Group", y="Revenue", color="Age_Group", color_discrete_sequence=BAR_COLORS, title="Revenue by Age Group")
    f4.update_layout(showlegend=False)
    c.plotly_chart(apply_theme(f4, height=380), use_container_width=True)

    gender = filtered.groupby("Gender", as_index=False).size().rename(columns={"size":"Orders"})
    f5 = px.bar(gender, x="Gender", y="Orders", color="Gender", color_discrete_sequence=BAR_COLORS, title="Customer Orders by Gender")
    f5.update_layout(showlegend=False)
    d.plotly_chart(apply_theme(f5, height=380), use_container_width=True)

    st.markdown("## Channels & Locations")
    e,f = st.columns(2)
    device = filtered.groupby("Device_Type", as_index=False).agg(Revenue=("Total_Amount","sum"))
    f6 = px.bar(device, x="Device_Type", y="Revenue", color="Device_Type", color_discrete_sequence=BAR_COLORS, title="Revenue by Device Type")
    f6.update_layout(showlegend=False)
    e.plotly_chart(apply_theme(f6, height=380), use_container_width=True)

    payment = filtered.groupby("Payment_Method", as_index=False).size().rename(columns={"size":"Orders"})
    f7 = px.pie(payment, names="Payment_Method", values="Orders", hole=.52, color_discrete_sequence=BAR_COLORS, title="Payment Method Preference")
    f.plotly_chart(apply_theme(f7, height=380), use_container_width=True)

    city = filtered.groupby("City", as_index=False).agg(Revenue=("Total_Amount","sum")).sort_values("Revenue", ascending=True)
    f8 = px.bar(city, x="Revenue", y="City", orientation="h", color="City", color_discrete_sequence=BAR_COLORS, title="Revenue by City")
    f8.update_layout(showlegend=False)
    st.plotly_chart(apply_theme(f8), use_container_width=True)

    st.markdown("## Customer Experience")
    g,h = st.columns(2)
    ratings = filtered["Customer_Rating"].value_counts().sort_index().reset_index()
    ratings.columns = ["Rating","Orders"]
    f9 = px.bar(ratings, x="Rating", y="Orders", color="Rating", color_continuous_scale="Blues", title="Customer Rating Distribution")
    g.plotly_chart(apply_theme(f9, height=380), use_container_width=True)

    delivery = filtered.groupby("Customer_Rating", as_index=False).agg(Avg_Delivery_Days=("Delivery_Time_Days","mean"))
    f10 = px.line(delivery, x="Customer_Rating", y="Avg_Delivery_Days", markers=True, title="Average Delivery Time by Rating")
    f10.update_traces(line=dict(color="#00C2A8", width=3), marker=dict(size=9, color="#FFD166"))
    h.plotly_chart(apply_theme(f10, height=380), use_container_width=True)

    st.markdown("## Engagement & Spending")
    i,j = st.columns(2)
    sample = filtered.sample(min(len(filtered), 600), random_state=42)
    f11 = px.scatter(sample, x="Session_Duration_Minutes", y="Total_Amount", color="Product_Category", size="Pages_Viewed",
                     color_discrete_sequence=BAR_COLORS, title="Session Duration vs Order Value")
    i.plotly_chart(apply_theme(f11, height=420), use_container_width=True)

    f12 = px.scatter(sample, x="Pages_Viewed", y="Total_Amount", color="Device_Type", size="Quantity",
                     color_discrete_sequence=BAR_COLORS, title="Pages Viewed vs Order Value")
    j.plotly_chart(apply_theme(f12, height=420), use_container_width=True)

    st.markdown("## Distribution & Customer Loyalty")
    k,l = st.columns(2)
    f13 = px.histogram(filtered, x="Total_Amount", nbins=35, title="Order Value Distribution", color_discrete_sequence=[AI_BLUE])
    k.plotly_chart(apply_theme(f13, height=380), use_container_width=True)

    loyalty = filtered.groupby("Is_Returning_Customer", as_index=False).agg(
        Median_Order=("Total_Amount","median"),
        Avg_Session=("Session_Duration_Minutes","mean"),
        Avg_Rating=("Customer_Rating","mean")
    )
    loyalty["Customer Type"] = np.where(loyalty["Is_Returning_Customer"], "Returning", "New")
    f14 = px.bar(loyalty, x="Customer Type", y="Median_Order", color="Customer Type", color_discrete_sequence=["#00E5FF","#7B61FF"], title="Median Order Value: Returning vs New")
    f14.update_layout(showlegend=False)
    l.plotly_chart(apply_theme(f14, height=380), use_container_width=True)

    st.markdown("## Relationships Between Behaviour Variables")
    corr_cols = ["Age","Session_Duration_Minutes","Pages_Viewed","Delivery_Time_Days","Customer_Rating","Total_Amount"]
    corr = filtered[corr_cols].corr(method="spearman")
    f15 = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale=["#06142F","#006CA8","#00E5FF"], title="Spearman Correlation Heatmap")
    st.plotly_chart(apply_theme(f15, height=520), use_container_width=True)

