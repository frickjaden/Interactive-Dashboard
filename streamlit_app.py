# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import datetime

# --- Helper Function to get Insights ---
# REVISI BESAR DI FUNGSI INI UNTUK INSIGHTS DINAMIS
def get_insights(chart_title, df_filtered):
    insights = [] # List untuk menyimpan insight

    if df_filtered.empty:
        return ["Tidak ada data yang tersedia untuk menghasilkan wawasan."]

    if chart_title == "Total Artikel":
        total_articles = len(df_filtered)
        insights.append(f"Total liputan media dalam periode ini adalah **{total_articles:,} artikel**.")
        if total_articles == 0:
            insights.append("Tidak ada artikel yang cocok dengan filter yang diterapkan.")
        elif total_articles < 100:
            insights.append("Volume liputan tergolong rendah, mungkin menandakan cakupan terbatas atau periode tenang.")
        else:
            insights.append("Volume liputan signifikan, menunjukkan aktivitas media yang tinggi.")

    elif chart_title == "Rata-rata Sentimen":
        if 'Sentiment_Score' in df_filtered.columns and not df_filtered['Sentiment_Score'].isnull().all():
            avg_sentiment_score = df_filtered['Sentiment_Score'].mean()
            insights.append(f"Rata-rata skor sentimen keseluruhan adalah **{avg_sentiment_score:.2f}**.")
            if avg_sentiment_score > 0.5:
                insights.append("Sentimen cenderung sangat positif.")
            elif avg_sentiment_score > 0.1:
                insights.append("Sentimen keseluruhan cenderung positif.")
            elif avg_sentiment_score < -0.1:
                insights.append("Sentimen keseluruhan cenderung negatif.")
            else:
                insights.append("Sentimen cenderung netral atau seimbang.")
        else:
            insights.append("Kolom 'Sentiment_Score' tidak ditemukan atau kosong untuk analisis sentimen.")

    elif chart_title == "Sumber Unik":
        if 'Source' in df_filtered.columns and not df_filtered['Source'].isnull().all():
            unique_sources = df_filtered['Source'].nunique()
            insights.append(f"Ada **{unique_sources:,} sumber media unik** yang berkontribusi pada liputan ini.")
            if unique_sources < 10:
                insights.append("Liputan terkonsentrasi pada beberapa sumber utama.")
            else:
                insights.append("Liputan berasal dari beragam sumber media.")
        else:
            insights.append("Kolom 'Source' tidak ditemukan atau kosong untuk analisis sumber.")

    elif chart_title == "Distribusi Sentimen":
        if 'Sentiment' in df_filtered.columns and not df_filtered['Sentiment'].isnull().all():
            sentiment_counts = df_filtered['Sentiment'].value_counts(normalize=True) * 100
            positive_pct = sentiment_counts.get('Positive', 0)
            negative_pct = sentiment_counts.get('Negative', 0)
            neutral_pct = sentiment_counts.get('Neutral', 0)

            insights.append(f"Distribusi sentimen: Positif **{positive_pct:.1f}%**, Negatif **{negative_pct:.1f}%**, Netral **{neutral_pct:.1f}%**.")

            if positive_pct > negative_pct and positive_pct > neutral_pct:
                insights.append("Mayoritas liputan memiliki sentimen positif, menunjukkan persepsi yang baik.")
            elif negative_pct > positive_pct and negative_pct > neutral_pct:
                insights.append("Sentimen negatif mendominasi, menunjukkan potensi krisis atau isu yang perlu ditangani.")
            elif neutral_pct > positive_pct and neutral_pct > negative_pct:
                insights.append("Sentimen netral adalah yang paling dominan, mungkin berarti liputan informatif tanpa bias kuat.")
            else:
                insights.append("Distribusi sentimen cukup seimbang antara kategori.")
        else:
            insights.append("Kolom 'Sentiment' tidak ditemukan atau kosong untuk distribusi sentimen.")

    elif chart_title == "Kata Kunci Teratas":
        if 'Keywords' in df_filtered.columns and not df_filtered['Keywords'].isnull().all():
            all_keywords = df_filtered['Keywords'].dropna().astype(str).str.split(', ').explode()
            all_keywords = all_keywords[all_keywords.str.strip() != '']
            if not all_keywords.empty:
                keyword_counts = all_keywords.value_counts().head(3)
                if not keyword_counts.empty:
                    top_keywords_str = ", ".join([f"'{k}' ({v} kali)" for k, v in keyword_counts.items()])
                    insights.append(f"Tiga kata kunci teratas adalah: **{top_keywords_str}**.")
                    insights.append("Ini menunjukkan topik-topik paling relevan yang dibahas dalam periode ini.")
                else:
                    insights.append("Tidak ada kata kunci yang cukup untuk diidentifikasi.")
            else:
                insights.append("Data kata kunci kosong setelah pembersihan.")
        else:
            insights.append("Kolom 'Keywords' tidak ditemukan atau kosong untuk analisis kata kunci.")

    elif chart_title == "Tren Sentimen Harian":
        if 'Date' in df_filtered.columns and 'Sentiment' in df_filtered.columns and \
           not df_filtered['Date'].isnull().all() and not df_filtered['Sentiment'].isnull().all():
            df_sentiment_time = df_filtered.copy()
            df_sentiment_time['Date'] = pd.to_datetime(df_sentiment_time['Date'])
            df_sentiment_time.set_index('Date', inplace=True)
            daily_sentiment_summary = df_sentiment_time.groupby(pd.Grouper(freq='D'))['Sentiment_Score'].mean() # Assuming 'Sentiment_Score' exists
            
            if not daily_sentiment_summary.empty:
                max_sentiment_date = daily_sentiment_summary.idxmax()
                min_sentiment_date = daily_sentiment_summary.idxmin()
                
                insights.append(f"Sentimen tertinggi tercatat pada **{max_sentiment_date.strftime('%d %b %Y')}**.")
                insights.append(f"Sentimen terendah tercatat pada **{min_sentiment_date.strftime('%d %b %Y')}**.")
                
                # Simple trend analysis
                if len(daily_sentiment_summary) > 1:
                    last_day_sentiment = daily_sentiment_summary.iloc[-1]
                    prev_day_sentiment = daily_sentiment_summary.iloc[-2] if len(daily_sentiment_summary) > 1 else None
                    if prev_day_sentiment is not None:
                        if last_day_sentiment > prev_day_sentiment:
                            insights.append("Sentimen menunjukkan tren kenaikan dalam beberapa hari terakhir.")
                        elif last_day_sentiment < prev_day_sentiment:
                            insights.append("Sentimen menunjukkan tren penurunan dalam beberapa hari terakhir.")
                        else:
                            insights.append("Sentimen cenderung stabil dalam beberapa hari terakhir.")
            else:
                insights.append("Tidak ada data sentimen yang cukup untuk menganalisis tren harian.")
        else:
            insights.append("Kolom 'Date' atau 'Sentiment' tidak ditemukan atau kosong untuk tren sentimen.")

    elif chart_title == "Sentimen Berdasarkan Sumber":
        if 'Source' in df_filtered.columns and 'Sentiment' in df_filtered.columns and not df_filtered['Source'].isnull().all():
            source_sentiment_summary = df_filtered.groupby('Source')['Sentiment_Score'].mean().nlargest(3) # Top 3 by avg sentiment
            source_volume = df_filtered['Source'].value_counts().nlargest(3) # Top 3 by volume

            if not source_sentiment_summary.empty:
                insights.append("Sumber dengan rata-rata sentimen tertinggi:")
                for source, score in source_sentiment_summary.items():
                    insights.append(f"- **{source}** (Sentimen: {score:.2f})")
            
            if not source_volume.empty:
                insights.append("Sumber dengan volume artikel terbanyak:")
                for source, count in source_volume.items():
                    insights.append(f"- **{source}** ({count} artikel)")

            if source_sentiment_summary.empty and source_volume.empty:
                insights.append("Tidak ada data sumber atau sentimen yang cukup untuk analisis.")
        else:
            insights.append("Kolom 'Source' atau 'Sentiment' tidak ditemukan atau kosong untuk sentimen berdasarkan sumber.")

    elif chart_title == "Total Jangkauan Harian":
        if 'Date' in df_filtered.columns and 'Reach' in df_filtered.columns and \
           not df_filtered['Date'].isnull().all() and not df_filtered['Reach'].isnull().all():
            df_reach_time = df_filtered.copy()
            df_reach_time['Date'] = pd.to_datetime(df_reach_time['Date'])
            df_reach_time.set_index('Date', inplace=True)
            daily_reach_summary = df_reach_time.resample('D')['Reach'].sum()

            if not daily_reach_summary.empty:
                max_reach_date = daily_reach_summary.idxmax()
                insights.append(f"Jangkauan tertinggi tercatat pada **{max_reach_date.strftime('%d %b %Y')}** dengan total **{daily_reach_summary.max():,.0f}**.")
                
                # Simple trend analysis for reach
                if len(daily_reach_summary) > 1:
                    last_day_reach = daily_reach_summary.iloc[-1]
                    prev_day_reach = daily_reach_summary.iloc[-2] if len(daily_reach_summary) > 1 else None
                    if prev_day_reach is not None:
                        if last_day_reach > prev_day_reach:
                            insights.append("Jangkauan menunjukkan tren kenaikan dalam beberapa hari terakhir.")
                        elif last_day_reach < prev_day_reach:
                            insights.append("Jangkauan menunjukkan tren penurunan dalam beberapa hari terakhir.")
                        else:
                            insights.append("Jangkauan cenderung stabil dalam beberapa hari terakhir.")
            else:
                insights.append("Tidak ada data jangkauan yang cukup untuk menganalisis tren harian.")
        else:
            insights.append("Kolom 'Date' atau 'Reach' tidak ditemukan atau kosong untuk jangkauan harian.")

    # Jika tidak ada insight spesifik, berikan insight umum
    if not insights:
        insights.append(f"Tidak ada wawasan spesifik yang tersedia untuk '{chart_title}'.")

    return insights

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
    st.info("Berikut adalah ringkasan dan wawasan utama dari data media Anda.") # Insight umum untuk halaman

    # Ensure data is available before proceeding
    if 'df' not in st.session_state or st.session_state.df.empty:
        st.warning("Silakan unggah data Anda terlebih dahulu di halaman 'Upload Data'.")
        st.stop()
    else:
        df = st.session_state.get('df')

        # --- Filtering Options ---
        with st.expander("Filter Data"):
            df_filtered = df.copy()

            # Ensure 'Date' column is present and valid for filtering
            if 'Date' in df_filtered.columns:
                df_filtered['Date'] = pd.to_datetime(df_filtered['Date'], errors='coerce')
                df_filtered.dropna(subset=['Date'], inplace=True) # Remove rows with invalid dates

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
                        st.info("Pilih rentang tanggal yang valid untuk memfilter data.")
                else:
                    st.warning("Tidak ada data tanggal yang valid setelah pembersihan. Filter tanggal tidak tersedia.")
            else:
                st.warning("Kolom 'Date' tidak ditemukan dalam data Anda. Filter tanggal tidak tersedia.")

            # Filter for Category
            if 'Category' in df_filtered.columns:
                categories = df_filtered['Category'].dropna().unique()
                if len(categories) > 0:
                    selected_categories = st.multiselect("Pilih Kategori", categories.tolist(), default=categories.tolist(), key="data_overview_category_filter")
                    df_filtered = df_filtered[df_filtered['Category'].isin(selected_categories)]
                else:
                    st.info("Tidak ada data kategori yang valid.")

            # Filter for Source
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
                # Print insights
                for insight in get_insights("Total Artikel", df_filtered):
                    st.caption(insight)
            with col2:
                # Check for 'Sentiment_Score' column before calculating mean
                if 'Sentiment_Score' in df_filtered.columns and not df_filtered['Sentiment_Score'].isnull().all():
                    avg_sentiment_score = df_filtered['Sentiment_Score'].mean()
                    st.metric(label="Rata-rata Sentimen", value=f"{avg_sentiment_score:.2f}")
                else:
                    st.metric(label="Rata-rata Sentimen", value="N/A")
                    st.caption("Kolom 'Sentiment_Score' tidak tersedia.")
                for insight in get_insights("Rata-rata Sentimen", df_filtered):
                    st.caption(insight)
            with col3:
                # Check for 'Source' column before counting unique
                if 'Source' in df_filtered.columns and not df_filtered['Source'].isnull().all():
                    unique_sources = df_filtered['Source'].nunique()
                    st.metric(label="Sumber Unik", value=f"{unique_sources:,}")
                else:
                    st.metric(label="Sumber Unik", value="N/A")
                    st.caption("Kolom 'Source' tidak tersedia.")
                for insight in get_insights("Sumber Unik", df_filtered):
                    st.caption(insight)

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
                    for insight in get_insights("Distribusi Sentimen", df_filtered):
                        st.info(insight)
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
                        for insight in get_insights("Kata Kunci Teratas", df_filtered):
                            st.info(insight)
                    else:
                        st.info("Tidak ada kata kunci yang valid untuk ditampilkan.")
                else:
                    st.warning("Kolom 'Keywords' tidak ditemukan atau kosong. Tren kata kunci tidak dapat ditampilkan.")

            st.markdown("---")

            # Row 3: Sentiment Over Time & Source Performance
            col_chart3, col_chart4 = st.columns(2)
            with col_chart3:
                st.subheader("Tren Sentimen Seiring Waktu")
                # Need both 'Date' and 'Sentiment'/'Sentiment_Score' for this chart and its insights
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
                    for insight in get_insights("Tren Sentimen Harian", df_filtered):
                        st.info(insight)
                else:
                    st.warning("Kolom 'Date' atau 'Sentiment' tidak ditemukan atau kosong. Tren sentimen tidak dapat ditampilkan.")

            with col_chart4:
                st.subheader("Sentimen Berdasarkan Sumber Media")
                if 'Source' in df_filtered.columns and 'Sentiment' in df_filtered.columns and not df_filtered['Source'].isnull().all():
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
                        for insight in get_insights("Sentimen Berdasarkan Sumber", df_filtered):
                            st.info(insight)
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
                            for insight in get_insights("Total Jangkauan Harian", df_filtered):
                                st.info(insight)
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
                            for insight in get_insights("Keyword Trends", df_filtered):
                                st.info(insight)
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
          Saat ini mendukung file Excel (.xlsx) dan CSV (.csv) dengan kolom yang relevan seperti **'Date'** (format tanggal), **'Headline'** (teks), **'Sentiment'** (teks: 'Positive', 'Negative', 'Neutral'), **'Keywords'** (teks, dipisahkan koma seperti "kata1, kata2"), **'Source'** (teks), **'Sentiment_Score'** (numerik, e.g., -1.0 hingga 1.0), dan **'Reach'** (numerik). Pastikan nama kolom Anda sesuai.
        - **Bagaimana cara mendapatkan wawasan dari dashboard?**
          Setiap visualisasi dilengkapi dengan penjelasan singkat (insights) di bawahnya yang dihasilkan secara dinamis berdasarkan data yang difilter. Anda juga dapat menggunakan filter di bagian atas halaman analisis untuk mengeksplorasi data lebih dalam.
        ---
        Kontak Dukungan: support@example.com
    """)
