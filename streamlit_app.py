# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import datetime

# --- Helper Function to get Insights ---
def get_insights(chart_title, df_filtered=None):
    insights = {
        "Data Overview": "Bagian ini menyajikan gambaran menyeluruh dari data media Anda, mencakup sentimen, tren, dan jangkauan.",
        "Distribusi Sentimen": "Distribusi sentimen berdasarkan artikel memberikan gambaran cepat tentang proporsi pandangan positif, negatif, dan netral secara keseluruhan.",
        "Kata Kunci Teratas": "Visualisasi kata kunci teratas menyoroti fokus utama diskusi dan isu yang paling relevan dalam dataset Anda.",
        "Tren Sentimen Harian": "Tren sentimen dari waktu ke waktu menunjukkan fluktuasi yang perlu dipantau untuk memahami dampak peristiwa atau kampanye.",
        "Sentimen Berdasarkan Sumber": "Beberapa sumber media memiliki dampak yang lebih besar pada sentimen, mengindikasikan pentingnya menganalisis asal liputan.",
        "Total Jangkauan Harian": "Jangkauan media yang terus meningkat menunjukkan keberhasilan dalam menjangkau audiens yang lebih luas seiring waktu.",
        "Total Artikel": "Angka total artikel menunjukkan volume liputan media yang diterima dalam periode yang dipilih.",
        "Rata-rata Sentimen": "Rata-rata sentimen memberikan indikator numerik singkat tentang keseluruhan nada liputan media.",
        "Sumber Unik": "Jumlah sumber unik menunjukkan keberagaman atau konsentrasi sumber yang meliput topik Anda."
    }
    return insights.get(chart_title, "Tidak ada wawasan spesifik yang tersedia untuk grafik ini.")

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="Media Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load custom CSS ---
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    st.error("File 'style.css' tidak ditemukan. Pastikan file tersebut berada di direktori yang sama dengan 'streamlit_app.py'.")
    st.stop() # Hentikan eksekusi jika CSS tidak dapat dimuat

# --- Page State Management for Sidebar Navigation ---
page_options = [
    "Home",
    "Upload Data",
    "Data Overview", # Consolidated all analysis here
    "Settings",
    "Help"
]

if 'page' not in st.session_state or st.session_state.page not in page_options:
    st.session_state.page = 'Home'

# --- Sidebar Content ---
st.sidebar.title("MENU ANALISIS")

try:
    current_page_index = page_options.index(st.session_state.page)
except ValueError:
    current_page_index = 0
    st.session_state.page = page_options[current_page_index]

page_selection = st.sidebar.radio(
    "Navigasi",
    page_options,
    index=current_page_index,
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
            <p>Untuk memulai, unggah data Anda.</p>
            <br>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Mulai Analisis", key="start_analysis_button"):
        st.session_state.page = 'Upload Data'
        st.experimental_rerun()

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
    st.markdown("Unggah file Excel (.xlsx) atau CSV (.csv) Anda di sini untuk memulai analisis.")

    uploaded_file = st.file_uploader("Pilih file data", type=["xlsx", "csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                st.error("Format file tidak didukung. Harap unggah file .xlsx atau .csv.")
                df = None

            if df is not None:
                st.session_state.df = df
                st.success("File berhasil diunggah!")
                st.write("Pratinjau Data:")
                st.dataframe(df.head())

                if st.button("Lihat Data Overview", key="view_dashboard_button"):
                    st.session_state.page = 'Data Overview' # Navigate to the new consolidated page
                    st.experimental_rerun()
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")
            st.info("Pastikan file Anda berformat benar dan tidak rusak, serta sesuai dengan ekspektasi kolom.")

# All analysis consolidated in 'Data Overview' page
elif st.session_state.page == 'Data Overview':
    st.title("Data Overview: Analisis Media Lengkap")
    st.info(get_insights("Data Overview"))

    # Ensure data is available before proceeding
    if 'df' not in st.session_state or st.session_state.df.empty:
        st.warning("Silakan unggah data Anda terlebih dahulu di halaman 'Upload Data'.")
        st.stop()
    else:
        df = st.session_state.get('df')

        # --- Filtering Options ---
        with st.expander("Filter Data"):
            df_filtered = df.copy()

            if 'Date' in df_filtered.columns:
                df_filtered['Date'] = pd.to_datetime(df_filtered['Date'], errors='coerce')
                df_filtered.dropna(subset=['Date'], inplace=True)

                if not df_filtered.empty:
                    min_date_available = df_filtered['Date'].min().date()
                    max_date_available = df_filtered['Date'].max().date()

                    date_range = st.date_input(
                        "Pilih Rentang Tanggal",
                        value=(min_date_available, max_date_available),
                        min_value=min_date_available,
                        max_value=max_date_available,
                        key="data_overview_date_filter"
                    )

                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        df_filtered = df_filtered[(df_filtered['Date'].dt.date >= start_date) & (df_filtered['Date'].dt.date <= end_date)]
                    else:
                        st.info("Pilih rentang tanggal yang valid.")
                else:
                    st.warning("Tidak ada data tanggal yang valid setelah pembersihan. Filter tanggal tidak tersedia.")
            else:
                st.warning("Kolom 'Date' tidak ditemukan dalam data Anda. Filter tanggal tidak tersedia.")

            if 'Category' in df_filtered.columns:
                categories = df_filtered['Category'].dropna().unique()
                if len(categories) > 0:
                    selected_categories = st.multiselect("Pilih Kategori", categories.tolist(), default=categories.tolist(), key="data_overview_category_filter")
                    df_filtered = df_filtered[df_filtered['Category'].isin(selected_categories)]
                else:
                    st.info("Tidak ada data kategori yang valid.")

            if 'Source' in df_filtered.columns:
                sources = df_filtered['Source'].dropna().unique()
                if len(sources) > 0:
                    selected_sources = st.multiselect("Pilih Sumber", sources.tolist(), default=sources.tolist(), key="data_overview_source_filter")
                    df_filtered = df_filtered[df_filtered['Source'].isin(selected_sources)]
                else:
                    st.info("Tidak ada data sumber yang valid.")

            st.write(f"Data yang difilter: {len(df_filtered)} baris")

        # --- Display Data Overview if filtered data is not empty ---
        if not df_filtered.empty:
            # Row 1: KPIs
            st.header("Ringkasan Metrik Utama")
            col1, col2, col3 = st.columns(3)
            with col1:
                total_articles = len(df_filtered)
                st.metric(label="Total Artikel", value=f"{total_articles:,}")
                st.caption(get_insights("Total Artikel"))
            with col2:
                avg_sentiment_score = df_filtered['Sentiment_Score'].mean() if 'Sentiment_Score' in df_filtered.columns else 0
                st.metric(label="Rata-rata Sentimen", value=f"{avg_sentiment_score:.2f}")
                st.caption(get_insights("Rata-rata Sentimen"))
            with col3:
                unique_sources = df_filtered['Source'].nunique() if 'Source' in df_filtered.columns else 0
                st.metric(label="Sumber Unik", value=f"{unique_sources:,}")
                st.caption(get_insights("Sumber Unik"))

            st.markdown("---")

            # Row 2: Sentiment Distribution & Top Keywords
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("Distribusi Sentimen")
                if 'Sentiment' in df_filtered.columns and not df_filtered['Sentiment'].isnull().all():
                    sentiment_counts = df_filtered['Sentiment'].value_counts().reset_index()
                    sentiment_counts.columns = ['Sentiment', 'Count']
                    fig_sentiment = px.pie(
                        sentiment_counts,
                        values='Count',
                        names='Sentiment',
                        title='Distribusi Sentimen Berdasarkan Artikel',
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        hole=0.3
                    )
                    fig_sentiment.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#E0E0E0",
                        legend_title_text='Sentimen', margin=dict(l=20, r=20, t=60, b=20), title_x=0.5
                    )
                    st.plotly_chart(fig_sentiment, use_container_width=True)
                    st.info(get_insights("Distribusi Sentimen"))
                else:
                    st.warning("Kolom 'Sentiment' tidak ditemukan atau kosong. Distribusi sentimen tidak dapat ditampilkan.")

            with col_chart2:
                st.subheader("Kata Kunci Teratas")
                if 'Keywords' in df_filtered.columns and not df_filtered['Keywords'].isnull().all():
                    all_keywords = df_filtered['Keywords'].dropna().astype(str).str.split(', ').explode()
                    keyword_counts = all_keywords.value_counts().head(10).reset_index()
                    keyword_counts.columns = ['Keyword', 'Count']
                    if not keyword_counts.empty:
                        fig_keywords = px.bar(
                            keyword_counts, x='Count', y='Keyword', orientation='h',
                            title='10 Kata Kunci Teratas', color_discrete_sequence=['#4A90E2']
                        )
                        fig_keywords.update_layout(
                            yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)', font_color="#E0E0E0",
                            margin=dict(l=20, r=20, t=60, b=20), title_x=0.5
                        )
                        st.plotly_chart(fig_keywords, use_container_width=True)
                        st.info(get_insights("Kata Kunci Teratas"))
                    else:
                        st.info("Tidak ada kata kunci yang valid untuk ditampilkan.")
                else:
                    st.warning("Kolom 'Keywords' tidak ditemukan atau kosong. Tren kata kunci tidak dapat ditampilkan.")

            st.markdown("---")

            # Row 3: Sentiment Over Time & Source Performance
            col_chart3, col_chart4 = st.columns(2)
            with col_chart3:
                st.subheader("Tren Sentimen Seiring Waktu")
                if 'Date' in df_filtered.columns and 'Sentiment' in df_filtered.columns and \
                   not df_filtered['Date'].isnull().all() and not df_filtered['Sentiment'].isnull().all():
                    df_filtered_sentiment = df_filtered.copy()
                    df_filtered_sentiment['Date'] = pd.to_datetime(df_filtered_sentiment['Date'])
                    df_filtered_sentiment.set_index('Date', inplace=True)
                    sentiment_daily = df_filtered_sentiment.groupby([pd.Grouper(freq='D'), 'Sentiment']).size().unstack(fill_value=0)
                    sentiment_daily = sentiment_daily.apply(lambda x: x / x.sum(), axis=1).fillna(0)
                    sentiment_order = ['Positive', 'Neutral', 'Negative']
                    sentiment_daily = sentiment_daily.reindex(columns=sentiment_order, fill_value=0)

                    fig_sentiment_time = px.area(
                        sentiment_daily, title='Distribusi Proporsi Sentimen Harian',
                        color_discrete_map={'Positive': '#4CAF50', 'Neutral': '#FFA000', 'Negative': '#D32F2F'}
                    )
                    fig_sentiment_time.update_layout(
                        xaxis_title="Tanggal", yaxis_title="Proporsi Sentimen", hovermode="x unified",
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#E0E0E0",
                        margin=dict(l=20, r=20, t=60, b=20), title_x=0.5
                    )
                    st.plotly_chart(fig_sentiment_time, use_container_width=True)
                    st.info(get_insights("Tren Sentimen Harian"))
                else:
                    st.warning("Kolom 'Date' atau 'Sentiment' tidak ditemukan atau kosong. Tren sentimen tidak dapat ditampilkan.")

            with col_chart4:
                st.subheader("Sentimen Berdasarkan Sumber Media")
                if 'Source' in df_filtered.columns and 'Sentiment' in df_filtered.columns and \
                   not df_filtered['Source'].isnull().all() and not df_filtered['Sentiment'].isnull().all():
                    source_sentiment = df_filtered.groupby(['Source', 'Sentiment']).size().unstack(fill_value=0)
                    source_sentiment['Total Articles'] = source_sentiment.sum(axis=1)
                    source_sentiment_sorted = source_sentiment.sort_values(by='Total Articles', ascending=False).head(10)

                    if not source_sentiment_sorted.empty:
                        source_sentiment_melted = source_sentiment_sorted.reset_index().melt(
                            id_vars=['Source', 'Total Articles'], var_name='Sentiment', value_name='Count'
                        )
                        source_sentiment_melted = source_sentiment_melted[source_sentiment_melted['Sentiment'].isin(['Positive', 'Negative', 'Neutral'])]
                        sentiment_order_for_plot = ['Positive', 'Neutral', 'Negative']
                        source_sentiment_melted['Sentiment'] = pd.Categorical(source_sentiment_melted['Sentiment'], categories=sentiment_order_for_plot, ordered=True)
                        source_sentiment_melted = source_sentiment_melted.sort_values('Sentiment')

                        fig_source = px.bar(
                            source_sentiment_melted, x='Count', y='Source', color='Sentiment',
                            title='Sentimen Berdasarkan Sumber Media (Top 10 Volume)', orientation='h',
                            color_discrete_map={'Positive': '#4CAF50', 'Neutral': '#FFA000', 'Negative': '#D32F2F'}
                        )
                        fig_source.update_layout(
                            yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)', font_color="#E0E0E0",
                            margin=dict(l=20, r=20, t=60, b=20), title_x=0.5
                        )
                        st.plotly_chart(fig_source, use_container_width=True)
                        st.info(get_insights("Sentimen Berdasarkan Sumber"))
                    else:
                        st.info("Tidak ada data sumber atau sentimen yang cukup untuk membuat visualisasi.")
                else:
                    st.warning("Kolom 'Source' atau 'Sentiment' tidak ditemukan atau kosong. Kinerja sumber tidak dapat ditampilkan.")

            st.markdown("---")

            # Row 4: Media Reach & (Optional: Headline or Keyword Trends over time)
            col_chart5, col_chart6 = st.columns(2)
            with col_chart5:
                st.subheader("Jangkauan Media")
                if 'Reach' in df_filtered.columns and not df_filtered['Reach'].isnull().all():
                    total_reach = df_filtered['Reach'].sum()
                    st.metric(label="Total Jangkauan Diperkirakan", value=f"{total_reach:,.0f}")

                    if 'Date' in df_filtered.columns and not df_filtered['Date'].isnull().all():
                        df_filtered_reach = df_filtered.copy()
                        df_filtered_reach['Date'] = pd.to_datetime(df_filtered_reach['Date'])
                        df_filtered_reach.set_index('Date', inplace=True)
                        daily_reach = df_filtered_reach.resample('D')['Reach'].sum().reset_index()

                        if not daily_reach.empty:
                            fig_reach_time = px.line(
                                daily_reach, x='Date', y='Reach', title='Total Jangkauan Harian',
                                line_shape="spline", color_discrete_sequence=['#4A90E2']
                            )
                            fig_reach_time.update_layout(
                                xaxis_title="Tanggal", yaxis_title="Jangkauan", hovermode="x unified",
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#E0E0E0",
                                margin=dict(l=20, r=20, t=60, b=20), title_x=0.5
                            )
                            st.plotly_chart(fig_reach_time, use_container_width=True)
                            st.info(get_insights("Total Jangkauan Harian"))
                        else:
                            st.info("Tidak ada data jangkauan yang cukup untuk membuat tren.")
                    else:
                        st.warning("Kolom 'Date' tidak ditemukan atau kosong. Tren jangkauan tidak dapat ditampilkan.")
                else:
                    st.warning("Kolom 'Reach' tidak ditemukan atau kosong. Tidak dapat menghitung jangkauan media.")
            with col_chart6:
                st.subheader("Tren Kata Kunci Populer")
                if 'Keywords' in df_filtered.columns and 'Date' in df_filtered.columns and \
                   not df_filtered['Keywords'].isnull().all() and not df_filtered['Date'].isnull().all():
                    all_keywords = df_filtered.assign(Keyword=df_filtered['Keywords'].astype(str).str.split(', ')).explode('Keyword')
                    all_keywords = all_keywords[all_keywords['Keyword'].str.strip() != '']
                    all_keywords['Date'] = pd.to_datetime(all_keywords['Date'])

                    if not all_keywords.empty and 'Date' in all_keywords.columns:
                        keyword_daily_counts = all_keywords.groupby([pd.Grouper(key='Date', freq='D'), 'Keyword']).size().reset_index(name='Count')
                        top_keywords_overall = keyword_daily_counts.groupby('Keyword')['Count'].sum().nlargest(5).index.tolist()

                        if top_keywords_overall:
                            df_trend = keyword_daily_counts[keyword_daily_counts['Keyword'].isin(top_keywords_overall)]
                            fig_keyword_trend = px.line(
                                df_trend, x='Date', y='Count', color='Keyword', title='Tren Harian 5 Kata Kunci Teratas',
                                line_shape="spline", color_discrete_sequence=px.colors.qualitative.Pastel
                            )
                            fig_keyword_trend.update_layout(
                                xaxis_title="Tanggal", yaxis_title="Jumlah Kemunculan", hovermode="x unified",
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#E0E0E0",
                                margin=dict(l=20, r=20, t=60, b=20), title_x=0.5
                            )
                            st.plotly_chart(fig_keyword_trend, use_container_width=True)
                            st.info(get_insights("Keyword Trends"))
                        else:
                            st.info("Tidak cukup data kata kunci untuk membuat tren.")
                    else:
                        st.info("Tidak ada data kata kunci yang valid.")
                else:
                    st.warning("Kolom 'Keywords' atau 'Date' tidak ditemukan atau kosong. Tren kata kunci tidak dapat ditampilkan.")

            st.markdown("---")

            # Row 5: Raw Data Preview (Moved from Headline Analysis)
            st.subheader("Pratinjau Data Terbaru")
            if 'Headline' in df_filtered.columns and not df_filtered['Headline'].isnull().all():
                st.dataframe(df_filtered[['Date', 'Source', 'Headline', 'Sentiment']].head(20)) # Display top 20 headlines
            else:
                st.info("Kolom 'Headline' tidak ditemukan atau kosong. Pratinjau data terbatas.")
                st.dataframe(df_filtered.head(20)) # Show generic head if no headline

        else:
            st.info("Tidak ada data yang tersedia untuk analisis setelah diterapkan filter. Sesuaikan filter Anda.")


# Page: Settings
elif st.session_state.page == 'Settings':
    st.title("Pengaturan")
    st.write("Di sini Anda dapat mengelola pengaturan aplikasi.")
    st.warning("Fitur pengaturan belum diimplementasikan sepenuhnya.")
    theme_option = st.radio("Pilih Tema", ["Dark", "Light"], index=0, key="theme_setting")
    if theme_option == "Light":
        st.info("Mode terang belum didukung sepenuhnya oleh CSS ini. Disarankan menggunakan mode gelap.")

# Page: Help
elif st.session_state.page == 'Help':
    st.title("Bantuan")
    st.write("Butuh bantuan? Silakan hubungi tim dukungan kami atau lihat dokumentasi.")
    st.markdown("""
        ### Pertanyaan Umum
        - **Bagaimana cara mengunggah data?**
          Pilih opsi "Upload Data" dari menu sidebar, lalu klik "Pilih file data" untuk memilih file Anda. Anda dapat mengunggah file Excel (.xlsx) atau CSV (.csv).
        - **Format data yang didukung?**
          Saat ini mendukung file Excel (.xlsx) dan CSV (.csv) dengan kolom yang relevan seperti **'Date'**, **'Headline'**, **'Sentiment'** (e.g., 'Positive', 'Negative', 'Neutral'), **'Keywords'** (comma-separated), **'Source'**, **'Sentiment_Score'** (numeric), dan **'Reach'** (numeric). Pastikan nama kolom Anda sesuai.
        - **Bagaimana cara mendapatkan wawasan dari dashboard?**
          Setiap visualisasi dilengkapi dengan penjelasan singkat (insights) di bawahnya. Anda juga dapat menggunakan filter di bagian atas halaman analisis untuk mengeksplorasi data lebih dalam.
        ---
        Kontak Dukungan: support@example.com
    """)
