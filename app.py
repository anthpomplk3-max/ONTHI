import streamlit as st
import os
import time
import base64
from pydub import AudioSegment
import io
import tempfile

# Hàm để định dạng thời gian
def format_time(seconds):
    if seconds < 0:
        seconds = 0
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

# Hàm để lấy độ dài audio từ file MP3
def get_audio_length(audio_file):
    try:
        audio = AudioSegment.from_file(audio_file, format="mp3")
        return len(audio) / 1000.0  # Chuyển từ mili giây sang giây
    except:
        # Ước tính nếu không đọc được (30 giây mỗi dòng văn bản)
        return 30 * len(st.session_state.get('text_lines', []))

# Hàm tạo HTML audio player
def audio_player_with_controls(audio_bytes, start_time=0):
    b64 = base64.b64encode(audio_bytes).decode()
    
    # Tạo HTML với JavaScript để điều khiển
    html = f"""
    <audio id="myAudio" controls style="width:100%">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    
    <script>
    const audio = document.getElementById('myAudio');
    
    // Đặt thời gian bắt đầu
    audio.currentTime = {start_time};
    
    // Lưu trạng thái phát
    audio.addEventListener('play', function() {{
        window.parent.postMessage({{type: 'audio', event: 'play', currentTime: audio.currentTime}}, '*');
    }});
    
    audio.addEventListener('pause', function() {{
        window.parent.postMessage({{type: 'audio', event: 'pause', currentTime: audio.currentTime}}, '*');
    }});
    
    audio.addEventListener('timeupdate', function() {{
        window.parent.postMessage({{type: 'audio', event: 'timeupdate', currentTime: audio.currentTime}}, '*');
    }});
    </script>
    """
    return html

# Hàm tải file âm thanh dưới dạng bytes
def load_audio_bytes(audio_file):
    try:
        with open(audio_file, 'rb') as f:
            return f.read()
    except:
        return None

# Danh sách các file có sẵn
def get_available_files():
    available = {}
    # Kiểm tra các file trong thư mục hiện tại
    files_in_dir = os.listdir('.')
    
    for num in [58, 72, 83, 85]:
        mp3_file = f"QT {num}.mp3"
        txt_file = f"QT {num}.txt"
        
        # Kiểm tra xem file có tồn tại không
        if mp3_file in files_in_dir and txt_file in files_in_dir:
            available[num] = {'mp3': mp3_file, 'txt': txt_file}
        else:
            # Thử tìm với pattern khác
            for f in files_in_dir:
                if f"QT {num}" in f and f.endswith('.mp3'):
                    mp3_file = f
                if f"QT {num}" in f and f.endswith('.txt'):
                    txt_file = f
            
            if os.path.exists(mp3_file) and os.path.exists(txt_file):
                available[num] = {'mp3': mp3_file, 'txt': txt_file}
    
    return available

# Đọc nội dung file văn bản
def load_text_content(txt_file):
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return [line.strip() for line in lines if line.strip()]
    except:
        try:
            with open(txt_file, 'r', encoding='latin-1') as f:
                lines = f.readlines()
            return [line.strip() for line in lines if line.strip()]
        except Exception as e:
            return [f"Lỗi đọc file: {str(e)}"]

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="QT Audio Player",
    page_icon="🎵",
    layout="wide"
)

# Tiêu đề
st.title("🎵 QT Audio Player")

# Khởi tạo session state
if 'current_audio' not in st.session_state:
    st.session_state.current_audio = None
if 'current_text_file' not in st.session_state:
    st.session_state.current_text_file = None
if 'text_lines' not in st.session_state:
    st.session_state.text_lines = []
if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = None
if 'current_position' not in st.session_state:
    st.session_state.current_position = 0
if 'audio_length' not in st.session_state:
    st.session_state.audio_length = 0
if 'highlight_index' not in st.session_state:
    st.session_state.highlight_index = -1
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

# Tạo file requirements.txt tự động
requirements_content = """streamlit>=1.28.0
pydub>=0.25.1
"""

# Sidebar để chọn file và điều khiển
with st.sidebar:
    st.header("📂 Chọn File")
    
    # Hiển thị file requirements
    with st.expander("📋 Requirements"):
        st.code(requirements_content, language="txt")
        if st.button("Copy requirements"):
            st.code("pip install streamlit pydub", language="bash")
    
    # Tải danh sách file
    available_files = get_available_files()
    
    if not available_files:
        st.error("Không tìm thấy file QT nào trong thư mục hiện tại!")
        st.info("Vui lòng đảm bảo các file có tên:")
        st.code("""
        QT 58.mp3, QT 58.txt
        QT 72.mp3, QT 72.txt  
        QT 83.mp3, QT 83.txt
        QT 85.mp3, QT 85.txt
        """)
    else:
        # Nút chọn file
        for num in [58, 72, 83, 85]:
            if num in available_files:
                if st.button(f"QT {num}", key=f"btn_{num}", use_container_width=True):
                    # Tải file mới
                    files = available_files[num]
                    st.session_state.current_audio = files['mp3']
                    st.session_state.current_text_file = files['txt']
                    st.session_state.text_lines = load_text_content(files['txt'])
                    st.session_state.audio_bytes = load_audio_bytes(files['mp3'])
                    st.session_state.audio_length = get_audio_length(files['mp3'])
                    
                    # Reset
                    st.session_state.current_position = 0
                    st.session_state.highlight_index = -1
                    st.session_state.is_playing = False
                    
                    st.success(f"✅ Đã tải QT {num}")
            else:
                st.warning(f"QT {num} - Không có file")

# Main content
if st.session_state.current_audio and st.session_state.audio_bytes:
    st.subheader(f"🎶 Đang chọn: {os.path.basename(st.session_state.current_audio)}")
    
    # Hiển thị thông tin
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Số dòng văn bản", len(st.session_state.text_lines))
    with col2:
        st.metric("Độ dài audio", f"{format_time(st.session_state.audio_length)}")
    
    # Hiển thị audio player với HTML/JavaScript
    st.subheader("🎧 Player")
    
    # Tạo audio player
    audio_html = audio_player_with_controls(
        st.session_state.audio_bytes,
        st.session_state.current_position
    )
    
    # Hiển thị audio player
    components = st.components.v1.html(audio_html, height=100)
    
    # Hiển thị thanh trượt để điều khiển thủ công
    current_time = st.slider(
        "Tiến độ",
        0.0,
        st.session_state.audio_length,
        st.session_state.current_position,
        key="progress_slider",
        format="%.1f giây",
        help="Kéo để thay đổi vị trí phát"
    )
    
    # Nếu người dùng thay đổi thanh trượt
    if current_time != st.session_state.current_position:
        st.session_state.current_position = current_time
        st.rerun()
    
    # Hiển thị văn bản với highlight
    st.subheader("📝 Nội dung")
    
    # Tạo container cho văn bản
    text_container = st.container()
    
    # Tính toán dòng cần highlight dựa trên thời gian hiện tại
    if st.session_state.text_lines:
        time_per_line = st.session_state.audio_length / max(len(st.session_state.text_lines), 1)
        current_line = int(st.session_state.current_position / time_per_line)
        current_line = min(current_line, len(st.session_state.text_lines) - 1)
        current_line = max(current_line, 0)
        
        # Tạo các cột để hiển thị văn bản
        with text_container:
            for i, line in enumerate(st.session_state.text_lines):
                # Tạo một box cho mỗi dòng
                if i == current_line:
                    # Highlight dòng hiện tại
                    st.markdown(
                        f'<div style="background-color: #FFFF99; padding: 15px; border-radius: 8px; '
                        f'margin: 10px 0; border-left: 5px solid #FF9900; font-weight: bold;">'
                        f'{i+1}. {line}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    # Dòng bình thường có thể click
                    line_html = f"""
                    <div style="padding: 10px; margin: 5px 0; cursor: pointer; 
                    border-left: 3px solid #E0E0E0;" 
                    onclick="window.parent.postMessage({{type: 'jump', line: {i}}}, '*')">
                    <b>{i+1}.</b> {line}
                    </div>
                    """
                    st.markdown(line_html, unsafe_allow_html=True)
        
        # Nút điều khiển nhảy đến dòng cụ thể
        st.subheader("🎯 Nhảy đến dòng")
        
        # Tạo các nút cho từng dòng (chia thành nhiều cột)
        cols_per_row = 4
        total_lines = len(st.session_state.text_lines)
        
        for row_start in range(0, total_lines, cols_per_row):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                line_idx = row_start + col_idx
                if line_idx < total_lines:
                    with cols[col_idx]:
                        if st.button(f"Dòng {line_idx + 1}", key=f"jump_btn_{line_idx}"):
                            # Tính thời gian tương ứng với dòng này
                            time_per_line = st.session_state.audio_length / total_lines
                            jump_time = line_idx * time_per_line
                            
                            st.session_state.current_position = jump_time
                            st.session_state.highlight_index = line_idx
                            st.rerun()
    
    # Hiển thị thông tin debug (có thể ẩn đi)
    with st.expander("ℹ️ Thông tin debug"):
        st.write(f"Vị trí hiện tại: {st.session_state.current_position:.2f} giây")
        st.write(f"Độ dài audio: {st.session_state.audio_length:.2f} giây")
        st.write(f"Dòng đang highlight: {current_line + 1}/{len(st.session_state.text_lines)}")
        
else:
    # Hướng dẫn khi chưa có file
    st.info("👈 Vui lòng chọn một file từ sidebar để bắt đầu.")
    
    if available_files:
        st.subheader("📁 File có sẵn:")
        for num, file_info in available_files.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**QT {num}:**")
                st.write(f"  - 🔊 `{file_info['mp3']}`")
                st.write(f"  - 📄 `{file_info['txt']}`")
            with col2:
                if st.button(f"Chọn QT {num}", key=f"select_{num}"):
                    st.session_state.current_audio = file_info['mp3']
                    st.session_state.current_text_file = file_info['txt']
                    st.session_state.text_lines = load_text_content(file_info['txt'])
                    st.session_state.audio_bytes = load_audio_bytes(file_info['mp3'])
                    st.session_state.audio_length = get_audio_length(file_info['mp3'])
                    st.rerun()
    else:
        st.warning("""
        Không tìm thấy file QT trong thư mục hiện tại.
        
        **Để sử dụng ứng dụng này, bạn cần:**
        
        1. **Tải lên các file:** QT 58.mp3, QT 58.txt, QT 72.mp3, QT 72.txt, QT 83.mp3, QT 83.txt, QT 85.mp3, QT 85.txt
        2. **Hoặc** thay đổi code để trỏ đến đúng đường dẫn file của bạn
        3. **Đảm bảo** có file `requirements.txt` với nội dung:
        ```
        streamlit>=1.28.0
        pydub>=0.25.1
        ```
        """)

# Footer
st.markdown("---")
st.caption("🎵 QT Audio Player | Sử dụng Streamlit và HTML5 Audio | Phiên bản không cần pygame")

# Thêm JavaScript để xử lý các sự kiện từ audio player
js_code = """
<script>
// Lắng nghe các message từ iframe (audio player)
window.addEventListener('message', function(event) {
    const data = event.data;
    
    if (data.type === 'audio') {
        if (data.event === 'timeupdate') {
            // Cập nhật vị trí hiện tại
            window.parent.stSessionState.set(
                'current_position', 
                data.currentTime,
                () => console.log('Updated position:', data.currentTime)
            );
        }
    }
    
    if (data.type === 'jump') {
        // Tính toán thời gian để nhảy đến dòng
        const line = data.line;
        // Gửi message để cập nhật session state
        window.parent.postMessage({
            type: 'streamlit',
            method: 'setComponentValue',
            args: ['jump_to_line', line]
        }, '*');
    }
});
</script>
"""

st.components.v1.html(js_code, height=0)
