import streamlit as st
import docx
from docx import Document
import tempfile
import io
import zipfile
import xml.etree.ElementTree as ET
import re
import time
from datetime import datetime
import base64

# Cấu hình trang
st.set_page_config(
    page_title="Học Tập Y Khoa - Nghe và Đọc",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh với highlight động
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: white;
        padding: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .tab-content {
        padding: 30px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-top: 20px;
        border: 1px solid #e0e0e0;
    }
    .audio-player-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border: 1px solid #d0d7e7;
    }
    .document-viewer {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        max-height: 600px;
        overflow-y: auto;
        line-height: 1.8;
        font-size: 16px;
        font-family: 'Arial', sans-serif;
        border: 1px solid #e8e8e8;
    }
    .highlight-playing {
        background-color: #FFFF00 !important;
        color: #000 !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        box-shadow: 0 0 10px rgba(255,255,0,0.5) !important;
        transition: all 0.3s ease !important;
        animation: pulse 2s infinite !important;
        border-left: 4px solid #FF5722 !important;
        margin: 5px 0 !important;
        font-weight: 600 !important;
    }
    .highlight-past {
        background-color: #4CAF50 !important;
        color: white !important;
        padding: 4px 8px !important;
        border-radius: 4px !important;
        opacity: 0.8 !important;
    }
    .highlight-future {
        background-color: #E3F2FD !important;
        color: #1565C0 !important;
        padding: 4px 8px !important;
        border-radius: 4px !important;
    }
    .word-paragraph {
        margin: 12px 0 !important;
        padding: 10px !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }
    .word-paragraph:hover {
        background-color: #f5f5f5 !important;
        transform: translateX(5px) !important;
    }
    .file-upload-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        border-radius: 12px;
        border: 2px dashed #6c757d;
        margin-bottom: 25px;
    }
    .status-bar {
        background: #2196F3;
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        margin: 10px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .timestamp {
        background: #FF9800;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 14px;
        margin-left: 10px;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 87, 34, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 87, 34, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 87, 34, 0); }
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        padding: 0 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 0 30px;
        background: linear-gradient(135deg, #f0f2f6 0%, #e4e8ef 100%);
        border-radius: 10px 10px 0 0;
        font-weight: 700;
        font-size: 16px;
        border: 1px solid #d1d9e6;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #e3e6ec 0%, #d7dbe6 100%);
        transform: translateY(-2px);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-bottom: 3px solid #FF5722 !important;
    }
    .control-panel {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo session state
if 'current_position' not in st.session_state:
    st.session_state.current_position = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'playback_rate' not in st.session_state:
    st.session_state.playback_rate = 1.0
if 'audio_duration' not in st.session_state:
    st.session_state.audio_duration = 0
if 'paragraph_timestamps' not in st.session_state:
    st.session_state.paragraph_timestamps = []
if 'current_audio' not in st.session_state:
    st.session_state.current_audio = None

# Header
st.markdown('''
<div class="main-header">
    <h1>🎧 HỆ THỐNG HỌC TẬP Y KHOA</h1>
    <h3>Nghe Âm Thanh & Đọc Tài Liệu Đồng Bộ</h3>
</div>
''', unsafe_allow_html=True)

# Hàm đọc file Word với định dạng
def read_docx_with_formatting(file):
    """Đọc file Word và trả về các đoạn văn bản với định dạng"""
    try:
        doc = Document(file)
        paragraphs = []
        
        for i, para in enumerate(doc.paragraphs):
            if para.text.strip():  # Chỉ lấy đoạn có nội dung
                # Lấy thông tin định dạng
                text = para.text
                style = para.style.name if para.style else 'Normal'
                
                # Kiểm tra định dạng
                runs_info = []
                for run in para.runs:
                    run_text = run.text
                    if run_text.strip():
                        font_info = {
                            'text': run_text,
                            'bold': run.bold,
                            'italic': run.italic,
                            'underline': run.underline,
                            'size': run.font.size.pt if run.font.size else None,
                            'color': run.font.color.rgb if run.font.color and run.font.color.rgb else None
                        }
                        runs_info.append(font_info)
                
                paragraphs.append({
                    'id': i,
                    'text': text,
                    'style': style,
                    'runs': runs_info,
                    'length': len(text)
                })
        
        return paragraphs
    except Exception as e:
        st.error(f"Lỗi đọc file Word: {str(e)}")
        return []

# Hàm hiển thị văn bản với highlight
def display_text_with_highlight(paragraphs, current_paragraph_idx):
    """Hiển thị văn bản với highlight cho đoạn đang phát"""
    html_content = '<div class="document-viewer">'
    
    for idx, para in enumerate(paragraphs):
        # Xác định class highlight
        if idx == current_paragraph_idx:
            highlight_class = "highlight-playing"
        elif idx < current_paragraph_idx:
            highlight_class = "highlight-past"
        else:
            highlight_class = "highlight-future"
        
        # Xây dựng nội dung đoạn với định dạng
        para_html = f'<div class="word-paragraph {highlight_class}" id="para-{idx}">'
        
        if para.get('runs'):
            for run in para['runs']:
                # Áp dụng định dạng
                style_parts = []
                if run.get('bold'):
                    style_parts.append('font-weight: bold;')
                if run.get('italic'):
                    style_parts.append('font-style: italic;')
                if run.get('underline'):
                    style_parts.append('text-decoration: underline;')
                if run.get('color'):
                    color = f"#{run['color']:06x}"
                    style_parts.append(f'color: {color};')
                if run.get('size'):
                    style_parts.append(f'font-size: {run["size"]}pt;')
                
                style_str = ' '.join(style_parts)
                if style_str:
                    para_html += f'<span style="{style_str}">{run["text"]}</span>'
                else:
                    para_html += run['text']
        else:
            para_html += para['text']
        
        # Thêm số thứ tự đoạn
        para_html += f'<span class="timestamp">Đoạn {idx+1}</span>'
        para_html += '</div>'
        
        html_content += para_html
    
    html_content += '</div>'
    
    return html_content

# Hàm tạo timeline cho các đoạn
def create_paragraph_timeline(paragraphs, audio_duration):
    """Tạo timeline phân bố thời gian cho các đoạn"""
    if not paragraphs:
        return []
    
    total_chars = sum(p['length'] for p in paragraphs)
    timeline = []
    current_time = 0
    
    for para in paragraphs:
        # Tính thời gian dựa trên độ dài đoạn
        para_duration = (para['length'] / total_chars) * audio_duration
        timeline.append({
            'start': current_time,
            'end': current_time + para_duration,
            'para_id': para['id']
        })
        current_time += para_duration
    
    return timeline

# Hàm tìm đoạn đang phát
def find_current_paragraph(timeline, current_time):
    """Tìm đoạn văn bản tương ứng với thời gian hiện tại"""
    if not timeline:
        return 0
    
    for i, segment in enumerate(timeline):
        if segment['start'] <= current_time <= segment['end']:
            return i
    
    # Nếu không tìm thấy, trả về đoạn cuối cùng
    return len(timeline) - 1

# Sidebar với điều khiển
with st.sidebar:
    st.markdown("### ⚙️ ĐIỀU KHIỂN")
    
    # Tốc độ phát
    playback_rate = st.slider(
        "Tốc độ phát",
        min_value=0.5,
        max_value=2.0,
        value=st.session_state.playback_rate,
        step=0.25
    )
    st.session_state.playback_rate = playback_rate
    
    # Auto-scroll
    auto_scroll = st.checkbox("Tự động cuộn theo đoạn đang phát", value=True)
    
    # Hiển thị trạng thái
    st.markdown("---")
    st.markdown("### 📊 TRẠNG THÁI")
    
    if st.session_state.current_audio:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Đoạn hiện tại", f"{st.session_state.current_position + 1}")
        with col2:
            st.metric("Tốc độ", f"{playback_rate}x")
    
    # Hướng dẫn
    with st.expander("📖 HƯỚNG DẪN SỬ DỤNG"):
        st.markdown("""
        1. **Tải lên** file Word (.docx) và file âm thanh
        2. **Nhấn play** để bắt đầu nghe
        3. **Văn bản sẽ tự động highlight** theo đoạn đang phát
        4. **Điều chỉnh tốc độ** trong sidebar
        5. **Nhấn vào đoạn văn bản** để phát từ đoạn đó
        
        **Định dạng hỗ trợ:**
        - Word: .docx (giữ nguyên định dạng)
        - Âm thanh: .mp3, .wav, .ogg, .m4a
        """)

# Tạo tabs
tab1, tab2 = st.tabs(["🔬 **HUYẾT HỌC**", "🧪 **HÓA SINH**"])

with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2c3e50;'>📚 HUYẾT HỌC</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="file-upload-section">', unsafe_allow_html=True)
        st.markdown("### 📄 Tải file Word")
        huyet_hoc_word = st.file_uploader(
            "Chọn file Word (.docx)", 
            type=['docx'], 
            key="huyethoc_word",
            help="File Word chứa nội dung bài học"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="file-upload-section">', unsafe_allow_html=True)
        st.markdown("### 🎵 Tải file Âm thanh")
        huyet_hoc_audio = st.file_uploader(
            "Chọn file âm thanh", 
            type=['mp3', 'wav', 'ogg', 'm4a', 'flac'], 
            key="huyethoc_audio",
            help="File âm thanh bài giảng"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Xử lý khi có file
    if huyet_hoc_audio and huyet_hoc_word:
        # Lưu audio vào session state
        st.session_state.current_audio = huyet_hoc_audio
        
        # Đọc file Word
        paragraphs = read_docx_with_formatting(huyet_hoc_word)
        
        # Hiển thị audio player
        st.markdown('<div class="audio-player-container">', unsafe_allow_html=True)
        st.markdown("### 🎵 TRÌNH PHÁT ÂM THANH")
        
        # Hiển thị audio player
        audio_bytes = huyet_hoc_audio.read()
        audio_type = huyet_hoc_audio.type.split('/')[-1]
        
        # Tạo file tạm cho audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_type}') as tmp_audio:
            tmp_audio.write(audio_bytes)
            tmp_audio_path = tmp_audio.name
        
        # Hiển thị audio player
        audio_html = f"""
        <audio id="huyethoc-audio" controls style="width: 100%;">
            <source src="data:audio/{audio_type};base64,{base64.b64encode(audio_bytes).decode()}" type="audio/{audio_type}">
            Trình duyệt không hỗ trợ phát âm thanh
        </audio>
        <script>
            var audio = document.getElementById('huyethoc-audio');
            audio.playbackRate = {playback_rate};
            
            // Gửi thời gian hiện tại về Streamlit
            audio.addEventListener('timeupdate', function() {{
                var currentTime = audio.currentTime;
                var duration = audio.duration;
                
                // Gửi thông qua window
                window.parent.postMessage({{
                    type: 'audio_time_update',
                    currentTime: currentTime,
                    duration: duration,
                    isPlaying: !audio.paused
                }}, '*');
            }});
        </script>
        """
        st.components.v1.html(audio_html, height=100)
        
        # Thông tin file
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("📄 Số đoạn văn", len(paragraphs))
        with col_info2:
            st.metric("⏱️ Thời lượng", f"{st.session_state.audio_duration:.1f}s")
        with col_info3:
            st.metric("🎯 Tốc độ", f"{playback_rate}x")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tạo timeline nếu chưa có
        if not st.session_state.paragraph_timestamps and paragraphs:
            st.session_state.paragraph_timestamps = create_paragraph_timeline(
                paragraphs, 
                st.session_state.audio_duration or 300  # Mặc định 5 phút nếu chưa biết
            )
        
        # Hiển thị văn bản với highlight
        st.markdown("### 📖 NỘI DUNG TÀI LIỆU")
        
        # Hiển thị văn bản
        html_content = display_text_with_highlight(paragraphs, st.session_state.current_position)
        st.markdown(html_content, unsafe_allow_html=True)
        
        # Điều khiển điều hướng
        st.markdown('<div class="control-panel">', unsafe_allow_html=True)
        st.markdown("##### 🎮 Điều khiển phát")
        
        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
        with col_nav1:
            if st.button("⏮️ Đoạn trước", key="prev_huyet"):
                if st.session_state.current_position > 0:
                    st.session_state.current_position -= 1
        with col_nav2:
            if st.button("⏭️ Đoạn sau", key="next_huyet"):
                if st.session_state.current_position < len(paragraphs) - 1:
                    st.session_state.current_position += 1
        with col_nav3:
            if st.button("🔁 Phát lại đoạn", key="repeat_huyet"):
                # Có thể thêm logic phát lại đoạn hiện tại
                pass
        with col_nav4:
            if st.button("📝 Ghi chú", key="note_huyet"):
                note = st.text_area("Ghi chú cho đoạn hiện tại:")
                if note:
                    st.success("Đã lưu ghi chú!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    elif huyet_hoc_audio or huyet_hoc_word:
        st.warning("⚠️ Vui lòng tải lên cả file Word và file âm thanh để sử dụng đầy đủ tính năng")
    else:
        st.info("👈 Vui lòng tải lên file Word và file âm thanh để bắt đầu học tập Huyết học")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2c3e50;'>🧬 HÓA SINH</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="file-upload-section">', unsafe_allow_html=True)
        st.markdown("### 📄 Tải file Word")
        hoa_sinh_word = st.file_uploader(
            "Chọn file Word (.docx)", 
            type=['docx'], 
            key="hoasinh_word",
            help="File Word chứa nội dung bài học"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="file-upload-section">', unsafe_allow_html=True)
        st.markdown("### 🎵 Tải file Âm thanh")
        hoa_sinh_audio = st.file_uploader(
            "Chọn file âm thanh", 
            type=['mp3', 'wav', 'ogg', 'm4a', 'flac'], 
            key="hoasinh_audio",
            help="File âm thanh bài giảng"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Xử lý khi có file
    if hoa_sinh_audio and hoa_sinh_word:
        # Lưu audio vào session state
        st.session_state.current_audio = hoa_sinh_audio
        
        # Đọc file Word
        paragraphs = read_docx_with_formatting(hoa_sinh_word)
        
        # Hiển thị audio player
        st.markdown('<div class="audio-player-container">', unsafe_allow_html=True)
        st.markdown("### 🎵 TRÌNH PHÁT ÂM THANH")
        
        # Hiển thị audio player
        audio_bytes = hoa_sinh_audio.read()
        audio_type = hoa_sinh_audio.type.split('/')[-1]
        
        # Tạo audio player
        audio_html = f"""
        <audio id="hoasinh-audio" controls style="width: 100%;">
            <source src="data:audio/{audio_type};base64,{base64.b64encode(audio_bytes).decode()}" type="audio/{audio_type}">
            Trình duyệt không hỗ trợ phát âm thanh
        </audio>
        <script>
            var audio = document.getElementById('hoasinh-audio');
            audio.playbackRate = {playback_rate};
            
            // Gửi thời gian hiện tại về Streamlit
            audio.addEventListener('timeupdate', function() {{
                var currentTime = audio.currentTime;
                var duration = audio.duration;
                
                // Gửi thông qua window
                window.parent.postMessage({{
                    type: 'audio_time_update',
                    currentTime: currentTime,
                    duration: duration,
                    isPlaying: !audio.paused
                }}, '*');
            }});
        </script>
        """
        st.components.v1.html(audio_html, height=100)
        
        # Thông tin file
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("📄 Số đoạn văn", len(paragraphs))
        with col_info2:
            st.metric("⏱️ Thời lượng", f"{st.session_state.audio_duration:.1f}s")
        with col_info3:
            st.metric("🎯 Tốc độ", f"{playback_rate}x")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Hiển thị văn bản với highlight
        st.markdown("### 📖 NỘI DUNG TÀI LIỆU")
        
        # Hiển thị văn bản
        html_content = display_text_with_highlight(paragraphs, st.session_state.current_position)
        st.markdown(html_content, unsafe_allow_html=True)
        
        # Điều khiển điều hướng
        st.markdown('<div class="control-panel">', unsafe_allow_html=True)
        st.markdown("##### 🎮 Điều khiển phát")
        
        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
        with col_nav1:
            if st.button("⏮️ Đoạn trước", key="prev_hoasinh"):
                if st.session_state.current_position > 0:
                    st.session_state.current_position -= 1
        with col_nav2:
            if st.button("⏭️ Đoạn sau", key="next_hoasinh"):
                if st.session_state.current_position < len(paragraphs) - 1:
                    st.session_state.current_position += 1
        with col_nav3:
            if st.button("🔁 Phát lại đoạn", key="repeat_hoasinh"):
                # Có thể thêm logic phát lại đoạn hiện tại
                pass
        with col_nav4:
            if st.button("📝 Ghi chú", key="note_hoasinh"):
                note = st.text_area("Ghi chú cho đoạn hiện tại:", key="note_area_hoasinh")
                if note:
                    st.success("Đã lưu ghi chú!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    elif hoa_sinh_audio or hoa_sinh_word:
        st.warning("⚠️ Vui lòng tải lên cả file Word và file âm thanh để sử dụng đầy đủ tính năng")
    else:
        st.info("👈 Vui lòng tải lên file Word và file âm thanh để bắt đầu học tập Hóa sinh")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🎓 Ứng dụng học tập y khoa - Kết hợp nghe và đọc đồng bộ</p>
        <p>📚 Thiết kế cho sinh viên y khoa • Phiên bản 2.0</p>
        <p style='font-size: 12px; margin-top: 10px;'>
            Tính năng: Highlight theo đoạn • Giữ nguyên định dạng Word • Đồng bộ âm thanh-văn bản
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)

# JavaScript để xử lý đồng bộ
js_code = """
<script>
// Lắng nghe sự kiện từ audio player
window.addEventListener('message', function(event) {
    if (event.data.type === 'audio_time_update') {
        // Cập nhật thời gian hiện tại
        console.log('Audio time:', event.data.currentTime);
        
        // Có thể gửi AJAX request để cập nhật session state
        // Hoặc sử dụng WebSocket cho real-time
    }
});

// Cuộn đến đoạn đang phát
function scrollToParagraph(paraId) {
    const element = document.getElementById('para-' + paraId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Thêm sự kiện click cho các đoạn văn
document.addEventListener('DOMContentLoaded', function() {
    const paragraphs = document.querySelectorAll('.word-paragraph');
    paragraphs.forEach(function(para, index) {
        para.addEventListener('click', function() {
            // Gửi thông tin về Streamlit khi click vào đoạn
            window.parent.postMessage({
                type: 'paragraph_click',
                paragraphIndex: index
            }, '*');
        });
    });
});
</script>
"""

st.components.v1.html(js_code, height=0)