# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import datetime

# --- Helper Function to get Insights ---
# Fungsi ini menghasilkan insight berdasarkan data yang difilter
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
        # Group by week and sum engagements
        df_filtered_weekly = df_filtered.groupby(df_filtered['date'].dt.to_period('W'))['engagements'].sum().reset_index()
        df_filtered_weekly['date'] = df_filtered_weekly['date'].dt.start_time # Convert Period back to Timestamp for Plotly

        if not df_filtered_weekly.empty:
            if not df_filtered_weekly['engagements'].empty: # Check if engagements column is not empty after grouping
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
            # Aggregate engagements by location
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
    .css-1d391kg { /* sidebar background */
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #4CAF50; /* Green */
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border: none;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049; /* Darker green on hover */
    }
    h1, h2, h3, h4, h5, h6 {
        color: #262730; /* Darker text for headers */
    }
    .stAlert {
        border-radius: 0.5rem;
    }
    .stMarkdown h4 {
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        color: #333; /* Slightly lighter header for insights */
    }
    .stMarkdown ul {
        list-style-type: disc;
        margin-left: 20px;
    }
    .stMarkdown li {
        margin-bottom: 5px;
    }
    /* Style for KPI boxes */
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem; /* Larger font for KPI numbers */
        color: #262730;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# --- Main Title ---
st.title("📊 Interactive Media Intelligence Dashboard")
st.markdown("""
Selamat datang di Dashboard Analisis Kampanye!
Unggah file CSV Anda untuk mendapatkan *insight* mendalam tentang performa media.
""")
st.markdown("---") # Garis pemisah

# --- Sidebar: Upload File ---
st.sidebar.header("1. Unggah File CSV Anda")
uploaded_file = st.sidebar.file_uploader(
    "Seret & Lepas atau Klik untuk Unggah file CSV Anda",
    type=["csv"],
    help="Pastikan file CSV memiliki kolom: Date, Platform, Sentiment, Location, Engagements, Media Type."
)

df = None # Inisialisasi DataFrame menjadi None

if uploaded_file is not None:
    with st.spinner('Memproses file dan menyiapkan dashboard... Mohon tunggu sebentar!'): # Indikator loading yang lebih informatif
        try:
            df = pd.read_csv(uploaded_file)
            st.sidebar.success("File berhasil diunggah!")

            st.header("2. Pembersihan Data")
            st.markdown(
                """
                Langkah-langkah pembersihan data yang dilakukan secara otomatis:
                -   Mengubah kolom **'Date'** ke format datetime.
                -   Mengisi nilai **'Engagements'** yang kosong (missing) dengan 0.
                -   Menormalisasi nama kolom (mengubah ke huruf kecil dan mengganti spasi dengan garis bawah).
                """
            )

            # --- Data Cleaning ---
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0).astype(int)
            df.dropna(subset=['date'], inplace=True)

            st.success("Pembersihan data selesai!")
            st.subheader("Pratinjau Data Setelah Dibersihkan:")
            st.dataframe(df.head())

            st.markdown("---")
            st.header("3. Visualisasi Interaktif & Insight")
            st.markdown("Gunakan filter di sidebar untuk menyesuaikan tampilan data dan mendapatkan *insight* yang spesifik.")

            # --- Sidebar: Filters ---
            st.sidebar.header("Filter Data")
            with st.sidebar.expander("Klik untuk Mengatur Filter"):
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
                st.subheader("3.0. Key Performance Indicators (KPIs)")
                kpi1, kpi2, kpi3 = st.columns(3)

                with kpi1:
                    total_engagements_kpi = df_filtered['engagements'].sum()
                    st.metric(label="Total Engagements", value=f"{total_engagements_kpi:,.0f}")
                    # You could add a delta here if comparing to a previous period

                with kpi2:
                    unique_platforms_kpi = df_filtered['platform'].nunique()
                    st.metric(label="Jumlah Platform Aktif", value=f"{unique_platforms_kpi}")

                with kpi3:
                    # Example of another KPI, e.g., Average Engagements per Item (if you had an 'item_id' column)
                    # For now, let's use number of data points (rows)
                    num_data_points_kpi = len(df_filtered)
                    st.metric(label="Jumlah Data Point", value=f"{num_data_points_kpi:,.0f}")

                st.markdown("---") # Separator

                # --- Row 1: Sentiment Breakdown & Engagement Trend ---
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("3.1. Pie Chart: Sentiment Breakdown")
                    sentiment_counts = df_filtered['sentiment'].value_counts().reset_index()
                    sentiment_counts.columns = ['sentiment', 'count']
                    fig_sentiment = px.pie(sentiment_counts, values='count', names='sentiment',
                                           title='**Distribusi Sentimen**',
                                           color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_sentiment.update_layout(title_x=0.5)
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
                    fig_engagement_trend.update_layout(title_x=0.5)
                    st.plotly_chart(fig_engagement_trend, use_container_width=True)
                    st.markdown("#### Insight:")
                    for insight in get_insights("Engagement Trend over Time", df_filtered):
                        st.markdown(f"- {insight}")

                st.markdown("---")

                # --- Row 2: Platform Engagements & Media Type Mix ---
                col3, col4 = st.columns(2)

                with col3:
                    st.subheader("3.3. Bar Chart: Platform Engagements")
                    platform_engagements = df_filtered.groupby('platform')['engagements'].sum().sort_values(ascending=True).reset_index()
                    fig_platform = px.bar(platform_engagements, x='engagements', y='platform', orientation='h',
                                         title='**Total Engagement per Platform**',
                                         color='platform',
                                         color_discrete_sequence=px.colors.qualitative.Set2)
                    fig_platform.update_xaxes(title_text='Total Engagements')
                    fig_platform.update_yaxes(title_text='Platform', categoryarray=platform_engagements['platform'].tolist(), categoryorder="array")
                    fig_platform.update_layout(title_x=0.5)
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
                    fig_media_type.update_layout(title_x=0.5)
                    st.plotly_chart(fig_media_type, use_container_width=True)
                    st.markdown("#### Insight:")
                    for insight in get_insights("Media Type Mix", df_filtered):
                        st.markdown(f"- {insight}")

                st.markdown("---")

                # --- Row 3: Top 5 Locations & Geographical Engagement ---
                st.subheader("3.5. Top 5 Locations by Engagement")
                top_locations = df_filtered.groupby('location')['engagements'].sum().nlargest(5).sort_values(ascending=True).reset_index()
                fig_locations = px.bar(top_locations, x='engagements', y='location', orientation='h',
                                      title='**Top 5 Lokasi Berdasarkan Total Engagement**',
                                      color='location',
                                      color_discrete_sequence=px.colors.qualitative.Dark24)
                fig_locations.update_xaxes(title_text='Total Engagements')
                fig_locations.update_yaxes(title_text='Lokasi', categoryarray=top_locations['location'].tolist(), categoryorder="array")
                fig_locations.update_layout(title_x=0.5)
                st.plotly_chart(fig_locations, use_container_width=True)
                st.markdown("#### Insight:")
                for insight in get_insights("Top 5 Locations", df_filtered):
                    st.markdown(f"- {insight}")

                # --- Geographical Map (Experimental - Requires valid location data) ---
                st.subheader("3.6. Peta Engagement Geografis (Eksperimental)")
                st.info("Peta ini akan bekerja paling baik jika kolom 'Location' Anda berisi nama kota atau negara yang dapat dikenali oleh Plotly.")
                try:
                    location_engagements_map = df_filtered.groupby('location')['engagements'].sum().reset_index()
                    location_engagements_map.columns = ['location', 'total_engagements']
                    # Use px.choropleth or px.scatter_geo. px.scatter_geo is more flexible for varied location data.
                    fig_geo = px.scatter_geo(
                        location_engagements_map,
                        locations="location",
                        locationmode="country names", # Adjust based on your 'location' column data (e.g., 'country names', 'USA-states', 'ISO-3')
                        size="total_engagements",
                        hover_name="location",
                        color="total_engagements",
                        title="**Peta Engagement Berdasarkan Lokasi**",
                        projection="natural earth" # You can experiment with 'natural earth', 'orthographic', etc.
                    )
                    fig_geo.update_layout(title_x=0.5)
                    st.plotly_chart(fig_geo, use_container_width=True)
                    st.markdown("#### Insight:")
                    for insight in get_insights("Geographical Engagement", df_filtered):
                        st.markdown(f"- {insight}")

                except Exception as e:
                    st.warning(f"Tidak dapat membuat peta geografis: {e}. Pastikan data 'Location' Anda valid (nama kota/negara) dan konsisten.")
                    st.info("Jika data lokasi Anda tidak dikenali oleh Plotly (misalnya, hanya nama provinsi atau kode lokal), peta mungkin tidak muncul.")


                st.markdown("---")

                # --- Key Action Summary ---
                st.header("4. Ringkasan Strategi Kampanye & Tindakan Kunci")
                st.markdown(
                    """
                    Berdasarkan analisis data yang telah dilakukan, berikut adalah ringkasan strategi kampanye dan tindakan kunci yang direkomendasikan:

                    * **Fokus pada Konten Positif:** Terus kembangkan konten yang membangkitkan sentimen positif. Identifikasi elemen kunci dari konten yang berhasil dan replikasi.
                    * **Optimalkan Platform Unggulan:** Alokasikan lebih banyak sumber daya dan perhatian pada *platform* yang menunjukkan *engagement* tertinggi. Pertimbangkan strategi khusus untuk mempertahankan dan meningkatkan performa di *platform* tersebut.
                    * **Diversifikasi & Eksperimen Format Media:** Meskipun ada tipe media yang dominan, terus lakukan eksperimen dengan format media lain untuk melihat respon audiens yang berbeda dan menjangkau segmen baru.
                    * **Targetkan Lokasi Kunci:** Fokuskan upaya pemasaran dan distribusi konten di lokasi-lokasi dengan *engagement* tertinggi. Pertimbangkan konten atau kampanye yang terlokalisasi untuk area ini.
                    * **Pantau Tren Engagement Berkala:** Lakukan pemantauan rutin terhadap tren *engagement* untuk mengidentifikasi pola musiman, dampak kampanye, dan anomali. Ini memungkinkan respons cepat terhadap perubahan performa.
                    * **Analisis Mendalam Sentimen Negatif (jika ada):** Jika sentimen negatif signifikan, lakukan analisis akar masalah untuk mengidentifikasi penyebabnya (misalnya, isu produk, layanan pelanggan, atau miskomunikasi) dan segera tangani.
                    """
                )

                st.markdown("---")
                # --- Export Data Button ---
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


        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca atau memproses file: {e}")
            st.info("Harap pastikan file CSV Anda memiliki kolom yang benar: **'Date', 'Platform', 'Sentiment', 'Location', 'Engagements', 'Media Type'** dan format datanya valid.")

else:
    st.info("Silakan unggah file CSV Anda di sidebar untuk memulai analisis.")

st.sidebar.markdown("---")
st.sidebar.markdown("Dibuat dengan ❤️ oleh Shannon Sifra - 2306221705")
