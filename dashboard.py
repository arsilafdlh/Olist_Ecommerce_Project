
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
DATA_DIR = os.path.join(BASE_DIR, "main_data")

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

    for col in candidates:
        if col in df.columns:
            return col

    return None


def format_currency(value):
    return f"R$ {value:,.2f}"


def format_category_name(category):

    if pd.isna(category):
        return "Unknown Category"

    return str(category).replace("_", " ").title()


def show_missing_column(message):
    st.warning(message)


def create_monthly_summary(
    df,
    date_col,
    price_col,
    order_col
):

    temp = df.copy()
    temp = temp.dropna(subset=[date_col])

    temp["month"] = (
        temp[date_col]
        .dt.to_period("M")
        .astype(str)
    )

    monthly = (
        temp.groupby("month")
        .agg(
            total_sales=(price_col, "sum"),
            total_orders=(order_col, "nunique")
        )
        .reset_index()
        .sort_values("month")
    )

    return monthly


def create_category_summary(
    df,
    category_col,
    price_col
):

    category = (
        df.groupby(category_col, dropna=False)
        .agg(
            total_revenue=(price_col, "sum"),
            total_transactions=(price_col, "count")
        )
        .reset_index()
        .sort_values(
            "total_revenue",
            ascending=False
        )
    )

    category["category_display"] = (
        category[category_col].apply(format_category_name)
    )

    return category


# =========================================================
# 4. IDENTIFIKASI KOLOM DATASET
# =========================================================

sales_price_col = find_column(
    sales_df,
    ["price", "total_sales", "monetary"]
)

sales_order_col = find_column(
    sales_df,
    ["order_id"]
)

sales_date_col = find_column(
    sales_df,
    ["order_purchase_timestamp"]
)

sales_category_col = find_column(
    sales_df,
    [
        "product_category_name_english",
        "product_category_name",
        "category",
        "category_name"
    ]
)


category_name_col = find_column(
    category_sales,
    [
        "product_category_name_english",
        "product_category_name",
        "category",
        "category_name"
    ]
)

category_value_col = find_column(
    category_sales,
    [
        "total_sales",
        "total_price",
        "total_revenue",
        "transaction_value",
        "price",
        "monetary"
    ]
)


segment_name_col = find_column(
    segment_summary,
    [
        "customer_segment",
        "segment",
        "customer_value_segment"
    ]
)

segment_count_col = find_column(
    segment_summary,
    [
        "total_customers",
        "customer_count",
        "total_customer"
    ]
)

segment_monetary_col = find_column(
    segment_summary,
    [
        "average_monetary",
        "avg_monetary",
        "monetary"
    ]
)


delivery_status_col = find_column(
    delivery_summary,
    ["delivery_status"]
)

delivery_count_col = find_column(
    delivery_summary,
    [
        "total_orders",
        "order_count"
    ]
)

delivery_review_col = find_column(
    delivery_summary,
    [
        "average_review_score",
        "avg_review_score"
    ]
)


state_name_col = find_column(
    state_summary,
    [
        "customer_state",
        "state"
    ]
)

state_count_col = find_column(
    state_summary,
    [
        "total_customers",
        "customer_count",
        "total_customer"
    ]
)


geo_state_col = find_column(
    geo_summary,
    [
        "customer_state",
        "state"
    ]
)

geo_lat_col = find_column(
    geo_summary,
    [
        "geolocation_lat",
        "latitude",
        "lat",
        "avg_lat"
    ]
)

geo_lon_col = find_column(
    geo_summary,
    [
        "geolocation_lng",
        "geolocation_long",
        "longitude",
        "lng",
        "lon",
        "avg_lng"
    ]
)

geo_count_col = find_column(
    geo_summary,
    [
        "total_customers",
        "customer_count",
        "total_customer"
    ]
)


# Konversi tanggal transaksi
if sales_date_col:

    sales_df[sales_date_col] = pd.to_datetime(
        sales_df[sales_date_col],
        errors="coerce"
    )


# =========================================================
# 5. FILTER TRANSAKSI
# =========================================================

def render_transaction_filters(page_key):

    filtered_df = sales_df.copy()

    st.subheader("Filter Data")

    col1, col2, col3 = st.columns(3)

    # -----------------------------------------------------
    # FILTER TAHUN
    # -----------------------------------------------------

    if sales_date_col:

        valid_dates = filtered_df[
            sales_date_col
        ].dropna()

        available_years = sorted(
            valid_dates.dt.year.unique().tolist()
        )

        year_options = (
            ["Semua Tahun"]
            + [str(year) for year in available_years]
        )

        with col1:

            selected_year = st.selectbox(
                "Tahun Transaksi",
                options=year_options,
                index=0,
                key=f"{page_key}_year"
            )

        if selected_year != "Semua Tahun":

            filtered_df = filtered_df[
                filtered_df[sales_date_col].dt.year
                == int(selected_year)
            ]

    else:

        with col1:
            st.warning("Kolom tanggal tidak ditemukan.")

    # -----------------------------------------------------
    # FILTER BULAN
    # -----------------------------------------------------

    month_names = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember"
    }

    if sales_date_col and not filtered_df.empty:

        available_month_numbers = sorted(
            filtered_df[sales_date_col]
            .dropna()
            .dt.month
            .unique()
            .tolist()
        )

    else:

        available_month_numbers = list(range(1, 13))

    month_options = (
        ["Semua Bulan"]
        + [
            month_names[number]
            for number in available_month_numbers
        ]
    )

    with col2:

        selected_month = st.selectbox(
            "Bulan Transaksi",
            options=month_options,
            index=0,
            key=f"{page_key}_month"
        )

    if (
        selected_month != "Semua Bulan"
        and sales_date_col
    ):

        selected_month_number = [
            number
            for number, name in month_names.items()
            if name == selected_month
        ][0]

        filtered_df = filtered_df[
            filtered_df[sales_date_col].dt.month
            == selected_month_number
        ]

    # -----------------------------------------------------
    # FILTER KATEGORI PRODUK
    # -----------------------------------------------------

    if sales_category_col:

        category_mapping = {
            format_category_name(category): category
            for category in sorted(
                sales_df[sales_category_col]
                .dropna()
                .astype(str)
                .unique()
            )
        }

        category_options = (
            ["Semua Kategori"]
            + list(category_mapping.keys())
        )

        with col3:

            selected_category = st.selectbox(
                "Kategori Produk",
                options=category_options,
                index=0,
                key=f"{page_key}_category"
            )

        if selected_category != "Semua Kategori":

            original_category = category_mapping[
                selected_category
            ]

            filtered_df = filtered_df[
                filtered_df[sales_category_col].astype(str)
                == original_category
            ]

    else:

        with col3:
            st.warning("Kolom kategori produk tidak ditemukan.")

    # -----------------------------------------------------
    # INFORMASI DATA SETELAH FILTER
    # -----------------------------------------------------

    st.caption(
        f"Menampilkan {len(filtered_df):,} baris transaksi "
        f"dari total {len(sales_df):,} baris."
    )

    st.divider()

    return filtered_df


# =========================================================
# 6. SIDEBAR DAN NAVIGASI
# =========================================================

st.sidebar.title("🛍️ Olist Analytics")

st.sidebar.caption(
    "E-Commerce Performance Dashboard"
)

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

st.sidebar.caption(
    "Dataset: Olist Brazilian E-Commerce"
)

st.sidebar.caption(
    "Analysis Period: 2016–2018"
)


# =========================================================
# 7. HALAMAN OVERVIEW
# =========================================================

if page == "Overview":

    st.title("Olist E-Commerce Analytics")

    st.caption(
        "Overview of Brazilian E-Commerce Performance"
    )

    filtered_sales = render_transaction_filters(
        "overview"
    )

    # BUSINESS PERFORMANCE

    st.subheader("Business Performance")

    total_sales = (
        filtered_sales[sales_price_col].sum()
        if sales_price_col else 0
    )

    total_orders = (
        filtered_sales[sales_order_col].nunique()
        if sales_order_col else 0
    )

    total_customers = (
        filtered_sales["customer_unique_id"].nunique()
        if "customer_unique_id" in filtered_sales.columns
        else 0
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Transaction Value",
        format_currency(total_sales)
    )

    c2.metric(
        "Total Orders",
        f"{total_orders:,}"
    )

    c3.metric(
        "Total Customers",
        f"{total_customers:,}"
    )

    st.divider()

    # MONTHLY SALES OVERVIEW

    st.subheader("Monthly Sales Overview")

    if (
        sales_date_col
        and sales_price_col
        and sales_order_col
        and not filtered_sales.empty
    ):

        monthly = create_monthly_summary(
            filtered_sales,
            sales_date_col,
            sales_price_col,
            sales_order_col
        )

        col1, col2 = st.columns(2)

        with col1:

            fig = px.line(
                monthly,
                x="month",
                y="total_sales",
                markers=True,
                title="Monthly Transaction Value",
                labels={
                    "month": "Month",
                    "total_sales": "Transaction Value (R$)"
                }
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            fig = px.bar(
                monthly,
                x="month",
                y="total_orders",
                title="Monthly Order Volume",
                labels={
                    "month": "Month",
                    "total_orders": "Number of Orders"
                }
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:

        st.info(
            "Tidak ada data transaksi pada filter yang dipilih."
        )

    st.divider()

    # TOP 5 PRODUCT CATEGORIES

    st.subheader("Top 5 Product Categories")

    if (
        sales_category_col
        and sales_price_col
        and not filtered_sales.empty
    ):

        category_data = create_category_summary(
            filtered_sales,
            sales_category_col,
            sales_price_col
        )

        top_categories = category_data.head(5)

        fig = px.bar(
            top_categories.sort_values("total_revenue"),
            x="total_revenue",
            y="category_display",
            orientation="h",
            title="Top 5 Categories by Transaction Value",
            labels={
                "total_revenue": "Transaction Value (R$)",
                "category_display": "Product Category"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "Tidak ada data kategori pada filter yang dipilih."
        )


# =========================================================
# 8. HALAMAN SALES PERFORMANCE
# =========================================================

elif page == "Sales Performance":

    st.title("Sales Performance")

    st.caption(
        "Analisis perkembangan nilai transaksi dan volume pesanan."
    )

    filtered_sales = render_transaction_filters(
        "sales"
    )

    if (
        sales_date_col
        and sales_price_col
        and sales_order_col
    ):

        col1, col2 = st.columns(2)

        col1.metric(
            "Transaction Value",
            format_currency(
                filtered_sales[sales_price_col].sum()
            )
        )

        col2.metric(
            "Total Orders",
            f"{filtered_sales[sales_order_col].nunique():,}"
        )

        if not filtered_sales.empty:

            monthly = create_monthly_summary(
                filtered_sales,
                sales_date_col,
                sales_price_col,
                sales_order_col
            )

            st.divider()

            st.subheader("Monthly Transaction Value")

            fig1 = px.line(
                monthly,
                x="month",
                y="total_sales",
                markers=True,
                title="Monthly Transaction Value",
                labels={
                    "month": "Month",
                    "total_sales": "Transaction Value (R$)"
                }
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

            st.subheader("Monthly Order Volume")

            fig2 = px.bar(
                monthly,
                x="month",
                y="total_orders",
                title="Monthly Order Volume",
                labels={
                    "month": "Month",
                    "total_orders": "Number of Orders"
                }
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

            st.subheader("Monthly Transaction Data")

            st.dataframe(
                monthly,
                use_container_width=True
            )

        else:

            st.info(
                "Tidak ada data transaksi pada filter yang dipilih."
            )

    else:

        show_missing_column(
            "Kolom transaksi yang diperlukan tidak tersedia."
        )


# =========================================================
# 9. HALAMAN PRODUCT CATEGORIES
# =========================================================

elif page == "Product Categories":

    st.title("Product Categories")

    st.caption(
        "Analisis kontribusi kategori produk terhadap nilai transaksi."
    )

    filtered_sales = render_transaction_filters(
        "categories"
    )

    if (
        sales_category_col
        and sales_price_col
    ):

        if not filtered_sales.empty:

            category_display = create_category_summary(
                filtered_sales,
                sales_category_col,
                sales_price_col
            )

            max_category = min(
                20,
                len(category_display)
            )

            top_n = st.slider(
                "Jumlah kategori yang ditampilkan",
                min_value=1,
                max_value=max_category,
                value=min(10, max_category),
                key="category_top_n"
            )

            selected_category_data = (
                category_display.head(top_n)
            )

            total_category_value = (
                category_display["total_revenue"].sum()
            )

            top_value = (
                selected_category_data["total_revenue"].sum()
            )

            c1, c2 = st.columns(2)

            c1.metric(
                "Number of Categories",
                f"{len(category_display):,}"
            )

            c2.metric(
                f"Contribution of Top {top_n}",
                (
                    f"{top_value / total_category_value * 100:.2f}%"
                    if total_category_value else "0%"
                )
            )

            st.divider()

            st.subheader("Category Transaction Value")

            fig = px.bar(
                selected_category_data.sort_values(
                    "total_revenue"
                ),
                x="total_revenue",
                y="category_display",
                orientation="h",
                title=f"Top {top_n} Product Categories",
                labels={
                    "total_revenue": "Transaction Value (R$)",
                    "category_display": "Product Category"
                }
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.subheader("Category Transaction Details")

            display_table = category_display[
                [
                    "category_display",
                    "total_revenue",
                    "total_transactions"
                ]
            ].rename(
                columns={
                    "category_display": "Product Category",
                    "total_revenue": "Transaction Value (R$)",
                    "total_transactions": "Transaction Count"
                }
            )

            st.dataframe(
                display_table,
                use_container_width=True
            )

        else:

            st.info(
                "Tidak ada data kategori pada filter yang dipilih."
            )

    else:

        st.error(
            "Kolom kategori atau nilai transaksi tidak ditemukan."
        )

        st.write(
            "Kolom tersedia:",
            sales_df.columns.tolist()
        )


# =========================================================
# 10. HALAMAN CUSTOMER SEGMENTATION
# =========================================================

elif page == "Customer Segmentation":

    st.title("Customer Segmentation")

    st.caption(
        "Analisis karakteristik pelanggan berdasarkan RFM "
        "dan nilai transaksi."
    )

    st.info(
        "Ringkasan segmentasi RFM menggunakan hasil perhitungan "
        "seluruh periode dataset dan tidak berubah mengikuti "
        "filter transaksi."
    )

    if segment_name_col and segment_count_col:

        st.subheader(
            "Customer Distribution by RFM Segment"
        )

        fig = px.pie(
            segment_summary,
            names=segment_name_col,
            values=segment_count_col,
            hole=0.45,
            title="Customer Segment Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        fig = px.bar(
            segment_summary.sort_values(
                segment_count_col
            ),
            x=segment_count_col,
            y=segment_name_col,
            orientation="h",
            title="Number of Customers by Segment",
            labels={
                segment_count_col: "Number of Customers",
                segment_name_col: "Customer Segment"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("RFM Segment Summary")

        st.dataframe(
            segment_summary,
            use_container_width=True
        )

    else:

        st.warning(
            "Kolom segmen pelanggan tidak ditemukan "
            "pada segment_summary.csv."
        )

        st.write(
            "Kolom tersedia:",
            segment_summary.columns.tolist()
        )

    st.divider()

    st.subheader(
        "Customer Segmentation Based on Monetary Value"
    )

    value_name_col = find_column(
        customer_value_summary,
        [
            "customer_value_segment",
            "customer_segment",
            "segment"
        ]
    )

    value_count_col = find_column(
        customer_value_summary,
        [
            "total_customers",
            "customer_count",
            "total_customer"
        ]
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

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            customer_value_summary,
            use_container_width=True
        )

    else:

        st.info(
            "Ringkasan segmentasi Monetary belum tersedia "
            "atau nama kolomnya berbeda."
        )


# =========================================================
# 11. HALAMAN DELIVERY & REVIEWS
# =========================================================

elif page == "Delivery & Reviews":

    st.title("Delivery Performance & Customer Reviews")

    st.caption(
        "Analisis ketepatan pengiriman dan kaitannya "
        "dengan ulasan pelanggan."
    )

    st.info(
        "Ringkasan pengiriman dan ulasan menggunakan hasil "
        "perhitungan seluruh periode dataset."
    )

    if (
        delivery_status_col
        and delivery_count_col
        and delivery_review_col
    ):

        on_time = delivery_summary[
            delivery_summary[delivery_status_col]
            == "Tepat Waktu"
        ]

        late = delivery_summary[
            delivery_summary[delivery_status_col]
            == "Terlambat"
        ]

        on_time_score = (
            on_time[delivery_review_col].iloc[0]
            if len(on_time) else 0
        )

        late_score = (
            late[delivery_review_col].iloc[0]
            if len(late) else 0
        )

        total_delivery = delivery_summary[
            delivery_count_col
        ].sum()

        total_on_time = on_time[
            delivery_count_col
        ].sum()

        on_time_pct = (
            total_on_time / total_delivery * 100
            if total_delivery else 0
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total Orders Analyzed",
            f"{total_delivery:,}"
        )

        c2.metric(
            "On-Time Delivery",
            f"{on_time_pct:.2f}%"
        )

        c3.metric(
            "Review Score Gap",
            f"{on_time_score - late_score:.2f} points"
        )

        st.divider()

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

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

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

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.subheader("Delivery Summary")

        st.dataframe(
            delivery_summary,
            use_container_width=True
        )

        st.caption(
            "Perbandingan ini menunjukkan hubungan antara status "
            "pengiriman dan ulasan pelanggan, bukan bukti bahwa "
            "keterlambatan menjadi satu-satunya penyebab perubahan "
            "skor ulasan."
        )

    else:

        st.warning(
            "Kolom status pengiriman, jumlah pesanan, atau "
            "skor ulasan tidak ditemukan."
        )

        st.write(
            "Kolom tersedia:",
            delivery_summary.columns.tolist()
        )


# =========================================================
# 12. HALAMAN GEOGRAPHICAL ANALYSIS
# =========================================================

elif page == "Geographical Analysis":

    st.title("Geographical Analysis")

    st.caption(
        "Distribusi pelanggan Olist berdasarkan wilayah di Brasil."
    )

    st.info(
        "Analisis geografis menggunakan ringkasan seluruh periode "
        "dataset."
    )

    if state_name_col and state_count_col:

        state_display = state_summary.sort_values(
            state_count_col,
            ascending=False
        )

        st.subheader("Customer Distribution by State")

        fig = px.bar(
            state_display.head(15).sort_values(
                state_count_col
            ),
            x=state_count_col,
            y=state_name_col,
            orientation="h",
            title="Top 15 States by Number of Customers",
            labels={
                state_count_col: "Number of Customers",
                state_name_col: "State"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("State Customer Summary")

        st.dataframe(
            state_display,
            use_container_width=True
        )

    else:

        st.warning(
            "Kolom wilayah atau jumlah pelanggan tidak ditemukan "
            "pada state_customer_summary.csv."
        )

        st.write(
            "Kolom tersedia:",
            state_summary.columns.tolist()
        )

    st.divider()

    st.subheader("Geographical Customer Map")

    if (
        geo_state_col
        and geo_lat_col
        and geo_lon_col
    ):

        geo_display = geo_summary.copy()

        if geo_count_col:

            geo_display = geo_display.sort_values(
                geo_count_col,
                ascending=False
            )

        fig = px.scatter_geo(
            geo_display,
            lat=geo_lat_col,
            lon=geo_lon_col,
            size=geo_count_col if geo_count_col else None,
            color=geo_count_col if geo_count_col else None,
            hover_name=geo_state_col,
            scope="south america",
            title="Customer Distribution Across Brazilian States"
        )

        fig.update_geos(
            showcountries=True,
            showland=True,
            fitbounds="locations"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.warning(
            "Kolom latitude, longitude, atau wilayah tidak ditemukan "
            "pada state_geo_summary.csv."
        )

        st.write(
            "Kolom tersedia:",
            geo_summary.columns.tolist()
        )


# =========================================================
# 13. FOOTER
# =========================================================

st.divider()

st.caption(
    "Olist E-Commerce Analytics Dashboard | "
    "Dicoding Data Analysis Project"
)

st.caption(
    "Catatan: Transaction Value dihitung berdasarkan nilai "
    "price produk dan tidak termasuk biaya pengiriman."
)
