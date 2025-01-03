import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import datetime

# Fungsi untuk menampilkan sidebar dengan informasi tambahan
def sidebar(df):
    df["datetime"] = pd.to_datetime(df["datetime"])
    min_date = df["datetime"].min()
    max_date = df["datetime"].max()

    with st.sidebar:
        st.title("Filter Data")
        st.markdown("**Pilih rentang tanggal untuk mengeksplorasi data peminjaman sepeda.**")
        date = st.date_input(
            label="Pilih Rentang Tanggal",
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
        st.markdown("**Catatan:** Data tersedia dari rentang yang dipilih.")
    return date

# Fungsi untuk menampilkan sidebar dengan informasi tambahan
def sidebar(df):
    df["datetime"] = pd.to_datetime(df["datetime"])
    min_date = df["datetime"].min()
    max_date = df["datetime"].max()

    with st.sidebar:
        st.image("https://github.com/user-attachments/assets/8227dbaa-6bbf-4c22-aa20-7da3bf874ca1", caption="Eksplorasi Pembagian Sepeda", use_column_width=True)
        st.title("Filter Data")
        st.markdown("**Pilih rentang tanggal untuk mengeksplorasi data peminjaman sepeda.**")
        date = st.date_input(
            label="Pilih Rentang Tanggal", 
            min_value=min_date, 
            max_value=max_date,
            value=[min_date, max_date]
        )
        st.markdown("**Catatan:** Data tersedia dari rentang yang dipilih.")
    return date

# Fungsi untuk membuat visualisasi data menggunakan plotly dengan perbandingan antara dua kolom
def create_comparison_chart(df, attribute1, attribute2, title):
    comparison_df = df.groupby([attribute1, attribute2]).size().reset_index(name='count')

    st.subheader(title)
    fig = px.scatter(
        comparison_df,
        x=attribute1,
        y=attribute2,
        size='count',
        color='count',
        hover_name=attribute2,
        hover_data=[attribute1, 'count'],
        title=title,
        labels={attribute1: attribute1.capitalize(), attribute2: attribute2.capitalize(), 'count': 'Jumlah Sewa'},
        template="plotly_dark",
        height=500
    )
    fig.update_layout(
        title_font_size=24, 
        title_x=0.5,
        xaxis_title=attribute1.capitalize(),
        yaxis_title=attribute2.capitalize()
    )
    st.plotly_chart(fig)

# Fungsi utama
if __name__ == "__main__":
    st.set_page_config(
        page_title="Dashboard Peminjaman Sepeda",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("🚴‍♂️ **Dashboard Peminjaman Sepeda**")
    st.markdown("""
    Selamat datang di Dashboard Peminjaman Sepeda! 🚲  
    Di sini, Anda dapat mengeksplorasi wawasan utama tentang pola penggunaan sepeda seiring waktu.
    Anda dapat memfilter data dengan memilih rentang tanggal yang berbeda dan menganalisis berbagai tren peminjaman sepeda.
    """)

    # Menggunakan jalur relatif untuk memuat file CSV
    days_df_csv = Path(__file__).parent / 'days_clean.csv'
    if not days_df_csv.exists():
        st.error("File 'days_clean.csv' tidak ditemukan. Pastikan file tersebut ada di direktori yang sama dengan skrip.")
    else:
        days_df = pd.read_csv(days_df_csv)

        # Sidebar filter
        date = sidebar(days_df)

        # Menangani kasus jika hanya satu tanggal yang dipilih
        if len(date) == 2:
            selected_date_range = (pd.to_datetime(date[0]), pd.to_datetime(date[1]))
        else:
            selected_date_range = (pd.to_datetime(date[0]), pd.to_datetime(date[0]))

        # Filter berdasarkan rentang tanggal
        main_df = days_df[(days_df["datetime"] >= selected_date_range[0]) & (days_df["datetime"] <= selected_date_range[1])]

        # Wawasan utama
        st.markdown("### Wawasan Utama")
        col1, col2, col3 = st.columns(3)

        with col1:
            daily_rent_casual = main_df['casual'].sum()
            st.metric("Pengguna Kasual", value=f"{daily_rent_casual:,}")

        with col2:
            daily_rent_registered = main_df['registered'].sum()
            st.metric("Pengguna Terdaftar", value=f"{daily_rent_registered:,}")

        with col3:
            daily_rent_total = main_df['count'].sum()
            st.metric("Total Sewa", value=f"{daily_rent_total:,}")

        # Visualisasi proporsi penggunaan sepeda di hari kerja vs hari libur
        st.markdown("### Proporsi Penggunaan Sepeda di Hari Kerja vs Hari Libur")
        main_df["is_working_day"] = main_df["workingday"].replace({1: "Hari Kerja", 0: "Hari Libur"})
        workday_vs_holiday_df = main_df.groupby("is_working_day")["count"].mean().reset_index()
        fig_workday = px.pie(
            workday_vs_holiday_df,
            names="is_working_day",
            values="count",
            title="Proporsi Penggunaan Sepeda di Hari Kerja vs Hari Libur",
            template="plotly_dark"
        )
        st.plotly_chart(fig_workday)

        # Visualisasi rata-rata pengguna sepeda berdasarkan kondisi cuaca
        st.markdown("### Rata-rata Pengguna Sepeda Berdasarkan Kondisi Cuaca")
        weather_avg_df = main_df.groupby("weather_condition")[['casual', 'registered']].mean().reset_index()
        fig_weather = px.bar(
            weather_avg_df,
            x="weather_condition",
            y=["casual", "registered"],
            title="Rata-rata Pengguna Sepeda Berdasarkan Kondisi Cuaca",
            labels={"weather_condition": "Kondisi Cuaca", "value": "Jumlah Pengguna"},
            template="plotly_dark"
        )
        st.plotly_chart(fig_weather)

                # Visualisasi Hubungan Musim dan Kondisi Cuaca
        st.markdown("### Hubungan Musim dan Kondisi Cuaca")
        weather_season_df = main_df.groupby(["season", "weather_condition"])["count"].mean().reset_index()
        fig_weather_season = px.density_heatmap(
            weather_season_df,
            x="season",
            y="weather_condition",
            z="count",
            color_continuous_scale="Viridis",
            labels={"season": "Musim", "weather_condition": "Kondisi Cuaca", "count": "Jumlah Sewa"},
            title="Rata-rata Jumlah Sewa Berdasarkan Musim dan Kondisi Cuaca",
            template="plotly_dark"
        )
        st.plotly_chart(fig_weather_season)

        # Visualisasi perbandingan data
        st.markdown("### Wawasan Perbandingan Data")
        comparison_attributes = [("season", "weather_condition"), 
                                 ("weekday", "month"), 
                                 ("year", "weather_condition")]
        for attribute1, attribute2 in comparison_attributes:
            create_comparison_chart(main_df, attribute1, attribute2, f"Perbandingan {attribute1.capitalize()} vs {attribute2.capitalize()}")



        # Informasi footer
        year_copyright = datetime.date.today().year
        st.markdown(f"""
        ---
        ### **Tentang Dashboard Ini:**
        Dashboard ini memvisualisasikan penggunaan sepeda berdasarkan kondisi cuaca, musim, dan lebih banyak faktor lainnya. 
        **Sumber Data:** Data Peminjaman Sepeda Publik.  
        © {year_copyright} Zahwa Genoveva | Dashboard dibuat dengan ❤️ menggunakan Streamlit.
        """)
