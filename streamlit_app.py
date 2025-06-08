# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import datetime

# --- Helper Function to get Insights ---
def get_insights(chart_title, df_filtered=None):
    insights = []
    if df_filtered is None or df_filtered.empty:
        return ["Tidak ada data yang tersedia untuk menghasilkan insight. Coba sesuaikan filter Anda."]

    if chart_title == "Sentiment Breakdown":
        sentiment_counts = df_filtered['sentiment'].value_counts(normalize=True)
        if not sentiment_counts.empty:
            positive_pct = sentiment_counts.get('positive', 0) * 100
            negative_pct = sentiment_counts.get('negative', 0) * 100
            neutral_pct = sentiment_counts.get('neutral', 0) * 100

            insights.append(f"Mayoritas sentimen adalah **{sentiment_counts.idxmax().capitalize()}** ({sentiment_counts.max():.1%}), menunjukkan penerimaan yang baik terhadap kampanye/konten.")
            if negative_pct > 0:
                insights.append(f"Sentimen negatif sebesar {negative_pct:.1%} mengindikasikan area yang perlu diperbaiki. Perlu dianalisis akar masalah dari konten atau respons yang menimbulkan sentimen ini.")
            else:
                insights.append("Tidak ada sentimen negatif terdeteksi, menunjukkan penerimaan yang sangat baik.")
            insights.append(f"Proporsi sentimen netral sebesar {neutral_pct:.1%} dapat mengindikasikan peluang untuk lebih mengarahkan audiens ke sentimen positif melalui *call-to-action* yang lebih jelas atau konten yang lebih memprovokasi emosi.")
        else:
            insights.append("Data sentimen tidak cukup untuk analisis.")

    elif chart_title == "Engagement Trend over Time":
        df_filtered_weekly = df_filtered.groupby(df_filtered['date'].dt.to_period('W'))['engagements'].sum().reset_index()
        df_filtered_weekly['date'] = df_filtered_weekly['date'].dt.start_time

        if not df_filtered_weekly.empty:
            if not df_filtered_weekly['engagements'].empty:
                max_engagement_date = df_filtered_weekly.loc[df_filtered_weekly['engagements'].idxmax(), 'date']
                min_engagement_date = df_filtered_weekly.loc[df_filtered_weekly['engagements'].idxmin(), 'date']
                total_engagements = df_filtered_weekly['engagements'].sum()

                insights.append(f"Tren *engagement* menunjukkan puncaknya pada minggu yang dimulai **{max_engagement_date.strftime('%d %b %Y')}**, menunjukkan waktu yang efektif untuk aktivitas kampanye tertentu.")
                insights.append(f"Terjadi penurunan *engagement* pada minggu yang dimulai **{min_engagement_date.strftime('%d %b %Y')}**, perlu diinvestigasi faktor penyebab seperti perubahan strategi, konten, atau kejadian eksternal.")
                insights.append(f"Total *engagement* dalam periode ini adalah **{total_engagements:,.0f}**. Fluktuasi *engagement* menunjukkan pentingnya konsistensi dalam produksi konten dan interaksi yang relevan.")
            else:
                insights.append("Data *engagement* tidak cukup untuk analisis tren.")
        else:
            insights.append("Data tren *engagement* tidak cukup untuk analisis.")

    elif chart_title == "Platform Engagements":
        platform_engagements = df_filtered.groupby('platform')['engagements'].sum().sort_values(ascending=True).reset_index()
        if not platform_engagements.empty:
            top_platform = platform_engagements.iloc[0]
            insights.append(f"**{top_platform['platform']}** adalah *platform* dengan *engagement* tertinggi ({top_platform['engagements']:,.0f}), menjadikannya saluran paling efektif untuk kampanye ini.")
            if len(platform_engagements) > 1:
                second_platform = platform_engagements.iloc[1]
                insights.append(f"**{second_platform['platform']}** berada di posisi kedua ({second_platform['engagements']:,.0f}), menunjukkan potensi yang baik namun mungkin masih bisa dioptimalkan.")
            if len(platform_engagements) > 2:
                 least_platform = platform_engagements.iloc[-1]
                 if least_platform['platform'] not in [top_platform['platform'], second_platform['platform']]:
                     insights.append(f"**{least_platform['platform']}** memiliki *engagement* terendah ({least_platform['engagements']:,.0f}), pertimbangkan untuk mengevaluasi kembali strategi atau alokasi sumber daya di *platform* ini.")
                 else:
                     insights.append("Diversifikasi *platform* penting untuk menjangkau audiens yang berbeda.")
            else:
                insights.append("Diversifikasi *platform* penting untuk menjangkau audiens yang berbeda, namun alokasi sumber daya harus proporsional dengan performa *engagement*.")
        else:
            insights.append("Data *engagement* per *platform* tidak cukup untuk analisis.")

    elif chart_title == "Media Type Mix":
        media_type_counts = df_filtered['media_type'].value_counts(normalize=True).reset_index()
        media_type_counts.columns = ['media_type', 'percentage']
        if not media_type_counts.empty:
            most_popular = media_type_counts.iloc[0]
            insights.append(f"**{most_popular['media_type'].capitalize()}** adalah tipe media paling populer dengan proporsi **{most_popular['percentage']:.1%}**, menunjukkan preferensi audiens yang kuat terhadap format ini.")
            if len(media_type_counts) > 1:
                second_popular = media_type_counts.iloc[1]
                insights.append(f"**{second_popular['media_type'].capitalize()}** berada di posisi kedua dengan **{second_popular['percentage']:.1%}**, yang juga merupakan format efektif untuk dipertimbangkan.")
            if len(media_type_counts) > 2:
                least_popular = media_type_counts.iloc[-1]
                if least_popular['media_type'] not in [most_popular['media_type'], second_popular['media_type']]:
                    insights.append(f"Tipe media **{least_popular['media_type'].capitalize()}** memiliki proporsi terendah (**{least_popular['percentage']:.1%}**), mungkin memerlukan eksperimen lebih lanjut atau peninjauan ulang daya tariknya.")
                else:
                    insights.append("Kombinasi berbagai tipe media dapat meningkatkan jangkauan dan daya tarik kampanye.")
            else:
                 insights.append("Kombinasi berbagai tipe media dapat meningkatkan jangkauan dan daya tarik kampanye, namun fokus harus pada format yang paling efektif.")
        else:
            insights.append("Data tipe media tidak cukup untuk analisis.")

    elif chart_title == "Top 5 Locations":
        top_locations = df_filtered.groupby('location')['engagements'].sum().nlargest(5).sort_values(ascending=True).reset_index()
        if not top_locations.empty:
            top1_loc = top_locations.iloc[0]
            insights.append(f"**{top1_loc['location']}** adalah lokasi dengan *engagement* tertinggi ({top1_loc['engagements']:,.0f}), ini adalah pasar utama yang harus terus ditargetkan dengan kuat.")
            if len(top_locations) > 1:
                top2_loc = top_locations.iloc[1]
                insights.append(f"**{top2_loc['location']}** juga menunjukkan *engagement* yang sangat tinggi ({top2_loc['engagements']:,.0f}), menjadikannya lokasi kunci kedua untuk strategi pemasaran.")
            if len(top_locations) > 2:
                remaining_eng = top_locations.iloc[2:]['engagements'].sum()
                insights.append(f"Terdapat **{len(top_locations) - 2}** lokasi lain dalam top 5 yang menyumbang total {remaining_eng:,.0f} *engagement*, menunjukkan distribusi minat geografis yang beragam.")
            else:
                insights.append("Data lokasi membantu dalam lokalisasi konten dan strategi pemasaran, mengidentifikasi pasar utama dan potensi ekspansi.")
        else:
            insights.append("Data lokasi tidak cukup untuk analisis.")

    elif chart_title == "Geographical Engagement":
        if not df_filtered.empty and 'location' in df_filtered.columns:
            location_engagements = df_filtered.groupby('location')['engagements'].sum().reset_index()
            location_engagements.columns = ['location', 'total_engagements']
            insights.append("Visualisasi geografis menunjukkan distribusi *engagement* berdasarkan lokasi.")
            insights.append("Lokasi dengan *engagement* tertinggi dapat menjadi target utama untuk kampanye lokal atau konten yang disesuaikan.")
            insights.append("Area dengan *engagement* rendah mungkin memerlukan strategi *awareness* atau eksplorasi pasar baru.")
        else:
            insights.append("Data lokasi tidak cukup untuk analisis geografis.")

    return insights

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="Media Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a modern, clean, dark blue theme ---
st.markdown("""
<style>
    /* General body and font styles */
    html, body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
        background-color: #F8F9FA; /* Very light grey, almost white */
        color: #212529; /* Dark charcoal for primary text */
    }

    /* Main content area padding and width */
    .reportview-container .main .block-container {
        padding-top: 2.5rem;
        padding-right: 3rem;
        padding-left: 3rem;
        padding-bottom: 2.5rem;
        max-width: 1200px; /* Slightly adjusted max-width for better proportion */
        margin: auto; /* Center alignment */
    }

    /* Sidebar styling */
    .css-1d391kg { /* Target sidebar background */
        background-color: #FFFFFF; /* Pure white sidebar */
        border-right: 1px solid #E0E0E0; /* Lighter border */
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); /* Soft, subtle shadow */
        border-radius: 0 12px 12px 0; /* More rounded right corners */
    }
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4, .css-1d391kg h5, .css-1d391kg h6 {
        color: #212529; /* Darker headers in sidebar */
    }
    .css-1d391kg .stSelectbox > label, .css-1d391kg .stMultiSelect > label, .css-1d391kg .stDateInput > label {
        color: #495057; /* Labels in sidebar */
        font-weight: 500;
    }

    /* Headers throughout the app */
    h1 {
        color: #0A1931; /* Dark Blue for main title */
        font-weight: 700;
        font-size: 2.8rem; /* Larger main title */
        margin-bottom: 0.8rem;
    }
    h2 {
        color: #0A1931; /* Dark Blue for section titles */
        font-weight: 600;
        font-size: 2rem;
        margin-top: 2.5rem;
        margin-bottom: 1.2rem;
    }
    h3 {
        color: #212529; /* Dark charcoal for sub-headers */
        font-weight: 600;
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    h4 { /* Used for Insight titles */
        color: #495057; /* Medium grey for insight titles */
        font-weight: 500;
        font-size: 1.2rem;
        margin-top: 1.8rem;
        margin-bottom: 0.8rem;
    }

    /* Buttons */
    .stButton>button {
        background-color: #0A1931; /* Dark Blue */
        color: white;
        padding: 0.8rem 1.8rem;
        border-radius: 10px;
        border: none;
        cursor: pointer;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: background-color 0.2s ease, transform 0.1s ease;
        box-shadow: 0 4px 12px rgba(10, 25, 49, 0.2); /* Dark blue subtle shadow */
    }
    .stButton>button:hover {
        background-color: #071324; /* Slightly darker blue on hover */
        transform: translateY(-2px); /* Lift effect */
    }
    .stButton>button:active {
        background-color: #050E1A; /* Even darker on click */
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(10, 25, 49, 0.3);
    }

    /* Alerts (Info, Success, Warning, Error) */
    .stAlert {
        border-radius: 10px;
        padding: 1.2rem;
        font-size: 0.95rem;
        border: 1px solid; /* Subtle border for clarity */
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .stAlert.info { background-color: #E6F3FF; border-color: #92B5F7; color: #0A1931; } /* Blueish tint */
    .stAlert.success { background-color: #E8FDE7; border-color: #A8E6CF; color: #388E3C; } /* Light green */
    .stAlert.warning { background-color: #FFF9E0; border-color: #FFECB3; color: #FFC107; } /* Light orange-yellow */
    .stAlert.error { background-color: #FFEBEE; border-color: #FFCDD2; color: #D32F2F; } /* Light red */

    /* Markdown text, lists */
    .stMarkdown {
        line-height: 1.7;
        color: #343A40; /* Darker grey for body text */
    }
    .stMarkdown ul {
        list-style-type: none;
        padding-left: 0;
        margin-left: 0;
    }
    .stMarkdown li {
        margin-bottom: 0.6rem;
        position: relative;
        padding-left: 1.5rem;
    }
    .stMarkdown li::before {
        content: "•";
        color: #0A1931; /* Dark Blue bullet */
        position: absolute;
        left: 0;
        font-weight: bold;
        font-size: 1.2em;
        line-height: 1; /* Align with text */
    }

    /* Input widgets (multiselect, date input, slider) */
    .stMultiSelect, .stDateInput, .stSlider {
        margin-bottom: 1.5rem;
    }
    .stMultiSelect > div > div, .stDateInput > div > label + div > div {
        border-radius: 8px;
        border: 1px solid #CED4DA; /* Subtle grey border */
        padding: 0.7rem 1rem;
        background-color: #FFFFFF;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05); /* Inner shadow for depth */
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .stMultiSelect > div > div:hover, .stDateInput > div > label + div > div:hover {
        border-color: #A0A9B3; /* Slightly darker on hover */
    }
    .stMultiSelect > div > div:focus-within, .stDateInput > div > label + div > div:focus-within {
        border-color: #0A1931; /* Dark blue on focus */
        box-shadow: 0 0 0 0.2rem rgba(10, 25, 49, 0.25); /* Blue outline on focus */
    }
    .stSlider .st-fx { /* Target slider track */
        background: #CED4DA;
    }
    .stSlider .st-ey { /* Target slider thumb */
        background: #0A1931;
        border-color: #0A1931;
    }

    /* Metric (KPI) boxes */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 1.8rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08); /* Soft shadow */
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid #E9ECEF; /* Very subtle border */
        transition: transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px); /* Subtle hover lift */
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1.05rem;
        color: #6C757D; /* Medium grey for labels */
        font-weight: 500;
        margin-bottom: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 3.5rem; /* Larger for impact */
        color: #0A1931; /* Dark blue for KPI values */
        font-weight: 700;
    }

    /* Expander style for filters */
    .streamlit-expanderContent {
        padding: 1.5rem;
    }
    .streamlit-expander {
        border-radius: 12px;
        border: 1px solid #E0E0E0;
        background-color: #FFFFFF;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }
    .streamlit-expander > button {
        font-weight: 600;
        color: #212529;
        padding: 1rem 1.2rem;
    }

    /* Dataframe style */
    .stDataFrame {
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.07);
        border: 1px solid #E8E8E8;
        overflow: hidden;
    }
    .stDataFrame > div > div > div:nth-child(2) > div {
        background-color: #F0F2F6; /* Lighter grey header */
        font-weight: 600;
        color: #343A40;
    }


    /* Remove default Streamlit 'Made with Streamlit' footer */
    footer { visibility: hidden; }

    /* Custom container/card style - this will be applied to all st.container() */
    .stContainer {
        background-color: #FFFFFF;
        border-radius: 15px; /* Consistent rounded corners */
        padding: 2.5rem; /* More generous padding */
        margin-bottom: 2.5rem; /* More space between sections */
        box-shadow: 0 8px 30px rgba(0,0,0,0.08); /* Softer, larger shadow for cards */
        border: 1px solid #E9ECEF; /* Very light border to define cards */
        color: #212529; /* Default text color inside cards */
    }
    /* Ensure headings inside containers also use dark colors */
    .stContainer h1, .stContainer h2, .stContainer h3, .stContainer h4, .stContainer p {
        color: #212529; /* Dark color for text within cards */
    }

    /* Plotly chart container styling (for better integration and avoiding "gepeng") */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #F0F0F0;
        /* Ensure responsive height/width without distorting aspect ratio */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .plotly-graph-div {
        width: 100% !important; /* Force plotly div to take 100% width of its parent */
        height: auto !important; /* Let height adjust automatically */
        min-height: 400px; /* Ensure minimum height for charts */
    }
</style>
""", unsafe_allow_html=True)

# --- Main Title ---
st.title("📊 Media Intelligence Dashboard")
st.markdown("""
Selamat datang di Dashboard Analisis Kampanye Anda. Unggah file CSV untuk mendapatkan **insight mendalam** tentang performa media Anda dengan visualisasi yang interaktif dan *actionable insights*.
""")
st.markdown("---") # Garis pemisah

# --- Bagian 1: Unggah & Pembersihan Data ---
with st.container():
    st.header("1. Unggah Data Anda")
    uploaded_file = st.file_uploader(
        "Seret & Lepas atau Klik untuk Unggah file CSV Anda",
        type=["csv"],
        help="Pastikan file CSV memiliki kolom: Date, Platform, Sentiment, Location, Engagements, Media Type."
    )

df = None # Inisialisasi DataFrame menjadi None

if uploaded_file is not None:
    with st.spinner('Memproses file dan menyiapkan dashboard... Ini mungkin memerlukan beberapa detik.'):
        try:
            df = pd.read_csv(uploaded_file)
            st.success("File berhasil diunggah!")

            with st.container():
                st.header("2. Pembersihan Data Otomatis")
                st.markdown(
                    """
                    Sistem secara otomatis melakukan pembersihan data untuk memastikan analisis yang akurat:
                    -   Mengubah kolom **'Date'** ke format tanggal yang standar.
                    -   Mengisi nilai **'Engagements'** yang kosong (missing) dengan 0.
                    -   Menormalisasi nama kolom (mengubah ke huruf kecil dan mengganti spasi dengan garis bawah) agar mudah diproses.
                    """
                )

                # --- Data Cleaning ---
                df.columns = df.columns.str.lower().str.replace(' ', '_')
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0).astype(int)
                df.dropna(subset=['date'], inplace=True)

                st.success("Pembersihan data selesai dan siap dianalisis!")
                st.subheader("Pratinjau Data Setelah Dibersihkan:")
                st.dataframe(df.head())

            st.markdown("---") # Separator

            st.header("3. Analisis Interaktif & Insight")
            st.markdown("Gunakan filter di sidebar untuk menyesuaikan tampilan data dan mendapatkan **insight yang spesifik** sesuai kebutuhan Anda.")

            # --- Sidebar: Filters ---
            st.sidebar.header("Filter Data")
            with st.sidebar.expander("Sesuaikan Filter Analisis Anda", expanded=True):
                unique_platforms = ['Semua'] + df['platform'].unique().tolist()
                selected_platforms = st.multiselect("Pilih Platform(s)", unique_platforms, default=['Semua'])

                unique_sentiments = ['Semua'] + df['sentiment'].unique().tolist()
                selected_sentiments = st.multiselect("Pilih Sentimen(s)", unique_sentiments, default=['Semua'])

                unique_media_types = ['Semua'] + df['media_type'].unique().tolist()
                selected_media_types = st.multiselect("Pilih Tipe Media(s)", unique_media_types, default=['Semua'])

                unique_locations = ['Semua'] + df['location'].unique().tolist()
                selected_locations = st.multiselect("Pilih Lokasi(s)", unique_locations, default=['Semua'])

                min_date_df = df['date'].min().date()
                max_date_df = df['date'].max().date()
                date_range_values = st.date_input(
                    "Pilih Rentang Tanggal",
                    value=(min_date_df, max_date_df),
                    min_value=min_date_df,
                    max_value=max_date_df
                )
                start_date_filter = date_range_values[0]
                end_date_filter = date_range_values[1] if len(date_range_values) > 1 else date_range_values[0]


            # Apply filters to create df_filtered
            df_filtered = df.copy()

            if 'Semua' not in selected_platforms:
                df_filtered = df_filtered[df_filtered['platform'].isin(selected_platforms)]
            if 'Semua' not in selected_sentiments:
                df_filtered = df_filtered[df_filtered['sentiment'].isin(selected_sentiments)]
            if 'Semua' not in selected_media_types:
                df_filtered = df_filtered[df_filtered['media_type'].isin(selected_media_types)]
            if 'Semua' not in selected_locations:
                df_filtered = df_filtered[df_filtered['location'].isin(selected_locations)]

            df_filtered = df_filtered[(df_filtered['date'].dt.date >= start_date_filter) &
                                      (df_filtered['date'].dt.date <= end_date_filter)]


            if df_filtered.empty:
                st.warning("Tidak ada data yang cocok dengan filter yang dipilih. Harap sesuaikan filter Anda atau unggah file CSV yang berbeda.")
            else:
                # --- Dynamic KPIs ---
                with st.container():
                    st.subheader("3.1. Key Performance Indicators (KPIs)")
                    kpi1, kpi2, kpi3 = st.columns(3)

                    with kpi1:
                        total_engagements_kpi = df_filtered['engagements'].sum()
                        st.metric(label="TOTAL ENGAGEMENTS", value=f"{total_engagements_kpi:,.0f}")

                    with kpi2:
                        unique_platforms_kpi = df_filtered['platform'].nunique()
                        st.metric(label="PLATFORM AKTIF", value=f"{unique_platforms_kpi}")

                    with kpi3:
                        num_data_points_kpi = len(df_filtered)
                        st.metric(label="JUMLAH DATA POINTS", value=f"{num_data_points_kpi:,.0f}")

                # --- Visualizations Section ---
                st.markdown("---")
                st.subheader("3.2. Visualisasi Utama")

                # --- Row 1: Sentiment Breakdown & Engagement Trend ---
                col1, col2 = st.columns(2)

                with col1:
                    with st.container():
                        st.write("### Distribusi Sentimen")
                        sentiment_counts = df_filtered['sentiment'].value_counts().reset_index()
                        sentiment_counts.columns = ['sentiment', 'count']
                        fig_sentiment = px.pie(sentiment_counts, values='count', names='sentiment',
                                               title='**Distribusi Sentimen**',
                                               color_discrete_sequence=px.colors.qualitative.Pastel)
                        fig_sentiment.update_layout(title_x=0.5, margin=dict(t=50, b=0, l=0, r=0))
                        st.plotly_chart(fig_sentiment, use_container_width=True)
                        st.markdown("#### Insight:")
                        for insight in get_insights("Sentiment Breakdown", df_filtered):
                            st.markdown(f"- {insight}")

                with col2:
                    with st.container():
                        st.write("### Tren Engagement dari Waktu ke Waktu")
                        engagement_over_time = df_filtered.groupby(df_filtered['date'].dt.to_period('W'))['engagements'].sum().reset_index()
                        engagement_over_time['date'] = engagement_over_time['date'].dt.start_time
                        fig_engagement_trend = px.line(engagement_over_time, x='date', y='engagements',
                                                     title='**Tren Engagement dari Waktu ke Waktu (Mingguan)**', markers=True,
                                                     color_discrete_sequence=["#0A1931"]) # Use Dark Blue for line
                        fig_engagement_trend.update_xaxes(title_text='Tanggal (Awal Minggu)')
                        fig_engagement_trend.update_yaxes(title_text='Total Engagements')
                        fig_engagement_trend.update_layout(title_x=0.5, margin=dict(t=50, b=0, l=0, r=0))
                        st.plotly_chart(fig_engagement_trend, use_container_width=True)
                        st.markdown("#### Insight:")
                        for insight in get_insights("Engagement Trend over Time", df_filtered):
                            st.markdown(f"- {insight}")

                # --- Row 2: Platform Engagements & Media Type Mix ---
                col3, col4 = st.columns(2)

                with col3:
                    with st.container():
                        st.write("### Engagement per Platform")
                        platform_engagements = df_filtered.groupby('platform')['engagements'].sum().sort_values(ascending=True).reset_index()
                        fig_platform = px.bar(platform_engagements, x='engagements', y='platform', orientation='h',
                                             title='**Total Engagement per Platform**',
                                             color='platform',
                                             color_discrete_sequence=px.colors.qualitative.Set2)
                        fig_platform.update_xaxes(title_text='Total Engagements')
                        fig_platform.update_yaxes(title_text='Platform', categoryarray=platform_engagements['platform'].tolist(), categoryorder="array")
                        fig_platform.update_layout(title_x=0.5, margin=dict(t=50, b=0, l=0, r=0))
                        st.plotly_chart(fig_platform, use_container_width=True)
                        st.markdown("#### Insight:")
                        for insight in get_insights("Platform Engagements", df_filtered):
                            st.markdown(f"- {insight}")

                with col4:
                    with st.container():
                        st.write("### Distribusi Tipe Media")
                        media_type_counts = df_filtered['media_type'].value_counts().reset_index()
                        media_type_counts.columns = ['media_type', 'count']
                        fig_media_type = px.pie(media_type_counts, values='count', names='media_type',
                                               title='**Distribusi Tipe Media**',
                                               color_discrete_sequence=px.colors.qualitative.Vivid)
                        fig_media_type.update_layout(title_x=0.5, margin=dict(t=50, b=0, l=0, r=0))
                        st.plotly_chart(fig_media_type, use_container_width=True)
                        st.markdown("#### Insight:")
                        for insight in get_insights("Media Type Mix", df_filtered):
                            st.markdown(f"- {insight}")

                # --- Row 3: Top 5 Locations & Geographical Engagement ---
                with st.container():
                    st.write("### Top 5 Lokasi Berdasarkan Engagement")
                    top_locations = df_filtered.groupby('location')['engagements'].sum().nlargest(5).sort_values(ascending=True).reset_index()
                    fig_locations = px.bar(top_locations, x='engagements', y='location', orientation='h',
                                          title='**Top 5 Lokasi Berdasarkan Total Engagement**',
                                          color='location',
                                          color_discrete_sequence=px.colors.qualitative.Dark24)
                    fig_locations.update_xaxes(title_text='Total Engagements')
                    fig_locations.update_yaxes(title_text='Lokasi', categoryarray=top_locations['location'].tolist(), categoryorder="array")
                    fig_locations.update_layout(title_x=0.5, margin=dict(t=50, b=0, l=0, r=0))
                    st.plotly_chart(fig_locations, use_container_width=True)
                    st.markdown("#### Insight:")
                    for insight in get_insights("Top 5 Locations", df_filtered):
                        st.markdown(f"- {insight}")

                with st.container():
                    st.write("### Peta Engagement Geografis (Eksperimental)")
                    st.info("Peta ini akan bekerja paling baik jika kolom 'Location' Anda berisi nama kota atau negara yang dapat dikenali oleh Plotly.")
                    try:
                        location_engagements_map = df_filtered.groupby('location')['engagements'].sum().reset_index()
                        location_engagements_map.columns = ['location', 'total_engagements']
                        fig_geo = px.scatter_geo(
                            location_engagements_map,
                            locations="location",
                            locationmode="country names", # Adjust based on your 'location' column data (e.g., 'country names', 'USA-states', 'ISO-3')
                            size="total_engagements",
                            hover_name="location",
                            color="total_engagements",
                            title="**Peta Engagement Berdasarkan Lokasi**",
                            projection="natural earth",
                            color_continuous_scale=px.colors.sequential.Plasma # Better color scale for geo map
                        )
                        fig_geo.update_layout(title_x=0.5, margin=dict(t=50, b=0, l=0, r=0))
                        st.plotly_chart(fig_geo, use_container_width=True)
                        st.markdown("#### Insight:")
                        for insight in get_insights("Geographical Engagement", df_filtered):
                            st.markdown(f"- {insight}")

                    except Exception as e:
                        st.warning(f"Tidak dapat membuat peta geografis: {e}. Pastikan data 'Location' Anda valid (nama kota/negara) dan konsisten.")
                        st.info("Jika data lokasi Anda tidak dikenali oleh Plotly (misalnya, hanya nama provinsi atau kode lokal), peta mungkin tidak muncul.")


                st.markdown("---")

                # --- Key Action Summary ---
                with st.container():
                    st.header("4. Ringkasan Strategi Kampanye & Tindakan Kunci")
                    st.markdown(
                        """
                        Berdasarkan analisis data yang telah dilakukan, berikut adalah ringkasan strategi kampanye dan tindakan kunci yang direkomendasikan:

                        * **Fokus pada Konten Positif:** Terus kembangkan konten yang membangkitkan sentimen positif. Identifikasi elemen kunci dari konten yang berhasil dan replikasi kesuksesan.
                        * **Optimalkan Platform Unggulan:** Alokasikan lebih banyak sumber daya dan perhatian pada *platform* yang menunjukkan *engagement* tertinggi. Pertimbangkan strategi khusus untuk mempertahankan dan meningkatkan performa di *platform* tersebut.
                        * **Diversifikasi & Eksperimen Format Media:** Meskipun ada tipe media yang dominan, terus lakukan eksperimen dengan format media lain untuk melihat respon audiens yang berbeda dan menjangkau segmen baru.
                        * **Targetkan Lokasi Kunci:** Fokuskan upaya pemasaran dan distribusi konten di lokasi-lokasi dengan *engagement* tertinggi. Pertimbangkan konten atau kampanye yang terlokalisasi untuk area ini.
                        * **Pantau Tren Engagement Berkala:** Lakukan pemantauan rutin terhadap tren *engagement* untuk mengidentifikasi pola musiman, dampak kampanye, dan anomali. Ini memungkinkan respons cepat terhadap perubahan performa.
                        * **Analisis Mendalam Sentimen Negatif (jika ada):** Jika sentimen negatif signifikan, lakukan analisis akar masalah untuk mengidentifikasi penyebabnya (misalnya, isu produk, layanan pelanggan, atau miskomunikasi) dan segera tangani.
                        """
                    )

                st.markdown("---")
                # --- Export Data Button (di Sidebar) ---
                st.sidebar.header("5. Ekspor Data")
                # Create a buffer to write to
                buffer = io.BytesIO()
                # Write DataFrame to Excel in the buffer
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_filtered.to_excel(writer, index=False, sheet_name='Filtered_Data')
                buffer.seek(0) # Rewind the buffer to the beginning

                st.sidebar.download_button(
                    label="Unduh Data yang Difilter (Excel)",
                    data=buffer,
                    file_name="filtered_media_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.sidebar.info("Data yang diunduh akan sesuai dengan filter yang Anda pilih di dashboard.")

                # --- Instructions for Downloading Dashboard (Main Content) ---
                with st.container():
                    st.header("6. Cara Mendapatkan Laporan Dashboard Anda")
                    st.markdown("""
                    Untuk mendapatkan salinan visual dari dashboard ini (termasuk grafik dan insight yang Anda lihat), Anda bisa menggunakan fitur **"Cetak ke PDF" bawaan browser** Anda:

                    1.  Tekan **`Ctrl + P`** (Windows/Linux) atau **`Cmd + P`** (Mac) pada keyboard Anda.
                    2.  Pada dialog cetak yang muncul, pilih tujuan (**"Save as PDF"** atau **"Print to PDF"**).
                    3.  Klik tombol **"Print"** atau **"Save"**.

                    Anda juga dapat mengunduh grafik individu sebagai gambar (PNG/SVG) dengan mengarahkan kursor mouse ke atas grafik dan mengklik ikon kamera (📷) yang muncul di pojok kanan atas.
                    """)


        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca atau memproses file: {e}")
            st.info("Harap pastikan file CSV Anda memiliki kolom yang benar: **'Date', 'Platform', 'Sentiment', 'Location', 'Engagements', 'Media Type'** dan format datanya valid.")

else:
    st.info("Silakan unggah file CSV Anda di sidebar untuk memulai analisis.")

st.sidebar.markdown("---")
st.sidebar.markdown("Dibuat dengan ❤️ oleh Shannon Sifra")
