import streamlit as st
import pandas as pd
import numpy as np
import base64
import os

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Portal & Analisis IMDb Publik",
    page_icon="🍿",
    layout="wide"
)

# CSS Kartu Poster dengan Efek Hover
st.markdown("""
<style>
/* Kontainer Utama Kartu Poster Film */
.anime-card-container {
    position: relative;
    width: 100%;
    border-radius: 12px;
    overflow: hidden;
    background-color: #121212;
    border: 2px solid #2a2a2a;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    margin-bottom: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
}

/* Efek Hover saat Kursor di atas Kartu */
.anime-card-container:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 12px 25px rgba(245, 197, 24, 0.4);
    border-color: #f5c518;
}

/* Gambar Poster */
.anime-poster-img {
    width: 100%;
    height: 320px;
    object-fit: cover;
    display: block;
    transition: filter 0.3s ease;
}

.anime-card-container:hover .anime-poster-img {
    filter: brightness(1.1);
}

/* Badge Rating di Pojok Kiri Atas */
.rating-badge {
    position: absolute;
    top: 10px;
    left: 10px;
    background: rgba(0, 0, 0, 0.85);
    color: #f5c518;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: bold;
    border: 1px solid #f5c518;
    backdrop-filter: blur(4px);
    z-index: 10;
}

/* Badge Ranking di Pojok Kanan Atas */
.rank-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    background: #f5c518;
    color: #000;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 800;
    z-index: 10;
}

/* Detail Informasi di Bawah Poster */
.anime-card-info {
    padding: 12px;
    background: linear-gradient(180deg, #181818 0%, #0d0d0d 100%);
    text-align: center;
}

.anime-title-link {
    color: #ffffff;
    font-weight: bold;
    font-size: 1.05rem;
    text-decoration: none;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    height: 2.6em;
    line-height: 1.3em;
}

.anime-title-link:hover {
    color: #f5c518;
}

.anime-meta {
    font-size: 0.85rem;
    color: #999999;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# Fungsi Cerdas Mencari & Konversi Gambar Lokal ke Base64
def get_local_poster(title_keyword):
    if not os.path.exists("assets"):
        os.makedirs("assets")
        
    for file in os.listdir("assets"):
        if title_keyword in file.lower():
            image_path = os.path.join("assets", file)
            if os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    data = f.read()
                encoded = base64.b64encode(data).decode()
                ext = image_path.split('.')[-1].lower()
                mime = "image/png" if ext == "png" else "image/jpeg"
                return f"data:{mime};base64,{encoded}"
    return None

# Memuat & Membersihkan Data (File CSV)
nama_file = "IMBD.csv"

@st.cache_data
def load_data(filepath):
    try:
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()
        
        for col in df.columns:
            col_lower = col.lower()
            if 'year' in col_lower or 'tahun' in col_lower:
                df[col] = pd.to_numeric(df[col].astype(str).str.extract(r'(\d{4})')[0], errors='coerce')
            elif 'rating' in col_lower or 'score' in col_lower or 'vote' in col_lower:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce')
                
        return df
    except FileNotFoundError:
        return None

data = load_data(nama_file)

# Sidebar Navigasi Publik 
with st.sidebar:
    st.image("https://img.icons8.com/color/96/imdb.png", width=80)
    st.title("IMDb Public Hub")
    st.write("Jelajahi informasi film, rating, dan tren data film populer dengan mudah.")
    
    st.divider()
    
    menu = st.radio(
        "Pilih Menu:",
        ["🏠 Beranda & Top Film", "🔍 Cari Detail Film", "📊 Statistik & Grafik Publik", "📥 Unduh Dataset"]
    )
    
    st.divider()
    st.info("💡 **Tips**: Arahkan kursor ke poster film untuk melihat efek hover bersinar emas!")

# Logika Tampilan Berdasarkan Menu
if data is not None:
    
    cols_lower = {c.lower(): c for c in data.columns}
    title_col = next((cols_lower[k] for k in cols_lower if 'title' in k or 'name' in k or 'film' in k), data.columns[0])
    rating_col = next((cols_lower[k] for k in cols_lower if 'rating' in k or 'score' in k), None)
    year_col = next((cols_lower[k] for k in cols_lower if 'year' in k or 'tahun' in k), None)
    genre_col = next((cols_lower[k] for k in cols_lower if 'genre' in k or 'kategori' in k), None)

    # BERANDA & TOP FILM
    if menu == "🏠 Beranda & Top Film":
        st.title("🍿 Portal Informasi & Rekomendasi Film")
        st.write("Selamat datang di platform eksplorasi data film terbuka untuk publik.")
        
        # Metrik Ringkas (KPI Cards)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Judul Film", value=f"{len(data):,} Film")
            
        with col2:
            if rating_col:
                avg_rating = round(data[rating_col].mean(), 2) if not data[rating_col].dropna().empty else 0
                st.metric(label="Rata-rata Rating Global", value=f"⭐ {avg_rating}")
            else:
                st.metric(label="Kolom Rating", value="Tidak tersedia")
                
        with col3:
            if year_col:
                years_numeric = data[year_col].dropna()
                if not years_numeric.empty:
                    tahun_min = int(years_numeric.min())
                    tahun_max = int(years_numeric.max())
                    st.metric(label="Rentang Tahun", value=f"{tahun_min} - {tahun_max}")
                else:
                    st.metric(label="Rentang Tahun", value="Data kosong")
            else:
                st.metric(label="Data Tahun", value="Tidak tersedia")

        st.divider()
        
        st.subheader("🔥 Top 3 Film Unggulan (Rating Tertinggi)")
        st.caption("✨ *Poster dimuat otomatis dari folder lokal 'assets'. Klik poster/judul untuk membuka detail di IMDb.*")
        
        if rating_col:
            clean_top_data = data.drop_duplicates(subset=[title_col])
            top_3_movies = clean_top_data.sort_values(by=rating_col, ascending=False).head(3)
            
            cols = st.columns(3)
            for idx, (_, row) in enumerate(top_3_movies.iterrows()):
                movie_title = str(row[title_col])
                movie_rating = row[rating_col] if rating_col and pd.notna(row[rating_col]) else "N/A"
                movie_year = int(row[year_col]) if year_col and pd.notna(row[year_col]) else "N/A"
                
                title_lower = movie_title.lower()
                if "bojack" in title_lower:
                    keyword = "bojack"
                elif "avatar" in title_lower:
                    keyword = "avatar"
                elif "1899" in title_lower:
                    keyword = "1899"
                else:
                    keyword = title_lower.split()[0]
                
                poster_src = get_local_poster(keyword)
                if not poster_src:
                    poster_src = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&q=80"
                
                search_url = f"https://www.imdb.com/find?q={movie_title.replace(' ', '+')}"
                
                with cols[idx]:
                    st.markdown(f"""
                        <div class="anime-card-container">
                            <div class="rating-badge">⭐ {movie_rating}</div>
                            <div class="rank-badge">#{idx+1} TOP</div>
                            <a href="{search_url}" target="_blank">
                                <img src="{poster_src}" class="anime-poster-img" alt="{movie_title}">
                            </a>
                            <div class="anime-card-info">
                                <a href="{search_url}" target="_blank" class="anime-title-link" title="{movie_title}">{movie_title}</a>
                                <div class="anime-meta">📅 {movie_year}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Kolom rating tidak ditemukan untuk menampilkan top film.")

        st.divider()
        
        # PRATINJAU DATA TERBARU (DIPERBAIKI DARI KATA 'NONE') 
        st.subheader("📋 Pratinjau 10 Film Teratas (Top Rated)")
        st.write("Tabel di bawah ini menampilkan 10 film teratas berdasarkan urutan rating tertinggi pada dataset.")
        
        if rating_col:
            top_10_data = data.drop_duplicates(subset=[title_col]).sort_values(by=rating_col, ascending=False).reset_index(drop=True).head(10).copy()
        else:
            top_10_data = data.head(10).copy()
            
        # Membersihkan nilai kosong/None/NaN menjadi tanda garis "-" agar rapi dipandang
        top_10_data = top_10_data.fillna("-")
            
        kolom_pilihan = [c for c in ['title', 'year', 'certificate', 'duration', 'genre', 'rating', 'description'] if c in top_10_data.columns]
        if not kolom_pilihan:
            kolom_pilihan = top_10_data.columns.tolist()
            
        st.dataframe(
            top_10_data[kolom_pilihan],
            use_container_width=True,
            column_config={
                "title": st.column_config.TextColumn("Judul Film", width="medium"),
                "year": st.column_config.NumberColumn("Tahun", format="%d", width="small"),
                "certificate": st.column_config.TextColumn("Rating Umur", width="small"),
                "duration": st.column_config.TextColumn("Durasi", width="small"),
                "genre": st.column_config.TextColumn("Genre", width="medium"),
                "rating": st.column_config.NumberColumn("Score", format="⭐ %.1f", width="small"),
                "description": st.column_config.TextColumn("Deskripsi Singkat", width="large"),
            },
            hide_index=True
        )

    # CARI DETAIL FILM 
    elif menu == "🔍 Cari Detail Film":
        st.title("🔍 Pencarian Film Interaktif")
        st.write("Ketik judul film yang ingin Anda cari untuk melihat informasi lengkap dan tautan webnya.")
        
        search_query = st.text_input("Masukkan Judul Film / Kata Kunci:", placeholder="Contoh: Batman, Inception, dll...")
        
        if search_query:
            result_df = data[data[title_col].astype(str).str.contains(search_query, case=False, na=False)]
            
            st.success(f"Ditemukan **{len(result_df)}** film yang cocok dengan kata kunci '{search_query}'.")
            
            if not result_df.empty:
                for _, row in result_df.iterrows():
                    movie_title = str(row[title_col])
                    search_url = f"https://www.imdb.com/find?q={movie_title.replace(' ', '+')}"
                    
                    with st.container(border=True):
                        col_info, col_btn = st.columns([3, 1])
                        with col_info:
                            st.subheader(f"🎬 {movie_title}")
                            c1, c2, c3 = st.columns(3)
                            if rating_col and pd.notna(row[rating_col]):
                                c1.metric("Rating", f"⭐ {row[rating_col]}")
                            if year_col and pd.notna(row[year_col]):
                                c2.metric("Tahun Rilis", int(row[year_col]))
                            if genre_col:
                                c3.metric("Genre", str(row[genre_col]))
                        with col_btn:
                            st.write("")
                            st.write("")
                            st.link_button("🌐 Buka di IMDb", search_url, use_container_width=True)
            else:
                st.info("Maaf, film yang Anda cari tidak ditemukan dalam database.")

    # STATISTIK & GRAFIK PUBLIK
    elif menu == "📊 Statistik & Grafik Publik":
        st.title("📊 Statistik & Tren Perfilman")
        st.write("Visualisasi data yang merangkum tren film secara keseluruhan untuk publik.")
        
        kolom_numerik = data.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(kolom_numerik) >= 1:
            col_x, col_y = st.columns(2)
            with col_x:
                x_axis = st.selectbox("Pilih Sumbu X (Kategori / Tahun):", data.columns.tolist())
            with col_y:
                y_axis = st.selectbox("Pilih Sumbu Y (Nilai Numerik):", kolom_numerik)
                
            if x_axis and y_axis:
                chart_data = data[[x_axis, y_axis]].dropna().set_index(x_axis)
                st.line_chart(chart_data)
        else:
            st.warning("Kolom numerik tidak mencukupi untuk membuat grafik tren.")

    # UNDUH DATASET 
    elif menu == "📥 Unduh Dataset":
        st.title("📥 Unduh Dataset IMDb")
        st.write("Publik dapat mengunduh salinan data ini untuk keperluan riset pribadi atau edukasi.")
        
        csv_bytes = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download File CSV Lengkap",
            data=csv_bytes,
            file_name="imdb_public_dataset.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    st.error(f"File **{nama_file}** tidak ditemukan! Test pastikan file CSV sudah diletakkan di dalam folder yang sama dengan `app.py`.")