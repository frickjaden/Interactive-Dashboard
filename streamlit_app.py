# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import datetime

# --- Helper Function to get Insights ---
# PERHATIAN: Pastikan Anda mengisi logika fungsi ini sesuai dengan implementasi Anda.
# Saya berasumsi Anda sudah memiliki fungsi ini, jadi saya hanya menyertakan templatenya.
def get_insights(chart_title, df_filtered=None):
    insights = {
        "Headline Analysis": "Total headline analysis shows a balanced sentiment distribution, with a slight dominance of positive mentions.",
        "Keyword Trends": "Key topics like 'E-commerce', 'Digital Transformation', and 'AI' are showing increased traction over the last quarter.",
        "Sentiment Over Time": "Sentiment dipped slightly in mid-May but has since recovered, indicating effective crisis management or positive news cycles.",
        "Source Performance": "News aggregators and tech blogs are the most influential sources, contributing to 60% of the positive mentions.",
        "Media Reach": "The overall media reach has expanded by 15% month-over-month, reaching a broader audience across online platforms."
    }
    return insights.get(chart_title, "No specific insight available for this chart.")

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="Media Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load custom CSS ---
# Baris ini yang paling penting untuk memuat style.css
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- Page State Management for Sidebar Navigation ---
if 'page' not in st.session_state:
    st.session_state.page = 'home' # Default page

# --- Sidebar Content ---
st.sidebar.title("MENU ANALISIS")

# Custom navigation using st.radio for "capsule" style
# The labels are now just text, as the icons were previously rendered by CSS
page_selection = st.sidebar.radio(
    "Navigasi",
    [
        "Home",
        "Upload Data",
        "Dashboard Overview",
        "Headline Analysis",
        "Keyword Trends",
        "Sentiment Over Time",
        "Source Performance",
        "Media Reach",
        "Settings",
        "Help"
    ],
    index=["Home", "Upload Data", "Dashboard Overview", "Headline Analysis", "Keyword Trends", "Sentiment Over Time", "Source Performance", "Media Reach", "Settings", "Help"].index(st.session_state.page),
    key="main_navigation"
)

if page_selection:
    st.session_state.page = page_selection

# --- Main Content Area ---

# Page: Home
if st.session_state.page == 'Home':
    st.title("Selamat Datang di Media Intelligence Dashboard")
    st.write("Gunakan dashboard ini untuk menganalisis data media Anda.")

    st.markdown("""
        <div class="stContainer">
            <h3>Overview</h3>
            <p>Aplikasi ini dirancang untuk membantu Anda memahami lanskap media, melacak tren, dan mengidentifikasi wawasan utama dari data berita dan publikasi.</p>
            <p>Pilih "Upload Data" dari sidebar untuk memulai dengan data Anda sendiri.</p>
            <br>
            <button class="hero-button" onclick="window.location.href='#upload-data'">Mulai Analisis</button>
        </div>
    """, unsafe_allow_html=True) # Menggunakan tombol HTML dengan kelas CSS

    st.subheader("Fitur Utama:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            - **Analisis Sentimen:** Pahami bagaimana merek atau topik Anda dipersepsikan.
            - **Identifikasi Kata Kunci:** Temukan kata kunci dan frasa yang paling relevan.
            - **Tren Waktu:** Lihat perubahan sentimen dan volume seiring waktu.
        """)
    with col2:
        st.markdown("""
            - **Kinerja Sumber:** Identifikasi sumber media yang paling berpengaruh.
            - **Jangkauan Media:** Ukur seberapa luas liputan Anda.
            - **Dashboard Interaktif:** Visualisasi data yang menarik dan mudah dipahami.
        """)


# Page: Upload Data
elif st.session_state.page == 'Upload Data':
    st.title("Unggah Data Anda")
    st.markdown("Unggah file Excel Anda di sini untuk memulai analisis.")

    uploaded_file = st.file_uploader("Pilih file Excel", type=["xlsx"])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.session_state.df = df # Store DataFrame in session_state
            st.success("File berhasil diunggah!")
            st.write("Pratinjau Data:")
            st.dataframe(df.head())

            # Optionally, move to Dashboard Overview after upload
            if st.button("Lihat Dashboard"):
                st.session_state.page = 'Dashboard Overview'
                st.experimental_rerun() # Rerun to navigate to the new page
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")
            st.info("Pastikan file Excel Anda berformat benar.")

# All subsequent pages require data
if 'df' not in st.session_state and st.session_state.page not in ['Home', 'Upload Data', 'Settings', 'Help']:
    st.warning("Silakan unggah data Anda terlebih dahulu di halaman 'Upload Data'.")
    st.stop() # Stop execution if data is not available for analysis pages
else:
    df = st.session_state.get('df') # Get DataFrame from session state for analysis pages

    # --- Filtering Options (Common for Dashboard & Analysis Pages) ---
    if st.session_state.page in ['Dashboard Overview', 'Headline Analysis', 'Keyword Trends', 'Sentiment Over Time', 'Source Performance', 'Media Reach']:
        with st.expander("Filter Data"):
            if df is not None:
                # Assuming 'Date' column exists and is in datetime format
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                    min_date = df['Date'].min().date() if not df['Date'].min() == pd.NaT else datetime.date(2020, 1, 1) # Fallback
                    max_date = df['Date'].max().date() if not df['Date'].max() == pd.NaT else datetime.date.today() # Fallback

                    date_range = st.date_input(
                        "Pilih Rentang Tanggal",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )

                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        df_filtered = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
                    else:
                        df_filtered = df.copy()
                else:
                    st.warning("Kolom 'Date' tidak ditemukan atau tidak valid. Filter tanggal tidak tersedia.")
                    df_filtered = df.copy()

                # Example of other filters (adjust to your actual columns)
                if 'Category' in df.columns:
                    selected_categories = st.multiselect("Pilih Kategori", df['Category'].unique(), default=df['Category'].unique())
                    df_filtered = df_filtered[df_filtered['Category'].isin(selected_categories)]

                if 'Source' in df.columns:
                    selected_sources = st.multiselect("Pilih Sumber", df['Source'].unique(), default=df['Source'].unique())
                    df_filtered = df_filtered[df_filtered['Source'].isin(selected_sources)]

                st.write(f"Data yang difilter: {len(df_filtered)} baris")
            else:
                st.warning("Tidak ada data untuk difilter.")
                df_filtered = pd.DataFrame() # Empty DataFrame if no data
    else:
        df_filtered = df # No filtering for pages like Home, Upload, Settings, Help


    # --- Dashboard Overview Page ---
    if st.session_state.page == 'Dashboard Overview':
        st.title("Dashboard Overview")
        if not df_filtered.empty:
            # Example KPIs
            total_articles = len(df_filtered)
            avg_sentiment_score = df_filtered['Sentiment_Score'].mean() if 'Sentiment_Score' in df_filtered.columns else 0 # Assuming 'Sentiment_Score'
            unique_sources = df_filtered['Source'].nunique() if 'Source' in df_filtered.columns else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Artikel", value=f"{total_articles:,}")
            with col2:
                st.metric(label="Rata-rata Sentimen", value=f"{avg_sentiment_score:.2f}")
            with col3:
                st.metric(label="Sumber Unik", value=f"{unique_sources:,}")

            st.markdown("---")

            st.header("Ringkasan Visual")

            # Example Chart 1: Sentiment Distribution (Assuming 'Sentiment' column: Positive, Negative, Neutral)
            if 'Sentiment' in df_filtered.columns:
                st.subheader("Distribusi Sentimen")
                sentiment_counts = df_filtered['Sentiment'].value_counts().reset_index()
                sentiment_counts.columns = ['Sentiment', 'Count']
                fig_sentiment = px.pie(
                    sentiment_counts,
                    values='Count',
                    names='Sentiment',
                    title='Distribusi Sentimen Berdasarkan Artikel',
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    hole=0.3 # Donut chart
                )
                fig_sentiment.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="#E0E0E0",
                    legend_title_text='Sentimen',
                    margin=dict(l=20, r=20, t=60, b=20)
                )
                st.plotly_chart(fig_sentiment, use_container_width=True)
                st.info(get_insights("Sentiment Distribution"))

            # Example Chart 2: Top Keywords (Assuming 'Keywords' column, possibly comma-separated)
            if 'Keywords' in df_filtered.columns:
                st.subheader("Kata Kunci Teratas")
                # Simple keyword extraction (adjust if your 'Keywords' column is different)
                all_keywords = df_filtered['Keywords'].dropna().str.split(', ').explode()
                keyword_counts = all_keywords.value_counts().head(10).reset_index()
                keyword_counts.columns = ['Keyword', 'Count']
                fig_keywords = px.bar(
                    keyword_counts,
                    x='Count',
                    y='Keyword',
                    orientation='h',
                    title='10 Kata Kunci Teratas',
                    color_discrete_sequence=['#4A90E2']
                )
                fig_keywords.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="#E0E0E0",
                    margin=dict(l=20, r=20, t=60, b=20)
                )
                st.plotly_chart(fig_keywords, use_container_width=True)
                st.info(get_insights("Keyword Trends"))

        else:
            st.info("Tidak ada data yang tersedia untuk ditampilkan di dashboard. Silakan unggah data terlebih dahulu.")

    # Page: Headline Analysis
    elif st.session_state.page == 'Headline Analysis':
        st.title("Analisis Headline")
        if not df_filtered.empty:
            # Assuming 'Headline' column exists
            if 'Headline' in df_filtered.columns:
                st.subheader("Headline Terbaru")
                st.dataframe(df_filtered[['Date', 'Source', 'Headline', 'Sentiment']].head(20)) # Display top 20 headlines

                # Example: Word Cloud or N-gram analysis could go here
                st.subheader("Analisis Frekuensi Kata dalam Headline")
                st.info(get_insights("Headline Analysis"))
            else:
                st.warning("Kolom 'Headline' tidak ditemukan dalam data Anda.")
        else:
            st.info("Tidak ada data yang tersedia untuk analisis headline.")

    # Page: Keyword Trends
    elif st.session_state.page == 'Keyword Trends':
        st.title("Tren Kata Kunci")
        if not df_filtered.empty:
            if 'Keywords' in df_filtered.columns and 'Date' in df_filtered.columns:
                st.subheader("Tren Kata Kunci Populer Seiring Waktu")
                # Example: Plotting keyword counts over time
                # This requires more complex logic to aggregate keywords by date.
                # For simplicity, let's just show top keywords again, or mention where a more complex chart would go.
                st.info("Ini adalah tempat untuk menampilkan tren kata kunci teratas seiring waktu (misalnya, menggunakan area chart atau line chart).")
                st.info(get_insights("Keyword Trends"))
            else:
                st.warning("Kolom 'Keywords' atau 'Date' tidak ditemukan dalam data Anda.")
        else:
            st.info("Tidak ada data yang tersedia untuk analisis tren kata kunci.")

    # Page: Sentiment Over Time
    elif st.session_state.page == 'Sentiment Over Time':
        st.title("Sentimen Seiring Waktu")
        if not df_filtered.empty:
            if 'Date' in df_filtered.columns and 'Sentiment' in df_filtered.columns:
                st.subheader("Tren Sentimen Harian/Mingguan")
                # Ensure 'Date' is datetime and set as index for resampling
                df_filtered_sentiment = df_filtered.copy()
                df_filtered_sentiment['Date'] = pd.to_datetime(df_filtered_sentiment['Date'])
                df_filtered_sentiment.set_index('Date', inplace=True)

                # Example: Calculate daily sentiment distribution
                sentiment_daily = df_filtered_sentiment.groupby([pd.Grouper(freq='D'), 'Sentiment']).size().unstack(fill_value=0)
                sentiment_daily = sentiment_daily.apply(lambda x: x / x.sum(), axis=1).fillna(0) # Convert to percentages

                fig_sentiment_time = px.area(
                    sentiment_daily,
                    title='Distribusi Sentimen Harian',
                    color_discrete_map={
                        'Positive': '#4CAF50',
                        'Negative': '#D32F2F',
                        'Neutral': '#FFA000'
                    }
                )
                fig_sentiment_time.update_layout(
                    xaxis_title="Tanggal",
                    yaxis_title="Proporsi Sentimen",
                    hovermode="x unified",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="#E0E0E0",
                    margin=dict(l=20, r=20, t=60, b=20)
                )
                st.plotly_chart(fig_sentiment_time, use_container_width=True)
                st.info(get_insights("Sentiment Over Time"))
            else:
                st.warning("Kolom 'Date' atau 'Sentiment' tidak ditemukan dalam data Anda.")
        else:
            st.info("Tidak ada data yang tersedia untuk analisis sentimen seiring waktu.")

    # Page: Source Performance
    elif st.session_state.page == 'Source Performance':
        st.title("Kinerja Sumber Media")
        if not df_filtered.empty:
            if 'Source' in df_filtered.columns and 'Sentiment' in df_filtered.columns:
                st.subheader("Sentimen Berdasarkan Sumber")
                source_sentiment = df_filtered.groupby(['Source', 'Sentiment']).size().unstack(fill_value=0)
                source_sentiment['Total'] = source_sentiment.sum(axis=1)
                source_sentiment_sorted = source_sentiment.sort_values(by='Total', ascending=False).head(10) # Top 10 sources

                fig_source = px.bar(
                    source_sentiment_sorted.reset_index(),
                    x='Total',
                    y='Source',
                    color='Sentiment',
                    title='Sentimen Berdasarkan Sumber Media (Top 10)',
                    orientation='h',
                    color_discrete_map={
                        'Positive': '#4CAF50',
                        'Negative': '#D32F2F',
                        'Neutral': '#FFA000'
                    }
                )
                fig_source.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="#E0E0E0",
                    margin=dict(l=20, r=20, t=60, b=20)
                )
                st.plotly_chart(fig_source, use_container_width=True)
                st.info(get_insights("Source Performance"))
            else:
                st.warning("Kolom 'Source' atau 'Sentiment' tidak ditemukan dalam data Anda.")
        else:
            st.info("Tidak ada data yang tersedia untuk analisis kinerja sumber.")

    # Page: Media Reach
    elif st.session_state.page == 'Media Reach':
        st.title("Jangkauan Media")
        if not df_filtered.empty:
            # Assuming 'Reach' or 'Impressions' column
            if 'Reach' in df_filtered.columns: # Or calculate based on unique sources/articles
                st.subheader("Jangkauan Media Keseluruhan")
                total_reach = df_filtered['Reach'].sum()
                st.metric(label="Total Jangkauan Diperkirakan", value=f"{total_reach:,.0f}")

                st.subheader("Jangkauan Berdasarkan Waktu")
                # Example: Time series of total reach
                df_filtered_reach = df_filtered.copy()
                df_filtered_reach['Date'] = pd.to_datetime(df_filtered_reach['Date'])
                df_filtered_reach.set_index('Date', inplace=True)
                daily_reach = df_filtered_reach.resample('D')['Reach'].sum().reset_index()

                fig_reach_time = px.line(
                    daily_reach,
                    x='Date',
                    y='Reach',
                    title='Total Jangkauan Harian',
                    line_shape="spline",
                    color_discrete_sequence=['#4A90E2']
                )
                fig_reach_time.update_layout(
                    xaxis_title="Tanggal",
                    yaxis_title="Jangkauan",
                    hovermode="x unified",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="#E0E0E0",
                    margin=dict(l=20, r=20, t=60, b=20)
                )
                st.plotly_chart(fig_reach_time, use_container_width=True)
                st.info(get_insights("Media Reach"))

            else:
                st.warning("Kolom 'Reach' tidak ditemukan dalam data Anda. Tidak dapat menghitung jangkauan media.")
        else:
            st.info("Tidak ada data yang tersedia untuk analisis jangkauan media.")

    # Page: Settings
    elif st.session_state.page == 'Settings':
        st.title("Pengaturan")
        st.write("Di sini Anda dapat mengelola pengaturan aplikasi.")
        st.warning("Fitur pengaturan belum diimplementasikan sepenuhnya.")
        # Example settings (dummy)
        theme_option = st.radio("Pilih Tema", ["Dark", "Light"], index=0)
        if theme_option == "Light":
            st.info("Mode terang belum didukung sepenuhnya oleh CSS ini. Disarankan menggunakan mode gelap.")

    # Page: Help
    elif st.session_state.page == 'Help':
        st.title("Bantuan")
        st.write("Butuh bantuan? Silakan hubungi tim dukungan kami atau lihat dokumentasi.")
        st.markdown("""
            ### Pertanyaan Umum
            - **Bagaimana cara mengunggah data?**
              Pilih opsi "Upload Data" dari menu sidebar, lalu klik "Pilih file Excel" untuk memilih file Anda.
            - **Format data yang didukung?**
              Saat ini hanya mendukung file Excel (.xlsx) dengan kolom yang relevan seperti 'Date', 'Headline', 'Sentiment', 'Keywords', 'Source', 'Sentiment_Score', dan 'Reach'.
            - **Bagaimana cara mendapatkan wawasan dari dashboard?**
              Setiap visualisasi dilengkapi dengan penjelasan singkat (insights) di bawahnya. Anda juga dapat menggunakan filter untuk mengeksplorasi data lebih dalam.
            ---
            Kontak Dukungan: shannonsifra@gmail.com
        """)
