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

# --- Custom CSS for a cleaner look (iPhone-like aesthetic) ---
st.markdown("""
<style>
    /* Global styles */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
        background-color: #F8F8F8; /* Light gray background */
        color: #333333;
    }

    /* Main content container */
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px; /* Limit width for cleaner look */
        margin: auto;
    }

    /* Sidebar styles */
    .css-1d391kg { /* sidebar background */
        background-color: #FFFFFF; /* White sidebar background */
        border-right: 1px solid #EDEDED;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); /* Subtle shadow */
    }

    /* Headers */
    h1 {
        color: #1C1C1E; /* Darker header */
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    h2 {
        color: #2C2C2E;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    h3 {
        color: #3C3C3E;
        font-weight: 500;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    h4 {
        color: #4C4C4E; /* Slightly lighter for insights */
        font-weight: 500;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }

    /* Buttons */
    .stButton
