
import os
import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# 1. KONFIGURASI DASHBOARD
# =========================================================

st.set_page_config(
    page_title="Olist E-Commerce Analytics",
    page_icon="🛍️",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

st.markdown("""
<style>
    .main {
        background-color: #F8F9FC;
    }
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #E5E7EB;
        padding: 18px;
        border-radius: 12px;
    }
    h1, h2, h3 {
        color: #26324A;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 2. MEMUAT DATASET
# =========================================================

@st.cache_data
def load_data():
    files = {
        "sales": "sales_data.csv",
        "monthly": "monthly_sales.csv",
        "category": "category_sales.csv",
        "rfm": "rfm_data.csv",
        "segment": "segment_summary.csv",
        "value": "customer_value_summary.csv",
        "delivery": "delivery_summary.csv",
        "state": "state_customer_summary.csv",
        "geo": "state_geo_summary.csv"
    }

    data = {}

    for key, filename in files.items():
        filepath = os.path.join(DATA_DIR, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"File {filename} tidak ditemukan di folder data."
            )

        data[key] = pd.read_csv(filepath)

    return data


try:
    data = load_data()
except Exception as e:
    st.error(f"Gagal memuat dataset: {e}")
    st.info(
        "Pastikan seluruh file CSV hasil pengolahan berada "
        "di dalam folder data yang satu lokasi dengan dashboard.py."
    )
    st.stop()


sales_df = data["sales"].copy()
monthly_sales = data["monthly"].copy()
category_sales = data["category"].copy()
rfm_df = data["rfm"].copy()
segment_summary = data["segment"].copy()
customer_value_summary = data["value"].copy()
delivery_summary = data["delivery"].copy()
state_summary = data["state"].copy()
geo_summary = data["geo"].copy()


# =========================================================
# 3. FUNGSI PENDUKUNG
# =========================================================

def find_column(df, candidates):
    """Mencari nama kolom berdasarkan beberapa kemungkinan nama."""
    for col in candidates:
        if col in df.columns:
            return col
    return None


def format_currency(value):
    return f"R$ {value:,.2f}"


def show_missing_column(message):
    st.warning(message)


# Identifikasi kolom penting
sales_price_col = find_column(
    sales_df, ["price", "total_sales", "monetary"]
)
sales_order_col = find_column(
    sales_df, ["order_id"]
)
sales_date_col = find_column(
    sales_df, ["order_purchase_timestamp"]
)

category_name_col = find_column(
    category_sales,
    ["product_category_name_english", "product_category_name",
     "category", "category_name"]
)
category_value_col = find_column(
    category_sales,
    ["total_sales", "total_price", "total_revenue",
     "transaction_value", "price", "monetary"]
)

segment_name_col = find_column(
    segment_summary,
    ["customer_segment", "segment", "customer_value_segment"]
)
segment_count_col = find_column(
    segment_summary,
    ["total_customers", "customer_count", "total_customer"]
)
segment_monetary_col = find_column(
    segment_summary,
    ["average_monetary", "avg_monetary", "monetary"]
)

delivery_status_col = find_column(
    delivery_summary, ["delivery_status"]
)
delivery_count_col = find_column(
    delivery_summary, ["total_orders", "order_count"]
)
delivery_review_col = find_column(
    delivery_summary, ["average_review_score", "avg_review_score"]
)

state_name_col = find_column(
    state_summary, ["customer_state", "state"]
)
state_count_col = find_column(
    state_summary, ["total_customers", "customer_count", "total_customer"]
)

geo_state_col = find_column(
    geo_summary, ["customer_state", "state"]
)
geo_lat_col = find_column(
    geo_summary, ["geolocation_lat", "latitude", "lat", "avg_lat"]
)
geo_lon_col = find_column(
    geo_summary, ["geolocation_lng", "geolocation_long",
                  "longitude", "lng", "lon", "avg_lng"]
)
geo_count_col = find_column(
    geo_summary, ["total_customers", "customer_count",
                  "total_customer", "customer_count"]
)


# =========================================================
# 4. SIDEBAR DAN NAVIGASI
# =========================================================

st.sidebar.title("🛍️ Olist Analytics")
st.sidebar.caption("E-Commerce Performance Dashboard")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigasi",
    [
        "Overview",
        "Sales Performance",
        "Product Categories",
        "Customer Segmentation",
        "Delivery & Reviews",
        "Geographical Analysis"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Dataset: Olist Brazilian E-Commerce")
st.sidebar.caption("Analysis Period: 2016–2018")


# =========================================================
# 5. HALAMAN OVERVIEW
# =========================================================

if page == "Overview":

    st.title("Olist E-Commerce Analytics")
    st.caption("Overview of Brazilian E-Commerce Performance")

    total_sales = sales_df[sales_price_col].sum() if sales_price_col else 0
    total_orders = (
        sales_df[sales_order_col].nunique()
        if sales_order_col else 0
    )
    total_customers = (
        rfm_df["customer_unique_id"].nunique()
        if "customer_unique_id" in rfm_df.columns else 0
    )

    average_review = 0
    if delivery_review_col and delivery_count_col:
        total_review_orders = delivery_summary[delivery_count_col].sum()
        if total_review_orders > 0:
            average_review = (
                delivery_summary[delivery_review_col] *
                delivery_summary[delivery_count_col]
            ).sum() / total_review_orders

    st.subheader("Business Performance")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Transaction Value", format_currency(total_sales))
    c2.metric("Total Orders", f"{total_orders:,}")
    c3.metric("Total Customers", f"{total_customers:,}")
    c4.metric("Average Review Score", f"{average_review:.2f} / 5")

    st.divider()

    st.subheader("Monthly Sales Overview")

    if sales_date_col and sales_price_col and sales_order_col:
        temp = sales_df.copy()
        temp[sales_date_col] = pd.to_datetime(
            temp[sales_date_col], errors="coerce"
        )
        temp = temp.dropna(subset=[sales_date_col])

        years = sorted(temp[sales_date_col].dt.year.unique())
        selected_year = st.selectbox(
            "Pilih Tahun Transaksi",
            ["All Years"] + [int(y) for y in years],
            key="overview_year"
        )

        if selected_year != "All Years":
            temp = temp[temp[sales_date_col].dt.year == selected_year]

        monthly = (
            temp.assign(
                month=temp[sales_date_col].dt.to_period("M").astype(str)
            )
            .groupby("month")
            .agg(
                total_sales=(sales_price_col, "sum"),
                total_orders=(sales_order_col, "nunique")
            )
            .reset_index()
        )

        c1, c2 = st.columns(2)

        with c1:
            fig = px.line(
                monthly, x="month", y="total_sales",
                markers=True, title="Monthly Transaction Value",
                labels={"month": "Month", "total_sales": "Value (R$)"}
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig = px.bar(
                monthly, x="month", y="total_orders",
                title="Monthly Order Volume",
                labels={"month": "Month", "total_orders": "Orders"}
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Top 5 Product Categories")

    if category_name_col and category_value_col:
        top = category_sales.nlargest(5, category_value_col)
        fig = px.bar(
            top.sort_values(category_value_col),
            x=category_value_col,
            y=category_name_col,
            orientation="h",
            title="Top 5 Categories by Transaction Value",
            labels={
                category_value_col: "Transaction Value (R$)",
                category_name_col: "Product Category"
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        show_missing_column(
            "Kolom kategori atau nilai transaksi tidak ditemukan."
        )


# =========================================================
# 6. HALAMAN SALES PERFORMANCE
# =========================================================

elif page == "Sales Performance":

    st.title("Sales Performance")
    st.caption("Analisis perkembangan nilai transaksi dan volume pesanan.")

    if sales_date_col and sales_price_col and sales_order_col:

        temp = sales_df.copy()
        temp[sales_date_col] = pd.to_datetime(
            temp[sales_date_col], errors="coerce"
        )
        temp = temp.dropna(subset=[sales_date_col])

        years = sorted(temp[sales_date_col].dt.year.unique())
        selected_year = st.selectbox(
            "Pilih Tahun",
            ["All Years"] + [int(y) for y in years],
            key="sales_year"
        )

        if selected_year != "All Years":
            temp = temp[temp[sales_date_col].dt.year == selected_year]

        monthly = (
            temp.assign(
                month=temp[sales_date_col].dt.to_period("M").astype(str)
            )
            .groupby("month")
            .agg(
                total_sales=(sales_price_col, "sum"),
                total_orders=(sales_order_col, "nunique")
            )
            .reset_index()
        )

        col1, col2 = st.columns(2)
        col1.metric(
            "Transaction Value",
            format_currency(temp[sales_price_col].sum())
        )
        col2.metric(
            "Total Orders",
            f"{temp[sales_order_col].nunique():,}"
        )

        fig1 = px.line(
            monthly, x="month", y="total_sales",
            markers=True, title="Monthly Transaction Value",
            labels={"month": "Month", "total_sales": "Value (R$)"}
        )
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.bar(
            monthly, x="month", y="total_orders",
            title="Monthly Order Volume",
            labels={"month": "Month", "total_orders": "Orders"}
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Monthly Transaction Data")
        st.dataframe(monthly, use_container_width=True)

    else:
        show_missing_column("Kolom transaksi yang diperlukan tidak tersedia.")


# =========================================================
# 7. HALAMAN PRODUCT CATEGORIES
# =========================================================

elif page == "Product Categories":

    st.title("Product Categories")
    st.caption("Analisis kontribusi kategori produk terhadap nilai transaksi.")

    if category_name_col and category_value_col:

        category_display = category_sales.copy()
        category_display = category_display.sort_values(
            category_value_col, ascending=False
        )

        top_n = st.slider(
            "Jumlah kategori yang ditampilkan",
            min_value=5,
            max_value=min(20, len(category_display)),
            value=min(10, len(category_display))
        )

        selected_categories = category_display.head(top_n)

        total_category_value = category_display[category_value_col].sum()
        top_value = selected_categories[category_value_col].sum()

        c1, c2 = st.columns(2)
        c1.metric("Number of Categories", f"{len(category_display):,}")
        c2.metric(
            f"Contribution of Top {top_n}",
            f"{top_value / total_category_value * 100:.2f}%"
            if total_category_value else "0%"
        )

        fig = px.bar(
            selected_categories.sort_values(category_value_col),
            x=category_value_col,
            y=category_name_col,
            orientation="h",
            title=f"Top {top_n} Product Categories",
            labels={
                category_value_col: "Transaction Value (R$)",
                category_name_col: "Product Category"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Category Transaction Details")
        st.dataframe(category_display, use_container_width=True)

    else:
        st.error(
            "Kolom kategori atau nilai transaksi tidak ditemukan. "
            "Periksa isi category_sales.csv."
        )
        st.write("Kolom yang tersedia:", category_sales.columns.tolist())


# =========================================================
# 8. HALAMAN CUSTOMER SEGMENTATION
# =========================================================

elif page == "Customer Segmentation":

    st.title("Customer Segmentation")
    st.caption("Analisis karakteristik pelanggan berdasarkan RFM dan nilai transaksi.")

    if segment_name_col and segment_count_col:

        st.subheader("Customer Distribution by RFM Segment")

        fig = px.pie(
            segment_summary,
            names=segment_name_col,
            values=segment_count_col,
            hole=0.45,
            title="Customer Segment Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

        fig = px.bar(
            segment_summary.sort_values(segment_count_col),
            x=segment_count_col,
            y=segment_name_col,
            orientation="h",
            title="Number of Customers by Segment",
            labels={
                segment_count_col: "Number of Customers",
                segment_name_col: "Customer Segment"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("RFM Segment Summary")
        st.dataframe(segment_summary, use_container_width=True)

    else:
        st.warning(
            "Kolom segmen pelanggan tidak ditemukan pada segment_summary.csv."
        )
        st.write("Kolom tersedia:", segment_summary.columns.tolist())

    st.divider()
    st.subheader("Customer Segmentation Based on Monetary Value")

    value_name_col = find_column(
        customer_value_summary,
        ["customer_value_segment", "customer_segment", "segment"]
    )
    value_count_col = find_column(
        customer_value_summary,
        ["total_customers", "customer_count", "total_customer"]
    )

    if value_name_col and value_count_col:
        fig = px.bar(
            customer_value_summary,
            x=value_name_col,
            y=value_count_col,
            text=value_count_col,
            title="Customer Distribution Based on Monetary Value",
            labels={
                value_name_col: "Customer Value Segment",
                value_count_col: "Number of Customers"
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(customer_value_summary, use_container_width=True)
    else:
        st.info(
            "Ringkasan segmentasi Monetary belum tersedia "
            "atau nama kolomnya berbeda."
        )


# =========================================================
# 9. HALAMAN DELIVERY & REVIEWS
# =========================================================

elif page == "Delivery & Reviews":

    st.title("Delivery Performance & Customer Reviews")
    st.caption("Analisis ketepatan pengiriman dan kaitannya dengan ulasan pelanggan.")

    if delivery_status_col and delivery_count_col and delivery_review_col:

        on_time = delivery_summary[
            delivery_summary[delivery_status_col] == "Tepat Waktu"
        ]
        late = delivery_summary[
            delivery_summary[delivery_status_col] == "Terlambat"
        ]

        on_time_score = (
            on_time[delivery_review_col].iloc[0] if len(on_time) else 0
        )
        late_score = (
            late[delivery_review_col].iloc[0] if len(late) else 0
        )

        total_delivery = delivery_summary[delivery_count_col].sum()
        total_on_time = on_time[delivery_count_col].sum()
        on_time_pct = (
            total_on_time / total_delivery * 100
            if total_delivery else 0
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Orders Analyzed", f"{total_delivery:,}")
        c2.metric("On-Time Delivery", f"{on_time_pct:.2f}%")
        c3.metric(
            "Review Score Gap",
            f"{on_time_score - late_score:.2f} points"
        )

        fig1 = px.bar(
            delivery_summary,
            x=delivery_status_col,
            y=delivery_count_col,
            color=delivery_status_col,
            text=delivery_count_col,
            title="Number of Orders by Delivery Status",
            labels={
                delivery_status_col: "Delivery Status",
                delivery_count_col: "Number of Orders"
            }
        )
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.bar(
            delivery_summary,
            x=delivery_status_col,
            y=delivery_review_col,
            color=delivery_status_col,
            text_auto=".2f",
            title="Average Review Score by Delivery Status",
            labels={
                delivery_status_col: "Delivery Status",
                delivery_review_col: "Average Review Score"
            }
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Delivery Summary")
        st.dataframe(delivery_summary, use_container_width=True)

        st.caption(
            "Perbandingan ini menunjukkan hubungan antara status pengiriman "
            "dan ulasan pelanggan, bukan bukti bahwa keterlambatan "
            "menjadi satu-satunya penyebab perubahan skor ulasan."
        )

    else:
        st.warning(
            "Kolom status pengiriman, jumlah pesanan, atau skor ulasan "
            "tidak ditemukan."
        )
        st.write("Kolom tersedia:", delivery_summary.columns.tolist())


# =========================================================
# 10. HALAMAN GEOGRAPHICAL ANALYSIS
# =========================================================

elif page == "Geographical Analysis":

    st.title("Geographical Analysis")
    st.caption("Distribusi pelanggan Olist berdasarkan wilayah di Brasil.")

    if state_name_col and state_count_col:

        state_display = state_summary.sort_values(
            state_count_col, ascending=False
        )

        st.subheader("Customer Distribution by State")

        fig = px.bar(
            state_display.head(15).sort_values(state_count_col),
            x=state_count_col,
            y=state_name_col,
            orientation="h",
            title="Top 15 States by Number of Customers",
            labels={
                state_count_col: "Number of Customers",
                state_name_col: "State"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("State Customer Summary")
        st.dataframe(state_display, use_container_width=True)

    else:
        st.warning(
            "Kolom wilayah atau jumlah pelanggan tidak ditemukan "
            "pada state_customer_summary.csv."
        )
        st.write("Kolom tersedia:", state_summary.columns.tolist())

    st.divider()
    st.subheader("Geographical Customer Map")

    if geo_state_col and geo_lat_col and geo_lon_col:

        geo_display = geo_summary.copy()

        if geo_count_col:
            geo_display = geo_display.sort_values(
                geo_count_col, ascending=False
            )

        fig = px.scatter_geo(
            geo_display,
            lat=geo_lat_col,
            lon=geo_lon_col,
            size=geo_count_col if geo_count_col else None,
            color=geo_count_col if geo_count_col else None,
            hover_name=geo_state_col,
            scope="south america",
            title="Customer Distribution Across Brazilian States",
            labels={
                geo_state_col: "State",
                geo_count_col: "Number of Customers"
            } if geo_count_col else {}
        )

        fig.update_geos(
            showcountries=True,
            showland=True,
            fitbounds="locations"
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning(
            "Kolom latitude, longitude, atau wilayah tidak ditemukan "
            "pada state_geo_summary.csv."
        )
        st.write("Kolom tersedia:", geo_summary.columns.tolist())


# =========================================================
# 11. FOOTER
# =========================================================

st.divider()
st.caption(
    "Olist E-Commerce Analytics Dashboard | "
    "Dicoding Data Analysis Project"
)
st.caption(
    "Catatan: Transaction Value dihitung berdasarkan nilai price "
    "produk dan tidak termasuk biaya pengiriman."
)
