import streamlit as st
import docx
import base64
import tempfile
from pathlib import Path

# Cấu hình trang
st.set_page_config(
    page_title="Học Tập Y Khoa",
    page_icon="🏥",
    layout="wide"
)

# CSS tùy chỉnh
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2c3e50;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .tab-content {
        padding: 25px;
        background: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    .audio-player {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .document-viewer {
        background: white;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        max-height: 500px;
        overflow-y: auto;
        line-height: 1.8;
        font-size: 16px;
    }
    .highlight {
        background-color: #fffacd;
        padding: 2px 5px;
        border-radius: 3px;
        transition: background-color 0.3s;
    }
    .file-upload {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 2px dashed #ddd;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 25px;
        background: #f0f2f6;
        border-radius: 5px 5px 0 0;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🎧 Hệ Thống Học Tập Y Khoa - Nghe và Đọc</h1>', unsafe_allow_html=True)

# Hàm đọc file Word
def read_docx(file):
    doc = docx.Document(file)
    full_text = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            full_text.append(paragraph.text)
    return "\n\n".join(full_text)

# Hàm hiển thị audio player
def display_audio_player(audio_bytes, file_type):
    if audio_bytes:
        # Tạo file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type}') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        # Hiển thị audio player
        st.markdown('<div class="audio-player">', unsafe_allow_html=True)
        st.markdown("### 🎵 Trình Phát Âm Thanh")
        st.audio(tmp_file_path, format=f'audio/{file_type}')
        
        # Hiển thị thông tin file
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Định dạng", file_type.upper())
        with col2:
            size_mb = len(audio_bytes) / (1024 * 1024)
            st.metric("Kích thước", f"{size_mb:.2f} MB")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return tmp_file_path
    return None

# Tạo tabs
tab1, tab2 = st.tabs(["🔬 **HUYẾT HỌC**", "🧪 **HÓA SINH**"])

with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2c3e50;'>📁 Tải Lên Tài Liệu Huyết Học</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="file-upload">', unsafe_allow_html=True)
        st.markdown("### 📄 File Word (.docx)")
        huyet_hoc_word = st.file_uploader(
            "Chọn file Word cho Huyết học", 
            type=['docx'], 
            key="huyethoc_word"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="file-upload">', unsafe_allow_html=True)
        st.markdown("### 🎵 File Âm Thanh")
        huyet_hoc_audio = st.file_uploader(
            "Chọn file âm thanh cho Huyết học", 
            type=['mp3', 'wav', 'ogg', 'm4a'], 
            key="huyethoc_audio"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Xử lý file Huyết học
    if huyet_hoc_audio:
        audio_bytes = huyet_hoc_audio.read()
        file_type = huyet_hoc_audio.name.split('.')[-1]
        audio_file_path = display_audio_player(audio_bytes, file_type)
    
    if huyet_hoc_word:
        st.markdown('<div class="document-viewer">', unsafe_allow_html=True)
        st.markdown("### 📖 Nội Dung Tài Liệu")
        
        # Đọc và hiển thị nội dung Word
        text_content = read_docx(huyet_hoc_word)
        
        # Tìm kiếm và highlight
        search_term = st.text_input("🔍 Tìm kiếm trong văn bản (Huyết học):", key="search_huyethoc")
        
        if search_term:
            highlighted_text = text_content.replace(
                search_term, 
                f'<span class="highlight">{search_term}</span>'
            )
            st.markdown(highlighted_text, unsafe_allow_html=True)
        else:
            st.markdown(text_content, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if not huyet_hoc_word and not huyet_hoc_audio:
        st.info("👈 Vui lòng tải lên file Word và file âm thanh để bắt đầu học tập")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2c3e50;'>📁 Tải Lên Tài Liệu Hóa Sinh</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="file-upload">', unsafe_allow_html=True)
        st.markdown("### 📄 File Word (.docx)")
        hoa_sinh_word = st.file_uploader(
            "Chọn file Word cho Hóa sinh", 
            type=['docx'], 
            key="hoasinh_word"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="file-upload">', unsafe_allow_html=True)
        st.markdown("### 🎵 File Âm Thanh")
        hoa_sinh_audio = st.file_uploader(
            "Chọn file âm thanh cho Hóa sinh", 
            type=['mp3', 'wav', 'ogg', 'm4a'], 
            key="hoasinh_audio"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Xử lý file Hóa sinh
    if hoa_sinh_audio:
        audio_bytes = hoa_sinh_audio.read()
        file_type = hoa_sinh_audio.name.split('.')[-1]
        audio_file_path = display_audio_player(audio_bytes, file_type)
    
    if hoa_sinh_word:
        st.markdown('<div class="document-viewer">', unsafe_allow_html=True)
        st.markdown("### 📖 Nội Dung Tài Liệu")
        
        # Đọc và hiển thị nội dung Word
        text_content = read_docx(hoa_sinh_word)
        
        # Tìm kiếm và highlight
        search_term = st.text_input("🔍 Tìm kiếm trong văn bản (Hóa sinh):", key="search_hoasinh")
        
        if search_term:
            highlighted_text = text_content.replace(
                search_term, 
                f'<span class="highlight">{search_term}</span>'
            )
            st.markdown(highlighted_text, unsafe_allow_html=True)
        else:
            st.markdown(text_content, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if not hoa_sinh_word and not hoa_sinh_audio:
        st.info("👈 Vui lòng tải lên file Word và file âm thanh để bắt đầu học tập")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Hướng dẫn sử dụng
with st.expander("📘 **Hướng Dẫn Sử Dụng**"):
    st.markdown("""
    ### Cách sử dụng:
    1. **Chọn tab** Huyết học hoặc Hóa sinh
    2. **Tải lên file**:
       - File Word (.docx) chứa nội dung cần đọc
       - File âm thanh (MP3, WAV, OGG, M4A) để nghe
    3. **Học tập**:
       - Bấm play để nghe âm thanh
       - Đọc theo nội dung trong file Word
       - Sử dụng tính năng tìm kiếm để nhanh chóng tìm từ khóa
    4. **Chức năng**:
       - Phát/tạm dừng âm thanh
       - Điều chỉnh âm lượng
       - Tìm kiếm trong văn bản
       - Highlight từ khóa tìm kiếm
    
    ### Định dạng hỗ trợ:
    - **Word**: .docx
    - **Âm thanh**: .mp3, .wav, .ogg, .m4a
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Ứng dụng học tập y khoa - Kết hợp nghe và đọc • "
    "Thiết kế cho sinh viên y khoa"
    "</div>", 
    unsafe_allow_html=True
)
