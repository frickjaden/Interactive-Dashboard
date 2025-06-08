import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Set page configuration for a wider layout
st.set_page_config(layout="wide", page_title="Interactive Media Intelligence Dashboard")

# --- 1. Title the notebook and ask for file upload ---
st.title("Interactive Media Intelligence Dashboard")
st.write("Selamat datang di Dashboard Intelijen Media! Silakan unggah file CSV Anda untuk memulai analisis.")

uploaded_file = st.file_uploader(
    "Unggah file CSV Anda",
    type=["csv"],
    help="Pastikan file CSV memiliki kolom: Date, Platform, Sentiment, Location, Engagements, Media Type."
)

if uploaded_file is not None:
    # Read the CSV file into a Pandas DataFrame
    try:
        df = pd.read_csv(uploaded_file)
        st.success("File berhasil diunggah!")
    except Exception as e:
        st.error(f"Error membaca file: {e}. Pastikan ini adalah file CSV yang valid.")
        st.stop() # Stop execution if file cannot be read

    # --- 2. Clean the data ---
    st.header("1. Pembersihan Data")
    st.info("Melakukan pembersihan data: konversi tanggal, mengisi nilai hilang, dan normalisasi nama kolom.")

    # Convert 'Date' to datetime, handling potential errors
    try:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # Drop rows where date conversion failed
        df.dropna(subset=['Date'], inplace=True)
    except KeyError:
        st.warning("Kolom 'Date' tidak ditemukan. Pastikan nama kolom sudah benar.")
        df['Date'] = pd.NaT # Assign NaT if column is missing to prevent further errors
    except Exception as e:
        st.warning(f"Gagal mengkonversi kolom 'Date' ke format tanggal: {e}. Beberapa analisis mungkin terpengaruh.")

    # Fill missing 'Engagements' with 0
    try:
        df['Engagements'] = pd.to_numeric(df['Engagements'], errors='coerce').fillna(0)
    except KeyError:
        st.warning("Kolom 'Engagements' tidak ditemukan. Pastikan nama kolom sudah benar.")
        df['Engagements'] = 0 # Assign 0 if column is missing
    except Exception as e:
        st.warning(f"Gagal mengkonversi kolom 'Engagements' ke numerik atau mengisi nilai hilang: {e}. Mengisi dengan 0.")
        df['Engagements'] = df['Engagements'].fillna(0) # Fallback to fillna

    # Normalize column names (lowercase and replace spaces with underscores)
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    # Display a snippet of the cleaned data
    st.subheader("Cuplikan Data Setelah Pembersihan:")
    st.dataframe(df.head())

    # Ensure required columns exist after cleaning and normalization
    required_cols = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Kolom yang diperlukan tidak ditemukan setelah pembersihan. Pastikan CSV Anda memiliki: {', '.join(col.capitalize() for col in required_cols)}.")
        st.stop() # Stop execution if critical columns are missing

    # --- 3. Build 5 interactive charts using Plotly ---
    st.header("2. Visualisasi Data Interaktif")
    st.write("Jelajahi insight utama dari data media Anda melalui visualisasi interaktif.")

    # Placeholder function for generating AI insights
    # In a real application, this would call an LLM API (e.g., Gemini, OpenRouter via OpenAI SDK)
    def generate_ai_insights(chart_title, data_summary, context):
        # This is a mock function. Replace with actual LLM API call.
        # Example using Gemini/OpenRouter API (requires 'openai' library and API key securely stored)
        # from openai import OpenAI
        # client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"])
        # response = client.chat.completions.create(
        #     model="mistralai/mistral-7b-instruct:free", # Example model, choose based on OpenRouter availability
        #     messages=[
        #         {"role": "user", "content": f"Generate 3 key insights for a chart titled '{chart_title}' based on the following data summary: {data_summary}. Context: {context}. Focus on actionable insights for media production/marketing."}
        #     ]
        # )
        # insights_text = response.choices[0].message.content
        # return insights_text.split('\n')[:3] # Assuming insights are line-separated

        # For demonstration, we provide generic insights based on chart type
        insights = []
        if "Sentiment Breakdown" in chart_title:
            total_sentiments = df['sentiment'].value_counts().sum()
            positive_percent = (df['sentiment'].value_counts().get('Positive', 0) / total_sentiments) * 100 if total_sentiments > 0 else 0
            negative_percent = (df['sentiment'].value_counts().get('Negative', 0) / total_sentiments) * 100 if total_sentiments > 0 else 0
            insights.append(f"Mayoritas sentimen adalah {df['sentiment'].mode()[0]} ({df['sentiment'].value_counts().max()} kasus), menunjukkan [persepsi umum].")
            insights.append(f"Proporsi sentimen positif ({positive_percent:.1f}%) dan negatif ({negative_percent:.1f}%) dapat mengindikasikan [area kekuatan/kelemahan].")
            insights.append("Perhatikan sentimen netral yang signifikan; ini bisa menjadi peluang untuk [strategi konten baru].")
        elif "Engagement Trend" in chart_title:
            max_engagement_date = df.groupby('date')['engagements'].sum().idxmax()
            min_engagement_date = df.groupby('date')['engagements'].sum().idxmin()
            insights.append(f"Puncak engagement terjadi pada {max_engagement_date.strftime('%Y-%m-%d')}, mungkin terkait dengan [kampanye/event tertentu].")
            insights.append(f"Penurunan engagement pada {min_engagement_date.strftime('%Y-%m-%d')} perlu dianalisis lebih lanjut untuk [faktor penyebab].")
            insights.append("Pola tren engagement menunjukkan [musiman/keefektifan strategi jangka panjang].")
        elif "Platform Engagements" in chart_title:
            top_platform = df.groupby('platform')['engagements'].sum().nlargest(1).index[0]
            insights.append(f"Platform {top_platform} mendominasi engagement, mengindikasikan [fokus audiens di platform tersebut].")
            insights.append("Disparitas engagement antar platform menunjukkan [peluang untuk mengoptimalkan distribusi konten].")
            insights.append("Platform dengan engagement rendah mungkin memerlukan [strategi konten yang disesuaikan atau investasi ulang].")
        elif "Media Type Mix" in chart_title:
            top_media_type = df['media_type'].value_counts().nlargest(1).index[0]
            insights.append(f"Tipe media '{top_media_type}' paling populer, sarankan [produksi konten lebih lanjut dalam format ini].")
            insights.append("Variasi dalam distribusi tipe media dapat mengidentifikasi [preferensi audiens yang beragam].")
            insights.append("Tipe media yang kurang berkinerja dapat dieksplorasi untuk [format baru atau targeting ulang].")
        elif "Top 5 Locations" in chart_title:
            top_location = df.groupby('location')['engagements'].sum().nlargest(1).index[0]
            insights.append(f"Lokasi '{top_location}' menunjukkan engagement tertinggi, menyoroti [pentingnya konten yang dilokalkan].")
            insights.append("Data lokasi dapat memandu [targeting iklan geografis atau pengembangan konten regional].")
            insights.append("Perbedaan engagement antar lokasi menunjukkan [peluang ekspansi atau penyesuaian strategi pasar].")
        return insights


    # --- 3.1. Sentiment Breakdown (Pie Chart) ---
    st.subheader("3.1. Sentiment Breakdown")
    if 'sentiment' in df.columns:
        sentiment_counts = df['sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig_sentiment = px.pie(
            sentiment_counts,
            values='Count',
            names='Sentiment',
            title='Distribusi Sentimen',
            hole=0.3
        )
        fig_sentiment.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_sentiment, use_container_width=True)

        # Generate insights for Sentiment Breakdown
        st.markdown("### Top 3 Insights:")
        insights_sentiment = generate_ai_insights(
            "Sentiment Breakdown",
            df['sentiment'].value_counts().to_dict(),
            "Analisis persepsi publik terhadap merek/konten."
        )
        for i, insight in enumerate(insights_sentiment):
            st.write(f"- {insight}")
    else:
        st.warning("Kolom 'sentiment' tidak ditemukan untuk visualisasi ini.")


    # --- 3.2. Engagement Trend Over Time (Line Chart) ---
    st.subheader("3.2. Engagement Trend Over Time")
    if 'date' in df.columns and 'engagements' in df.columns:
        # Group by date and sum engagements
        daily_engagements = df.groupby(df['date'].dt.date)['engagements'].sum().reset_index()
        daily_engagements.columns = ['Date', 'Total Engagements']
        fig_engagement_trend = px.line(
            daily_engagements,
            x='Date',
            y='Total Engagements',
            title='Tren Engagement Seiring Waktu',
            markers=True
        )
        fig_engagement_trend.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        st.plotly_chart(fig_engagement_trend, use_container_width=True)

        # Generate insights for Engagement Trend Over Time
        st.markdown("### Top 3 Insights:")
        insights_engagement_trend = generate_ai_insights(
            "Engagement Trend Over Time",
            daily_engagements.to_dict('list'),
            "Melacak performa kampanye media dan mengidentifikasi puncak/penurunan."
        )
        for i, insight in enumerate(insights_engagement_trend):
            st.write(f"- {insight}")
    else:
        st.warning("Kolom 'date' atau 'engagements' tidak ditemukan untuk visualisasi ini.")

    # --- 3.3. Platform Engagements (Bar Chart) ---
    st.subheader("3.3. Platform Engagements")
    if 'platform' in df.columns and 'engagements' in df.columns:
        platform_engagements = df.groupby('platform')['engagements'].sum().reset_index()
        platform_engagements = platform_engagements.sort_values(by='engagements', ascending=False)
        fig_platform_engagements = px.bar(
            platform_engagements,
            x='platform',
            y='engagements',
            title='Engagement per Platform',
            labels={'platform': 'Platform Media', 'engagements': 'Total Engagement'}
        )
        st.plotly_chart(fig_platform_engagements, use_container_width=True)

        # Generate insights for Platform Engagements
        st.markdown("### Top 3 Insights:")
        insights_platform_engagements = generate_ai_insights(
            "Platform Engagements",
            platform_engagements.to_dict('list'),
            "Membandingkan kinerja engagement di berbagai platform media sosial atau portal berita."
        )
        for i, insight in enumerate(insights_platform_engagements):
            st.write(f"- {insight}")
    else:
        st.warning("Kolom 'platform' atau 'engagements' tidak ditemukan untuk visualisasi ini.")

    # --- 3.4. Media Type Mix (Pie Chart) ---
    st.subheader("3.4. Media Type Mix")
    if 'media_type' in df.columns:
        media_type_counts = df['media_type'].value_counts().reset_index()
        media_type_counts.columns = ['Media Type', 'Count']
        fig_media_type_mix = px.pie(
            media_type_counts,
            values='Count',
            names='Media Type',
            title='Distribusi Tipe Media',
            hole=0.3
        )
        fig_media_type_mix.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_media_type_mix, use_container_width=True)

        # Generate insights for Media Type Mix
        st.markdown("### Top 3 Insights:")
        insights_media_type_mix = generate_ai_insights(
            "Media Type Mix",
            media_type_counts.to_dict(),
            "Menganalisis proporsi tipe media memberikan insight tentang format konten yang paling disukai."
        )
        for i, insight in enumerate(insights_media_type_mix):
            st.write(f"- {insight}")
    else:
        st.warning("Kolom 'media_type' tidak ditemukan untuk visualisasi ini.")

    # --- 3.5. Top 5 Locations by Engagement (Bar Chart) ---
    st.subheader("3.5. Top 5 Locations by Engagement")
    if 'location' in df.columns and 'engagements' in df.columns:
        location_engagements = df.groupby('location')['engagements'].sum().nlargest(5).reset_index()
        fig_top_locations = px.bar(
            location_engagements,
            x='engagements',
            y='location',
            orientation='h',
            title='Top 5 Lokasi Berdasarkan Engagement',
            labels={'location': 'Lokasi', 'engagements': 'Total Engagement'}
        )
        fig_top_locations.update_layout(yaxis={'categoryorder':'total ascending'}) # Ensure largest is at the top
        st.plotly_chart(fig_top_locations, use_container_width=True)

        # Generate insights for Top 5 Locations
        st.markdown("### Top 3 Insights:")
        insights_top_locations = generate_ai_insights(
            "Top 5 Locations by Engagement",
            location_engagements.to_dict('list'),
            "Mengidentifikasi lokasi geografis dengan engagement tertinggi, relevan untuk targeting audiens atau produksi konten lokal."
        )
        for i, insight in enumerate(insights_top_locations):
            st.write(f"- {insight}")
    else:
        st.warning("Kolom 'location' atau 'engagements' tidak ditemukan untuk visualisasi ini.")

else:
    st.info("Silakan unggah file CSV Anda di atas untuk melihat dashboard.")


