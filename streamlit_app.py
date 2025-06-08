# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import datetime

# --- Helper Function to get Insights ---
# PERHATIAN: Isi logika fungsi ini sesuai dengan implementasi Anda.
# Saya berasumsi Anda sudah memiliki fungsi ini, jadi saya hanya menyertakan templatenya
# dengan contoh wawasan. Anda bisa menyesuaikannya atau membuatnya lebih dinamis.
def get_insights(chart_title, df_filtered=None):
    insights = {
        "Dashboard Overview": "Ringkasan metrik utama menunjukkan kinerja media yang stabil dengan jangkauan dan sentimen yang positif secara keseluruhan.",
        "Headline Analysis": "Analisis judul menunjukkan tren dominasi topik tertentu dan sentimen yang terkait dengan narasi tersebut.",
        "Keyword Trends": "Kata kunci yang sedang tren mengindikasikan area minat publik dan publikasi yang paling sering dibahas di media.",
        "Sentiment Over Time": "Sentimen dari waktu ke waktu menunjukkan fluktuasi yang perlu dipantau untuk memahami dampak peristiwa atau kampanye.",
        "Source Performance": "Beberapa sumber media memiliki dampak yang lebih besar pada sentimen atau jangkauan, mengindikasikan pentingnya kemitraan strategis.",
        "Media Reach": "Jangkauan media yang terus meningkat menunjukkan keberhasilan dalam menjangkau audiens yang lebih luas.",
        "Distribusi Sentimen": "Distribusi sentimen berdasarkan artikel memberikan gambaran cepat tentang proporsi pandangan positif, negatif, dan netral.",
        "Kata Kunci Teratas": "Visualisasi kata kunci teratas menyoroti fokus utama diskusi dan isu yang paling relevan.",
        "Total Artikel": "Angka total artikel menunjukkan volume liputan media yang diterima.",
        "Rata-rata Sentimen": "Rata-rata sentimen memberikan indikator numerik singkat tentang keseluruhan nada liputan."
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
# Pastikan file style.css ada di direktori yang sama
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    st.error("File 'style.css' tidak ditemukan. Pastikan file tersebut berada di direktori yang sama dengan 'streamlit_app.py'.")
    st.stop() # Hentikan eksekusi jika CSS tidak dapat dimuat

# --- Page State Management for Sidebar Navigation ---
# Define the list of page options.
page_options = [
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
]

# Ensure 'page' is initialized and valid.
if 'page' not in st.session_state or st.session_state.page not in page_options:
    st.session_state.page = 'Home' # Set a default page that is definitely in the list

# --- Sidebar Content ---
st.sidebar.title("MENU ANALISIS")

# Get the current index of the selected page
try:
    current_page_index = page_options.index(st.session_state.page)
except ValueError:
    # Fallback in case st.session_state.page somehow gets an invalid value (should be rare with above check)
    current_page_index = 0 # Default to 'Home'
    st.session_state.page = page_options[current_page_index] # Correct the session state

# Custom navigation using st.radio for "capsule" style
page_selection = st.sidebar.radio(
    "Navigasi",
    page_options,
    index=current_page_index, # Use the calculated index
    key="main_navigation"
)

# Update session state if the user selects a different page from the radio button
if page_selection:
    st.session_state.page = page_selection

# --- Main Content Area ---

# Page: Home
if st.session_state.page == 'Home':
    st.title("Selamat Datang di Media Intelligence Dashboard")
    st.write("Gunakan dashboard ini untuk menganalisis data media Anda.")

    # HTML for the hero section, incorporating the custom CSS classes
    st.markdown("""
        <div class="stContainer">
            <h3>Overview</h3>
            <p>Aplikasi ini dirancang untuk membantu Anda memahami lanskap media, melacak tren, dan mengidentifikasi wawasan utama dari data berita dan publikasi.</p>
            <p>Untuk memulai, unggah data Anda.</p>
            <br>
        </div>
    """, unsafe_allow_html=True)

    # Button to navigate to Upload Data page
    if st.button("Mulai Analisis", key="start_analysis_button"):
        st.session_state.page = 'Upload Data'
        st.experimental_rerun() # Rerun to navigate to the new page

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
            # Determine file type and read accordingly
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                st.error("Format file tidak didukung. Harap unggah file .xlsx atau .csv.")
                df = None # Set df to None if format is not supported

            if df is not None:
                st.session_state.df = df # Store DataFrame in session_state
                st.success("File berhasil diunggah!")
                st.write("Pratinjau Data:")
                st.dataframe(df.head())

                # Optionally, move to Dashboard Overview after upload
                if st.button("Lihat Dashboard", key="view_dashboard_button"):
                    st.session_state.page = 'Dashboard Overview'
                    st.experimental_rerun() # Rerun to navigate to the new page
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")
            st.info("Pastikan file Anda berformat benar dan tidak rusak, serta sesuai dengan ekspektasi kolom.")

# All subsequent pages require data
if 'df' not in st.session_state or st.session_state.df.empty: # Check if df exists AND is not empty
    if st.session_state.page not in ['Home', 'Upload Data', 'Settings', 'Help']:
        st.warning("Silakan unggah data Anda terlebih dahulu di halaman 'Upload Data'.")
        st.stop() # Stop execution if data is not available for analysis pages
    else:
        df = pd.DataFrame() # Ensure df is defined as empty for non-data pages if no data
else:
    df = st.session_state.get('df') # Get DataFrame from session state for analysis pages

    # --- Filtering Options (Common for Dashboard & Analysis Pages) ---
    if st.session_state.page in ['Dashboard Overview', 'Headline Analysis', 'Keyword Trends', 'Sentiment Over Time', 'Source Performance', 'Media Reach']:
        with st.expander("Filter Data"):
            if not df.empty:
                df_filtered = df.copy() # Start with a copy of the original df

                # Assuming 'Date' column exists and is in datetime format
                if 'Date' in df_filtered.columns:
                    # Convert to datetime, coercing errors to NaT (Not a Time)
                    df_filtered['Date'] = pd.to_datetime(df_filtered['Date'], errors='coerce')
                    # Drop rows where 'Date' conversion failed
                    df_filtered.dropna(subset=['Date'], inplace=True)

                    if not df_filtered.empty:
                        min_date_available = df_filtered['Date'].min().date()
                        max_date_available = df_filtered['Date'].max().date()

                        date_range = st.date_input(
                            "Pilih Rentang Tanggal",
                            value=(min_date_available, max_date_available),
                            min_value=min_date_available,
                            max_value=max_date_available,
                            key="date_filter"
                        )

                        if len(date_range) == 2:
                            start_date, end_date = date_range
                            df_filtered = df_filtered[(df_filtered['Date'].dt.date >= start_date) & (df_filtered['Date'].dt.date <= end_date)]
                        else:
                            st.info("Pilih rentang tanggal yang valid.") # User might select only one date
                    else:
                        st.warning("Tidak ada data tanggal yang valid setelah pembersihan. Filter tanggal tidak tersedia.")
                else:
                    st.warning("Kolom 'Date' tidak ditemukan dalam data Anda. Filter tanggal tidak tersedia.")

                # Example of other filters (adjust to your actual columns)
                if 'Category' in df_filtered.columns:
                    # Ensure unique values, drop NaNs before getting unique for selection
                    categories = df_filtered['Category'].dropna().unique()
                    if len(categories) > 0:
                        selected_categories = st.multiselect("Pilih Kategori", categories.tolist(), default=categories.tolist(), key="category_filter")
                        df_filtered = df_filtered[df_filtered['Category'].isin(selected_categories)]
                    else:
                        st.info("Tidak ada data kategori yang valid.")


                if 'Source' in df_filtered.columns:
                    # Ensure unique values, drop NaNs before getting unique for selection
                    sources = df_filtered['Source'].dropna().unique()
                    if len(sources) > 0:
                        selected_sources = st.multiselect("Pilih Sumber", sources.tolist(), default=sources.tolist(), key="source_filter")
                        df_filtered = df_filtered[df_filtered['Source'].isin(selected_sources)]
                    else:
                        st.info("Tidak ada data sumber yang valid.")

                st.write(f"Data yang difilter: {len(df_filtered)} baris")
            else:
                st.info("Tidak ada data untuk difilter setelah unggahan.")
                df_filtered = pd.DataFrame() # Ensure df_filtered is empty if original df is empty
    else:
        df_filtered = df.copy() # No filtering applied for Home, Upload, Settings, Help pages
        # If df was empty from the start, df_filtered will also be empty here.


    # --- Dashboard Overview Page ---
    if st.session_state.page == 'Dashboard Overview':
        st.title("Dashboard Overview")
        st.info(get_insights("Dashboard Overview")) # General insight for the page

        if not df_filtered.empty:
            # Example KPIs (ensure columns exist before trying to access them)
            total_articles = len(df_filtered)
            avg_sentiment_score = df_filtered['Sentiment_Score'].mean() if 'Sentiment_Score' in df_filtered.columns else 0 # Assuming 'Sentiment_Score'
            unique_sources = df_filtered['Source'].nunique() if 'Source' in df_filtered.columns else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Artikel", value=f"{total_articles:,}")
                st.caption(get_insights("Total Artikel"))
            with col2:
                st.metric(label="Rata-rata Sentimen", value=f"{avg_sentiment_score:.2f}")
                st.caption(get_insights("Rata-rata Sentimen"))
            with col3:
                st.metric(label="Sumber Unik", value=f"{unique_sources:,}")
                st.caption(get_insights("Source Performance"))

            st.markdown("---")

            st.header("Ringkasan Visual")

            # Example Chart 1: Sentiment Distribution (Assuming 'Sentiment' column: Positive, Negative, Neutral)
            if 'Sentiment' in df_filtered.columns and not df_filtered['Sentiment'].isnull().all():
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
                    margin=dict(l=20, r=20, t=60, b=20),
                    title_x=0.5 # Center title
                )
                st.plotly_chart(fig_sentiment, use_container_width=True)
                st.info(get_insights("Distribusi Sentimen"))
            else:
                st.warning("Kolom 'Sentiment' tidak ditemukan atau kosong. Distribusi sentimen tidak dapat ditampilkan.")


            # Example Chart 2: Top Keywords (Assuming 'Keywords' column, possibly comma-separated)
            if 'Keywords' in df_filtered.columns and not df_filtered['Keywords'].isnull().all():
                st.subheader("Kata Kunci Teratas")
                # Simple keyword extraction (adjust if your 'Keywords' column is different)
                # Ensure keywords are strings before splitting
                all_keywords = df_filtered['Keywords'].dropna().astype(str).str.split(', ').explode()
                keyword_counts = all_keywords.value_counts().head(10).reset_index()
                keyword_counts.columns = ['Keyword', 'Count']
                if not keyword_counts.empty:
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
                        margin=dict(l=20, r=20, t=60, b=20),
                        title_x=0.5 # Center title
                    )
                    st.plotly_chart(fig_keywords, use_container_width=True)
                    st.info(get_insights("Kata Kunci Teratas"))
                else:
                    st.info("Tidak ada kata kunci yang valid untuk ditampilkan.")
            else:
                st.warning("Kolom 'Keywords' tidak ditemukan atau kosong. Tren kata kunci tidak dapat ditampilkan.")

        else:
            st.info("Tidak ada data yang tersedia untuk ditampilkan di dashboard. Silakan unggah data terlebih dahulu.")

    # Page: Headline Analysis
    elif st.session_state.page == 'Headline Analysis':
        st.title("Analisis Headline")
        st.info(get_insights("Headline Analysis"))

        if not df_filtered.empty:
            # Assuming 'Headline' column exists
            if 'Headline' in df_filtered.columns and not df_filtered['Headline'].isnull().all():
                st.subheader("Headline Terbaru")
                st.dataframe(df_filtered[['Date', 'Source', 'Headline', 'Sentiment']].head(20)) # Display top 20 headlines

                st.subheader("Analisis Frekuensi Kata dalam Headline")
                st.write("*(Area ini dapat diperluas untuk analisis lebih mendalam seperti Word Cloud atau N-gram analysis)*")
            else:
                st.warning("Kolom 'Headline' tidak ditemukan atau kosong dalam data Anda.")
        else:
            st.info("Tidak ada data yang tersedia untuk analisis headline.")

    # Page: Keyword Trends
    elif st.session_state.page == 'Keyword Trends':
        st.title("Tren Kata Kunci")
        st.info(get_insights("Keyword Trends"))

        if not df_filtered.empty:
            if 'Keywords' in df_filtered.columns and 'Date' in df_filtered.columns and \
               not df_filtered['Keywords'].isnull().all() and not df_filtered['Date'].isnull().all():
                st.subheader("Tren Kata Kunci Populer Seiring Waktu")
                # This requires more complex logic to aggregate keywords by date.
                # For simplicity, let's just show top keywords again, or mention where a more complex chart would go.
                st.write("*(Untuk visualisasi tren kata kunci seiring waktu, Anda dapat membuat area chart atau line chart yang menampilkan frekuensi kata kunci teratas per periode waktu.)*")

                # Example of a simple keyword count trend (might need refinement based on your data)
                # Ensure 'Keywords' column is string and then split
                all_keywords = df_filtered.assign(Keyword=df_filtered['Keywords'].astype(str).str.split(', ')).explode('Keyword')
                if not all_keywords.empty and 'Date' in all_keywords.columns:
                    # Drop any rows where Keyword is empty string from splitting
                    all_keywords = all_keywords[all_keywords['Keyword'].str.strip() != '']
                    all_keywords['Date'] = pd.to_datetime(all_keywords['Date']) # Ensure Date is datetime

                    keyword_daily_counts = all_keywords.groupby([pd.Grouper(key='Date', freq='D'), 'Keyword']).size().reset_index(name='Count')
                    top_keywords_overall = keyword_daily_counts.groupby('Keyword')['Count'].sum().nlargest(5).index.tolist()

                    if top_keywords_overall:
                        df_trend = keyword_daily_counts[keyword_daily_counts['Keyword'].isin(top_keywords_overall)]
                        fig_keyword_trend = px.line(
                            df_trend,
                            x='Date',
                            y='Count',
                            color='Keyword',
                            title='Tren Harian 5 Kata Kunci Teratas',
                            line_shape="spline",
                            color_discrete_sequence=px.colors.qualitative.Pastel # Use a nice color palette
                        )
                        fig_keyword_trend.update_layout(
                            xaxis_title="Tanggal",
                            yaxis_title="Jumlah Kemunculan",
                            hovermode="x unified",
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color="#E0E0E0",
                            margin=dict(l=20, r=20, t=60, b=20),
                            title_x=0.5
                        )
                        st.plotly_chart(fig_keyword_trend, use_container_width=True)
                    else:
                        st.info("Tidak cukup data kata kunci untuk membuat tren.")
                else:
                    st.info("Tidak ada data kata kunci yang valid.")
            else:
                st.warning("Kolom 'Keywords' atau 'Date' tidak ditemukan atau kosong dalam data Anda.")
        else:
            st.info("Tidak ada data yang tersedia untuk analisis tren kata kunci.")

    # Page: Sentiment Over Time
    elif st.session_state.page == 'Sentiment Over Time':
        st.title("Sentimen Seiring Waktu")
        st.info(get_insights("Sentiment Over Time"))

        if not df_filtered.empty:
            if 'Date' in df_filtered.columns and 'Sentiment' in df_filtered.columns and \
               not df_filtered['Date'].isnull().all() and not df_filtered['Sentiment'].isnull().all():
                st.subheader("Tren Sentimen Harian/Mingguan")
                # Ensure 'Date' is datetime and set as index for resampling
                df_filtered_sentiment = df_filtered.copy()
                df_filtered_sentiment['Date'] = pd.to_datetime(df_filtered_sentiment['Date'])
                df_filtered_sentiment.set_index('Date', inplace=True)

                # Example: Calculate daily sentiment distribution
                sentiment_daily = df_filtered_sentiment.groupby([pd.Grouper(freq='D'), 'Sentiment']).size().unstack(fill_value=0)
                # Convert to percentages per day
                sentiment_daily = sentiment_daily.apply(lambda x: x / x.sum(), axis=1).fillna(0)

                # Define consistent order for sentiment columns and colors
                sentiment_order = ['Positive', 'Neutral', 'Negative']
                # Reindex to ensure all sentiment types are present, filling missing with 0
                sentiment_daily = sentiment_daily.reindex(columns=sentiment_order, fill_value=0)

                fig_sentiment_time = px.area(
                    sentiment_daily,
                    title='Distribusi Proporsi Sentimen Harian',
                    color_discrete_map={
                        'Positive': '#4CAF50',  # Green
                        'Neutral': '#FFA000',   # Orange
                        'Negative': '#D32F2F'   # Red
                    }
                )
                fig_sentiment_time.update_layout(
                    xaxis_title="Tanggal",
                    yaxis_title="Proporsi Sentimen",
                    hovermode="x unified",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="#E0E0E0",
                    margin=dict(l=20, r=20, t=60, b=20),
                    title_x=0.5
                )
                st.plotly_chart(fig_sentiment_time, use_container_width=True)
            else:
                st.warning("Kolom 'Date' atau 'Sentiment' tidak ditemukan atau kosong dalam data Anda.")
        else:
            st.info("Tidak ada data yang tersedia untuk analisis sentimen seiring waktu.")

    # Page: Source Performance
    elif st.session_state.page == 'Source Performance':
        st.title("Kinerja Sumber Media")
        st.info(get_insights("Source Performance"))

        if not df_filtered.empty:
            if 'Source' in df_filtered.columns and 'Sentiment' in df_filtered.columns and \
               not df_filtered['Source'].isnull().all() and not df_filtered['Sentiment'].isnull().all():
                st.subheader("Sentimen Berdasarkan Sumber")
                # Group by source and sentiment, then unstack to get counts for each sentiment type
                source_sentiment = df_filtered.groupby(['Source', 'Sentiment']).size().unstack(fill_value=0)
                source_sentiment['Total Articles'] = source_sentiment.sum(axis=1) # Calculate total articles per source
                source_sentiment_sorted = source_sentiment.sort_values(by='Total Articles', ascending=False).head(10) # Top 10 sources by volume

                if not source_sentiment_sorted.empty:
                    # Melt the DataFrame for Plotly to easily plot stacked bars by sentiment
                    source_sentiment_melted = source_sentiment_sorted.reset_index().melt(
                        id_vars=['Source', 'Total Articles'],
                        var_name='Sentiment',
                        value_name='Count'
                    )
                    # Filter out the 'Total Articles' row from sentiment for plotting
                    source_sentiment_melted = source_sentiment_melted[source_sentiment_melted['Sentiment'].isin(['Positive', 'Negative', 'Neutral'])]

                    # Ensure consistent order for sentiment legend
                    sentiment_order_for_plot = ['Positive', 'Neutral', 'Negative'] # Order in legend
                    source_sentiment_melted['Sentiment'] = pd.Categorical(source_sentiment_melted['Sentiment'], categories=sentiment_order_for_plot, ordered=True)
                    source_sentiment_melted = source_sentiment_melted.sort_values('Sentiment')


                    fig_source = px.bar(
                        source_sentiment_melted,
                        x='Count',
                        y='Source',
                        color='Sentiment',
                        title='Sentimen Berdasarkan Sumber Media (Top 10 Volume)',
                        orientation='h',
                        color_discrete_map={
                            'Positive': '#4CAF50',
                            'Neutral': '#FFA000',
                            'Negative': '#D32F2F'
                        }
                    )
                    fig_source.update_layout(
                        yaxis={'categoryorder':'total ascending'}, # Sort sources by total count
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color="#E0E0E0",
                        margin=dict(l=20, r=20, t=60, b=20),
                        title_x=0.5
                    )
                    st.plotly_chart(fig_source, use_container_width=True)
                else:
                    st.info("Tidak ada data sumber atau sentimen yang cukup untuk membuat visualisasi.")
            else:
                st.warning("Kolom 'Source' atau 'Sentiment' tidak ditemukan atau kosong dalam data Anda.")
        else:
            st.info("Tidak ada data yang tersedia untuk analisis kinerja sumber.")

    # Page: Media Reach
    elif st.session_state.page == 'Media Reach':
        st.title("Jangkauan Media")
        st.info(get_insights("Media Reach"))

        if not df_filtered.empty:
            # Assuming 'Reach' or 'Impressions' column
            if 'Reach' in df_filtered.columns and not df_filtered['Reach'].isnull().all(): # Or calculate based on unique sources/articles
                st.subheader("Jangkauan Media Keseluruhan")
                total_reach = df_filtered['Reach'].sum()
                st.metric(label="Total Jangkauan Diperkirakan", value=f"{total_reach:,.0f}")

                if 'Date' in df_filtered.columns and not df_filtered['Date'].isnull().all():
                    st.subheader("Jangkauan Berdasarkan Waktu")
                    # Example: Time series of total reach
                    df_filtered_reach = df_filtered.copy()
                    df_filtered_reach['Date'] = pd.to_datetime(df_filtered_reach['Date'])
                    df_filtered_reach.set_index('Date', inplace=True)
                    daily_reach = df_filtered_reach.resample('D')['Reach'].sum().reset_index()

                    if not daily_reach.empty:
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
                            margin=dict(l=20, r=20, t=60, b=20),
                            title_x=0.5
                        )
                        st.plotly_chart(fig_reach_time, use_container_width=True)
                    else:
                        st.info("Tidak ada data jangkauan yang cukup untuk membuat tren.")
                else:
                    st.warning("Kolom 'Date' tidak ditemukan atau kosong. Tren jangkauan tidak dapat ditampilkan.")
            else:
                st.warning("Kolom 'Reach' tidak ditemukan atau kosong dalam data Anda. Tidak dapat menghitung jangkauan media.")
        else:
            st.info("Tidak ada data yang tersedia untuk analisis jangkauan media.")

    # Page: Settings
    elif st.session_state.page == 'Settings':
        st.title("Pengaturan")
        st.write("Di sini Anda dapat mengelola pengaturan aplikasi.")
        st.warning("Fitur pengaturan belum diimplementasikan sepenuhnya.")
        # Example settings (dummy)
        theme_option = st.radio("Pilih Tema", ["Dark", "Light"], index=0, key="theme_setting")
        if theme_option == "Light":
            st.info("Mode terang belum didukung sepenuhnya oleh CSS ini. Disarankan menggunakan mode gelap.")
        # You could add more settings like:
        # data_refresh_interval = st.slider("Interval Refresh Data (menit)", 5, 60, 30)

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
            Kontak Dukungan: shannonsifra@gmail.com
        """)
