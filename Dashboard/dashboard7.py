import pandas as pd
import streamlit as st
import datetime
import plotly.express as px
from pathlib import Path

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
        template="plotly_dark",  # Menggunakan template plotly yang lebih modern
        height=500
    )
    fig.update_layout(
        title_font_size=24, 
        title_x=0.5,
        xaxis_title=attribute1.capitalize(),
        yaxis_title=attribute2.capitalize()
    )
    st.plotly_chart(fig)

# Fungsi untuk menampilkan sidebar dengan informasi tambahan
def sidebar(df):
    df["datetime"] = pd.to_datetime(df["datetime"])  # Pastikan kolom datetime adalah tipe datetime
    min_date = df["datetime"].min()
    max_date = df["datetime"].max()

    with st.sidebar:
        st.image("https://github.com/user-attachments/assets/57c8a3f1-9d7f-44d5-986b-25cdede86de9", caption="Eksplorasi Pembagian Sepeda", use_column_width=True)
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

# Fungsi utama
if __name__ == "__main__":
    st.set_page_config(
        page_title="Dashboard Peminjaman Sepeda",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Tampilan halaman dengan background abu-abu gradasi
    st.markdown("""
        <style>
        body {
            background: linear-gradient(to right, #6e7dff, #a8b6ff);
            color: white;
            font-family: 'Arial', sans-serif;
        }
        .css-1d391kg {
            background-color: rgba(0,0,0,0.3);
        }
        h1 {
            font-size: 36px;
            color: white;
            text-align: center;
            margin-bottom: 20px;
        }
        .stMetric {
            background-color: rgba(255,255,255,0.2);
            padding: 10px;
            border-radius: 10px;
        }
        .stButton>button {
            background-color: #6e7dff;
            color: white;
            border-radius: 5px;
            padding: 12px 30px;
            border: none;
            font-size: 18px;
        }
        .stButton>button:hover {
            background-color: #a8b6ff;
        }
        .css-1kyxreq {
            padding-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🚴‍♂️ **Dashboard Peminjaman Sepeda**")
    st.markdown("""
    Selamat datang di **Dashboard Peminjaman Sepeda**! 🚲  
    Di sini, Anda dapat mengeksplorasi wawasan utama tentang pola penggunaan sepeda seiring waktu.  
    Anda dapat memfilter data dengan memilih rentang tanggal yang berbeda dan menganalisis berbagai tren peminjaman sepeda.
    """)

    # Menampilkan ikon dan tombol upload file
    st.markdown("<h2 style='text-align: center;'>🎯 Eksplorasi Data Peminjaman</h2>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'><i class='fas fa-cloud-upload-alt'></i></div>", unsafe_allow_html=True)
    st.markdown("""
    **Inputkan file CSV untuk menampilkan Dataframe (Dashboard):**
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])

    if uploaded_file is not None:
        days_df = pd.read_csv(uploaded_file)
        st.success("File berhasil diunggah!")
        
        date = sidebar(days_df)

        # Menangani kasus jika hanya satu tanggal yang dipilih
        if len(date) == 2:
            selected_date_range = (pd.to_datetime(date[0]), pd.to_datetime(date[1]))
        else:
            selected_date_range = (pd.to_datetime(date[0]), pd.to_datetime(date[0]))

        # Filter berdasarkan rentang tanggal
        main_df = days_df[(days_df["datetime"] >= selected_date_range[0]) & (days_df["datetime"] <= selected_date_range[1])]

        # Visualisasi metrik utama dengan desain yang lebih menarik
        st.markdown("### Wawasan Utama")
        col1, col2, col3 = st.columns(3)

        with col1:
            daily_rent_casual = main_df['casual'].sum()
            st.metric("👤 Pengguna Kasual", value=f"{daily_rent_casual:,}", delta=daily_rent_casual * 0.02, delta_color="normal")

        with col2:
            daily_rent_registered = main_df['registered'].sum()
            st.metric("🧑‍💼 Pengguna Terdaftar", value=f"{daily_rent_registered:,}", delta=daily_rent_registered * 0.02, delta_color="normal")

        with col3:
            daily_rent_total = main_df['count'].sum()
            st.metric("📊 Total Sewa", value=f"{daily_rent_total:,}", delta=daily_rent_total * 0.02, delta_color="normal")

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

        # Visualisasi proporsi penggunaan sepeda di hari kerja vs hari libur
        st.markdown("### Proporsi Penggunaan Sepeda di Hari Kerja vs Hari Libur")
        workday_vs_holiday_df = main_df.groupby("weekday")[['casual', 'registered']].sum().reset_index()
        workday_vs_holiday_df["total"] = workday_vs_holiday_df['casual'] + workday_vs_holiday_df['registered']
        fig_workday = px.pie(
            workday_vs_holiday_df,
            names="weekday",
            values="total",
            title="Proporsi Penggunaan Sepeda di Hari Kerja vs Hari Libur",
            labels={"weekday": "Hari Kerja/Hari Libur", "total": "Jumlah Sewa"},
            template="plotly_dark"
        )
        st.plotly_chart(fig_workday)

        # Visualisasi perbandingan berdasarkan atribut
        st.markdown("### Wawasan Perbandingan Data")
        comparison_attributes = [("season", "weather_condition"), 
                                ("weekday", "month"), 
                                ("year", "weather_condition")]
        
        for attribute1, attribute2 in comparison_attributes:
            create_comparison_chart(main_df, attribute1, attribute2, f"Perbandingan antara {attribute1.capitalize()} dan {attribute2.capitalize()}")

        # Informasi footer
        year_copyright = datetime.date.today().year
        st.markdown(f"""
        ---
        ### **Tentang Dashboard Ini:**
        Dashboard ini memvisualisasikan penggunaan sepeda berdasarkan kondisi cuaca, musim, dan lebih banyak faktor lainnya. Ini dirancang untuk membantu kota-kota dan organisasi memahami pola penggunaan sepeda untuk mengoptimalkan layanan peminjaman sepeda.
        
        **Sumber Data:** Data Peminjaman Sepeda Publik.
        
        © {year_copyright} Zahwa Genoveva | Dashboard dibuat dengan ❤️ menggunakan Streamlit.
        """)
