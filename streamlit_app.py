import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import datetime # Import the datetime module

# --- Helper Function to get Insights ---
def get_insights(chart_title, df_filtered=None):
    insights = []
    if df_filtered is None or df_filtered.empty:
        return ["Tidak ada data yang tersedia untuk menghasilkan insight."]

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
            insights.append(f"Proporsi sentimen netral sebesar {neutral_pct:.1%} dapat mengindikasikan peluang untuk lebih mengarahkan audiens ke sentimen positif melalui call-to-action yang lebih jelas atau konten yang lebih memprovokasi emosi.")
        else:
            insights.append("Data sentimen tidak cukup untuk analisis.")

    elif chart_title == "Engagement Trend over Time":
        df_filtered_weekly = df_filtered.groupby(df_filtered['date'].dt.to_period('W'))['engagements'].sum().reset_index()
        df_filtered_weekly['date'] = df_filtered_weekly['date'].dt.start_time
        if not df_filtered_weekly.empty:
            max_engagement_date = df_filtered_weekly.loc[df_filtered_weekly['engagements'].idxmax(), 'date']
            min_engagement_date = df_filtered_weekly.loc[df_filtered_weekly['engagements'].idxmin(), 'date']
            total_engagements = df_filtered_weekly['engagements'].sum()

            insights.append(f"Tren engagement menunjukkan puncaknya pada minggu yang dimulai **{max_engagement_date.strftime('%d %b %Y')}**, menunjukkan waktu yang efektif untuk aktivitas kampanye tertentu.")
            insights.append(f"Terjadi penurunan engagement pada minggu yang dimulai **{min_engagement_date.strftime('%d %b %Y')}**, perlu diinvestigasi faktor penyebab seperti perubahan strategi, konten, atau kejadian eksternal.")
            insights.append(f"Total engagement dalam periode ini adalah **{total_engagements:,.0f}**. Fluktuasi engagement menunjukkan pentingnya konsistensi dalam produksi konten dan strategi interaksi.")
        else:
            insights.append("Data tren engagement tidak cukup untuk analisis.")

    elif chart_title == "Platform Engagements":
        platform_engagements = df_filtered.groupby('platform')['engagements'].sum().sort_values(ascending=False).reset_index()
        if not platform_engagements.empty:
            top_platform = platform_engagements.iloc[0]
            insights.append(f"**{top_platform['platform']}** adalah platform dengan engagement tertinggi ({top_platform['engagements']:,.0f}), menjadikannya saluran paling efektif untuk kampanye ini.")
            if len(platform_engagements) > 1:
                second_platform = platform_engagements.iloc[1]
                insights.append(f"**{second_platform['platform']}** berada di posisi kedua ({second_platform['engagements']:,.0f}), menunjukkan potensi yang baik namun mungkin masih bisa dioptimalkan.")
            if len(platform_engagements) > 2:
                 least_platform = platform_engagements.iloc[-1]
                 insights.append(f"**{least_platform['platform']}** memiliki engagement terendah ({least_platform['engagements']:,.0f}), pertimbangkan untuk mengevaluasi kembali strategi atau alokasi sumber daya di platform ini.")
            else:
                insights.append("Diversifikasi platform penting untuk menjangkau audiens yang berbeda, namun alokasi sumber daya harus proporsional dengan performa engagement.")
        else:
            insights.append("Data engagement per platform tidak cukup untuk analisis.")

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
                insights.append(f"Tipe media **{least_popular['media_type'].capitalize()}** memiliki proporsi terendah (**{least_popular['percentage']:.1%}**), mungkin memerlukan eksperimen lebih lanjut atau peninjauan ulang daya tariknya.")
            else:
                 insights.append("Kombinasi berbagai tipe media dapat meningkatkan jangkauan dan daya tarik kampanye, namun fokus harus pada format yang paling efektif.")
        else:
            insights.append("Data tipe media tidak cukup untuk analisis.")

    elif chart_title == "Top 5 Locations":
        top_locations = df_filtered.groupby('location')['engagements'].sum().nlargest(5).reset_index()
        if not top_locations.empty:
            top1_loc = top_locations.iloc[0]
            insights.append(f"**{top1_loc['location']}** adalah lokasi dengan engagement tertinggi ({top1_loc['engagements']:,.0f}), ini adalah pasar utama yang harus terus ditargetkan dengan kuat.")
            if len(top_locations) > 1:
                top2_loc = top_locations.iloc[1]
                insights.append(f"**{top2_loc['location']}** juga menunjukkan engagement yang sangat tinggi ({top2_loc['engagements']:,.0f}), menjadikannya lokasi kunci kedua untuk strategi pemasaran.")
            if len(top_locations) > 2:
                remaining_eng = top_locations.iloc[2:]['engagements'].sum()
                insights.append(f"Terdapat **{len(top_locations) - 2}** lokasi lain dalam top 5 yang menyumbang total {remaining_eng:,.0f} engagement, menunjukkan distribusi minat geografis yang beragam.")
            else:
                insights.append("Data lokasi membantu dalam lokalisasi konten dan strategi pemasaran, mengidentifikasi pasar utama dan potensi ekspansi.")
        else:
            insights.append("Data lokasi tidak cukup untuk analisis.")

    return insights

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="Interactive Media Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a cleaner look ---
st.markdown("""
<style>
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .css-1d391kg { /* sidebar */
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #262730;
    }
    .stAlert {
        border-radius: 0.5rem;
    }
    .stMarkdown h4 {
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        color: #333;
    }
    .stMarkdown ul {
        list-style-type: disc;
        margin-left: 20px;
    }
    .stMarkdown li {
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Main Title ---
st.title("📊 Interactive Media Intelligence Dashboard")
st.markdown("""
Selamat datang di Dashboard Analisis Kampanye!
Unggah file CSV Anda untuk mendapatkan insight mendalam tentang performa media.
""")
st.markdown("---")

# --- Sidebar: Upload File ---
st.sidebar.header("1. Unggah File CSV Anda")
uploaded_file = st.sidebar.file_uploader(
    "Seret & Lepas atau Klik untuk Unggah file CSV Anda",
    type=["csv"],
    help="Pastikan file CSV memiliki kolom: Date, Platform, Sentiment, Location, Engagements, Media Type."
)

df = None # Initialize df to None

if uploaded_file is not None:
    with st.spinner('Memproses file...'):
        try:
            df = pd.read_csv(uploaded_file)
            st.sidebar.success("File berhasil diunggah!")

            st.header("2. Pembersihan Data")
            st.markdown(
                """
                Langkah-langkah pembersihan data yang dilakukan:
                -   Mengubah kolom 'Date' ke format datetime.
                -   Mengisi nilai 'Engagements' yang kosong dengan 0.
                -   Menormalisasi nama kolom (mengubah ke huruf kecil dan mengganti spasi dengan garis bawah).
                """
            )

            # --- Data Cleaning ---
            # Normalize column names for easier access
            df.columns = df.columns.str.lower().str.replace(' ', '_')

            # Convert 'date' to datetime format
            df['date'] = pd.to_datetime(df['date'], errors='coerce') # Coerce errors will turn invalid dates into NaT

            # Fill empty 'engagements' with 0 and convert to numeric
            df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0).astype(int)

            # Drop rows where 'date' became NaT due to errors
            df.dropna(subset=['date'], inplace=True)

            st.success("Pembersihan data selesai!")
            st.subheader("Pratinjau Data Setelah Dibersihkan:")
            st.dataframe(df.head())

            st.markdown("---")
            st.header("3. Visualisasi Interaktif & Insight")
            st.markdown("Gunakan filter di sidebar untuk menyesuaikan tampilan data dan mendapatkan insight yang spesifik.")

            # --- Sidebar: Filters ---
            st.sidebar.header("Filter Data")
            with st.sidebar.expander("Klik untuk Mengatur Filter"):
                # Filter Platform
                unique_platforms = ['Semua'] + df['platform'].unique().tolist()
                selected_platforms = st.multiselect("Pilih Platform(s)", unique_platforms, default=['Semua'])

                # Filter Sentiment
                unique_sentiments = ['Semua'] + df['sentiment'].unique().tolist()
                selected_sentiments = st.multiselect("Pilih Sentimen(s)", unique_sentiments, default=['Semua'])

                # Filter Media Type
                unique_media_types = ['Semua'] + df['media_type'].unique().tolist()
                selected_media_types = st.multiselect("Pilih Tipe Media(s)", unique_media_types, default=['Semua'])

                # Filter Location
                unique_locations = ['Semua'] + df['location'].unique().tolist()
                selected_locations = st.multiselect("Pilih Lokasi(s)", unique_locations, default=['Semua'])

                # Date Range Filter
                min_date = df['date'].min().date()
                max_date = df['date'].max().date()
                date_range_values = st.date_input(
                    "Pilih Rentang Tanggal",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
                start_date_filter = date_range_values[0]
                end_date_filter = date_range_values[1] if len(date_range_values) > 1 else date_range_values[0]


            # Apply filters
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
                st.warning("Tidak ada data yang cocok dengan filter yang dipilih. Harap sesuaikan filter Anda.")
            else:
                # --- Row 1: Sentiment Breakdown & Engagement Trend ---
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("3.1. Pie Chart: Sentiment Breakdown")
                    sentiment_counts = df_filtered['sentiment'].value_counts().reset_index()
                    sentiment_counts.columns = ['sentiment', 'count']
                    fig_sentiment = px.pie(sentiment_counts, values='count', names='sentiment',
                                           title='**Distribusi Sentimen**',
                                           color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_sentiment.update_layout(title_x=0.5) # Center title
                    st.plotly_chart(fig_sentiment, use_container_width=True)
                    st.markdown("#### Insight:")
                    for insight in get_insights("Sentiment Breakdown", df_filtered):
                        st.markdown(f"- {insight}")

                with col2:
                    st.subheader("3.2. Line Chart: Engagement Trend over Time")
                    engagement_over_time = df_filtered.groupby(df_filtered['date'].dt.to_period('W'))['engagements'].sum().reset_index()
                    engagement_over_time['date'] = engagement_over_time['date'].dt.start_time
                    fig_engagement_trend = px.line(engagement_over_time, x='date', y='engagements',
                                                 title='**Tren Engagement dari Waktu ke Waktu (Mingguan)**', markers=True)
                    fig_engagement_trend.update_xaxes(title_text='Tanggal (Awal Minggu)')
                    fig_engagement_trend.update_yaxes(title_text='Total Engagements')
                    fig_engagement_trend.update_layout(title_x=0.5) # Center title
                    st.plotly_chart(fig_engagement_trend, use_container_width=True)
                    st.markdown("#### Insight:")
                    for insight in get_insights("Engagement Trend over Time", df_filtered):
                        st.markdown(f"- {insight}")

                st.markdown("---") # Separator

                # --- Row 2: Platform Engagements & Media Type Mix ---
                col3, col4 = st.columns(2)

                with col3:
                    st.subheader("3.3. Bar Chart: Platform Engagements")
                    platform_engagements = df_filtered.groupby('platform')['engagements'].sum().sort_values(ascending=True).reset_index() # Ascending for better bar order
                    fig_platform = px.bar(platform_engagements, x='engagements', y='platform', orientation='h',
                                         title='**Total Engagement per Platform**',
                                         color='platform',
                                         color_discrete_sequence=px.colors.qualitative.Set2)
                    fig_platform.update_xaxes(title_text='Total Engagements')
                    fig_platform.update_yaxes(title_text='Platform', categoryarray=platform_engagements['platform'].tolist(), categoryorder="array") # Ensure order
                    fig_platform.update_layout(title_x=0.5) # Center title
                    st.plotly_chart(fig_platform, use_container_width=True)
                    st.markdown("#### Insight:")
                    for insight in get_insights("Platform Engagements", df_filtered):
                        st.markdown(f"- {insight}")

                with col4:
                    st.subheader("3.4. Pie Chart: Media Type Mix")
                    media_type_counts = df_filtered['media_type'].value_counts().reset_index()
                    media_type_counts.columns = ['media_type', 'count']
                    fig_media_type = px.pie(media_type_counts, values='count', names='media_type',
                                           title='**Distribusi Tipe Media**',
                                           color_discrete_sequence=px.colors.qualitative.Vivid)
                    fig_media_type.update_layout(title_x=0.5) # Center title
                    st.plotly_chart(fig_media_type, use_container_width=True)
                    st.markdown("#### Insight:")
                    for insight in get_insights("Media Type Mix", df_filtered):
                        st.markdown(f"- {insight}")

                st.markdown("---") # Separator

                # --- Row 3: Top 5 Locations ---
                st.subheader("3.5. Bar Chart: Top 5 Locations by Engagement")
                top_locations = df_filtered.groupby('location')['engagements'].sum().nlargest(5).sort_values(ascending=True).reset_index()
                fig_locations = px.bar(top_locations, x='engagements', y='location', orientation='h',
                                      title='**Top 5 Lokasi Berdasarkan Total Engagement**',
                                      color='location',
                                      color_discrete_sequence=px.colors.qualitative.Dark24)
                fig_locations.update_xaxes(title_text='Total Engagements')
                fig_locations.update_yaxes(title_text='Lokasi', categoryarray=top_locations['location'].tolist(), categoryorder="array")
                fig_locations.update_layout(title_x=0.5) # Center title
                st.plotly_chart(fig_locations, use_container_width=True)
                st.markdown("#### Insight:")
                for insight in get_insights("Top 5 Locations", df_filtered):
                    st.markdown(f"- {insight}")

                st.markdown("---") # Separator

                # --- Key Action Summary ---
                st.header("4. Ringkasan Strategi Kampanye & Tindakan Kunci")
                st.markdown(
                    """
                    Berdasarkan analisis data yang telah dilakukan, berikut adalah ringkasan strategi kampanye dan tindakan kunci yang direkomendasikan:

                    * **Fokus pada Konten Positif:** Terus kembangkan konten yang membangkitkan sentimen positif. Identifikasi elemen kunci dari konten yang berhasil dan replikasi.
                    * **Optimalkan Platform Unggulan:** Alokasikan lebih banyak sumber daya dan perhatian pada platform yang menunjukkan engagement tertinggi. Pertimbangkan strategi khusus untuk mempertahankan dan meningkatkan performa di platform tersebut.
                    * **Diversifikasi & Eksperimen Format Media:** Meskipun ada tipe media yang dominan, terus lakukan eksperimen dengan format media lain untuk melihat respon audiens yang berbeda dan menjangkau segmen baru.
                    * **Targetkan Lokasi Kunci:** Fokuskan upaya pemasaran dan distribusi konten di lokasi-lokasi dengan engagement tertinggi. Pertimbangkan konten atau kampanye yang terlokalisasi untuk area ini.
                    * **Pantau Tren Engagement Berkala:** Lakukan pemantauan rutin terhadap tren engagement untuk mengidentifikasi pola musiman, dampak kampanye, dan anomali. Ini memungkinkan respons cepat terhadap perubahan performa.
                    * **Analisis Mendalam Sentimen Negatif (jika ada):** Jika sentimen negatif signifikan, lakukan analisis akar masalah untuk mengidentifikasi penyebabnya (misalnya, isu produk, layanan pelanggan, atau miskomunikasi) dan segera tangani.
                    """
                )

        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca atau memproses file: {e}")
            st.info("Harap pastikan file CSV Anda memiliki kolom yang benar: 'Date', 'Platform', 'Sentiment', 'Location', 'Engagements', 'Media Type' dan format datanya valid.")

else:
    st.info("Silakan unggah file CSV Anda di sidebar untuk memulai analisis.")

st.sidebar.markdown("---")
st.sidebar.markdown("Dibuat dengan ❤️ oleh [Nama Kelompok Anda/Nama Anda]") # Ganti dengan nama kelompok/nama Anda
