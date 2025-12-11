import streamlit as st
import os
import time
from pathlib import Path
import base64

# Thiết lập trang Streamlit
st.set_page_config(
    page_title="Audio Player with Text Sync",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4A4A4A;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .track-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #4CAF50;
        transition: all 0.3s;
    }
    .track-card:hover {
        background-color: #e9ecef;
        transform: translateY(-2px);
    }
    .active-track {
        border-left: 5px solid #2196F3;
        background-color: #e3f2fd;
    }
    .audio-controls {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .text-display {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        min-height: 400px;
        max-height: 500px;
        overflow-y: auto;
        font-size: 16px;
        line-height: 1.6;
        white-space: pre-wrap;
        word-wrap: break-word;
        font-family: 'Courier New', monospace;
    }
    .control-button {
        margin: 5px;
    }
    .status-bar {
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Danh sách các file theo thứ tự trong hình
TRACKS = [
    {"audio": "QT 58.mp3", "text": "QT 58.txt"},
    {"audio": "QT 72.mp3", "text": "QT 72.txt"},
    {"audio": "QT 83.mp3", "text": "QT 83.txt"},
    {"audio": "QT 85.mp3", "text": "QT 85.txt"}
]

# Khởi tạo session state
if 'current_track' not in st.session_state:
    st.session_state.current_track = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'volume' not in st.session_state:
    st.session_state.volume = 0.7
if 'playback_speed' not in st.session_state:
    st.session_state.playback_speed = 1.0
if 'player_state' not in st.session_state:
    st.session_state.player_state = "stopped"
if 'track_progress' not in st.session_state:
    st.session_state.track_progress = 0

def load_text_file(filename):
    """Load nội dung file text với multiple encoding fallback"""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1258', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding=encoding) as f:
                    content = f.read()
                return content
        except UnicodeDecodeError:
            continue
        except Exception as e:
            continue
    
    # Nếu không đọc được với các encoding trên, thử đọc binary
    try:
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                content = f.read()
            # Thử decode với utf-8 và thay thế các ký tự lỗi
            return content.decode('utf-8', errors='replace')
    except Exception as e:
        return f"Không thể đọc file: {filename}\nLỗi: {str(e)}\n\nVui lòng kiểm tra:\n1. File có tồn tại không?\n2. File có nội dung không?\n3. Encoding của file là gì?"

def get_audio_data_url(audio_file):
    """Chuyển đổi audio file thành data URL để phát"""
    try:
        if os.path.exists(audio_file):
            with open(audio_file, "rb") as f:
                data = f.read()
                base64_encoded = base64.b64encode(data).decode()
                mime_type = "audio/mpeg" if audio_file.endswith('.mp3') else "audio/wav"
                return f"data:{mime_type};base64,{base64_encoded}"
        return None
    except Exception as e:
        st.error(f"Lỗi khi đọc file audio: {str(e)}")
        return None

def display_audio_player():
    """Hiển thị audio player với controls"""
    current_audio = TRACKS[st.session_state.current_track]["audio"]
    audio_url = get_audio_data_url(current_audio)
    
    if audio_url:
        # HTML audio player với JavaScript controls
        audio_html = f"""
        <div class="audio-controls">
            <audio id="audioPlayer" controls style="width: 100%;" autoplay>
                <source src="{audio_url}" type="audio/mpeg">
                Trình duyệt của bạn không hỗ trợ phát audio.
            </audio>
            
            <div style="margin-top: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span>Âm lượng: {int(st.session_state.volume * 100)}%</span>
                    <span>Tốc độ: {st.session_state.playback_speed}x</span>
                </div>
                
                <div style="display: flex; gap: 10px; align-items: center;">
                    <input type="range" id="volumeSlider" min="0" max="100" 
                           value="{int(st.session_state.volume * 100)}" 
                           style="flex-grow: 1;"
                           oninput="updateVolume(this.value)">
                    
                    <input type="range" id="speedSlider" min="0.5" max="2.0" step="0.1"
                           value="{st.session_state.playback_speed}" 
                           style="flex-grow: 1;"
                           oninput="updateSpeed(this.value)">
                </div>
            </div>
        </div>
        
        <script>
            const audio = document.getElementById('audioPlayer');
            
            // Khởi tạo volume và playbackRate
            audio.volume = {st.session_state.volume};
            audio.playbackRate = {st.session_state.playback_speed};
            
            // Hàm cập nhật volume
            function updateVolume(value) {{
                audio.volume = value / 100;
            }}
            
            // Hàm cập nhật tốc độ
            function updateSpeed(value) {{
                audio.playbackRate = parseFloat(value);
            }}
        </script>
        """
        st.components.v1.html(audio_html, height=150)
    else:
        st.error(f"Không thể tải file audio: {current_audio}")
        st.info(f"Vui lòng đảm bảo file '{current_audio}' tồn tại trong thư mục hiện tại.")

def main():
    st.markdown('<h1 class="main-header">🎵 Audio Player with Text Sync</h1>', unsafe_allow_html=True)
    
    # DEBUG: Hiển thị thông tin thư mục hiện tại
    with st.expander("🔍 Debug Information"):
        st.write("Current directory:", os.getcwd())
        st.write("Files in directory:", os.listdir('.'))
        
        # Kiểm tra từng file
        for track in TRACKS:
            st.write(f"{track['audio']} exists:", os.path.exists(track['audio']))
            st.write(f"{track['text']} exists:", os.path.exists(track['text']))
            if os.path.exists(track['text']):
                st.write(f"{track['text']} size:", os.path.getsize(track['text']), "bytes")
    
    # Sidebar cho danh sách track
    with st.sidebar:
        st.markdown("### 📋 Danh sách Track")
        
        for idx, track in enumerate(TRACKS):
            is_active = idx == st.session_state.current_track
            audio_exists = os.path.exists(track["audio"])
            text_exists = os.path.exists(track["text"])
            
            card_class = "track-card"
            if is_active:
                card_class += " active-track"
            
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Track {idx+1}**")
                if audio_exists:
                    st.markdown(f"✅ {track['audio']}")
                else:
                    st.markdown(f"❌ {track['audio']}")
                
                if text_exists:
                    st.markdown(f"✅ {track['text']}")
                else:
                    st.markdown(f"❌ {track['text']}")
            with col2:
                if st.button("▶️", key=f"select_{idx}", help=f"Chọn track {idx+1}"):
                    st.session_state.current_track = idx
                    st.session_state.player_state = "playing"
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Thông tin hệ thống
        st.markdown("---")
        st.markdown("### ℹ️ Thông tin")
        
        current_track = st.session_state.current_track + 1
        total_tracks = len(TRACKS)
        st.info(f"**Track hiện tại:** {current_track}/{total_tracks}")
        
        # Thống kê file
        audio_count = sum(1 for track in TRACKS if os.path.exists(track["audio"]))
        text_count = sum(1 for track in TRACKS if os.path.exists(track["text"]))
        st.metric("Audio files", f"{audio_count}/{len(TRACKS)}")
        st.metric("Text files", f"{text_count}/{len(TRACKS)}")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎚️ Điều khiển")
        
        # Control buttons
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        
        with col_btn1:
            if st.button("⏮️ Trước", use_container_width=True, disabled=st.session_state.current_track == 0):
                if st.session_state.current_track > 0:
                    st.session_state.current_track -= 1
                    st.session_state.player_state = "stopped"
                    st.rerun()
        
        with col_btn2:
            if st.button("▶️ Phát", use_container_width=True, type="primary"):
                st.session_state.player_state = "playing"
                st.rerun()
        
        with col_btn3:
            if st.button("⏸️ Tạm dừng", use_container_width=True):
                st.session_state.player_state = "paused"
                st.rerun()
        
        with col_btn4:
            if st.button("⏹️ Dừng", use_container_width=True):
                st.session_state.player_state = "stopped"
                st.rerun()
        
        # Next button
        if st.button("⏭️ Tiếp", use_container_width=True, 
                    disabled=st.session_state.current_track == len(TRACKS) - 1):
            if st.session_state.current_track < len(TRACKS) - 1:
                st.session_state.current_track += 1
                st.session_state.player_state = "stopped"
                st.rerun()
        
        # Hiển thị audio player
        st.markdown("### 🔊 Audio Player")
        display_audio_player()
        
        # Thông tin track hiện tại
        current_track_info = TRACKS[st.session_state.current_track]
        st.markdown(f"""
        <div class="status-bar">
            <strong>Track hiện tại:</strong> {current_track}. {current_track_info['audio']}<br>
            <strong>File text:</strong> {current_track_info['text']}<br>
            <strong>Trạng thái:</strong> {st.session_state.player_state} | 
            <strong>Âm lượng:</strong> {int(st.session_state.volume * 100)}% | 
            <strong>Tốc độ:</strong> {st.session_state.playback_speed}x
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📄 Nội dung Text")
        
        # Load và hiển thị nội dung file text
        current_text_file = TRACKS[st.session_state.current_track]["text"]
        
        if os.path.exists(current_text_file):
            # Hiển thị thông tin file
            file_size = os.path.getsize(current_text_file)
            st.caption(f"File: {current_text_file} ({file_size} bytes)")
            
            # Đọc và hiển thị nội dung
            text_content = load_text_file(current_text_file)
            
            if text_content:
                # Hiển thị trong text area với thanh cuộn
                st.markdown(f'<div class="text-display">{text_content}</div>', unsafe_allow_html=True)
                
                # Nút download
                with open(current_text_file, "rb") as f:
                    st.download_button(
                        label="📥 Tải xuống file text",
                        data=f,
                        file_name=current_text_file,
                        mime="text/plain",
                        use_container_width=True
                    )
                
                # Thống kê nội dung
                lines = text_content.split('\n')
                words = text_content.split()
                chars = len(text_content)
                
                st.caption(f"Thống kê: {len(lines)} dòng, {len(words)} từ, {chars} ký tự")
            else:
                st.warning("File text tồn tại nhưng không có nội dung hoặc không thể đọc.")
                
                # Hiển thị raw content
                with open(current_text_file, 'rb') as f:
                    raw_content = f.read()
                st.code(f"Raw content (hex):\n{raw_content.hex()[:200]}...")
        else:
            st.error(f"❌ File text không tồn tại: {current_text_file}")
            
            # Tạo file text mẫu
            st.info("Tạo file text mẫu để test:")
            
            sample_content = f"""Đây là nội dung mẫu cho file {current_text_file}

Bạn có thể chỉnh sửa nội dung này hoặc thay thế bằng nội dung thực tế.

Các tính năng của ứng dụng:
1. Phát audio file tương ứng: {TRACKS[st.session_state.current_track]['audio']}
2. Hiển thị nội dung text đồng bộ
3. Điều chỉnh âm lượng và tốc độ phát
4. Chuyển đổi giữa các track dễ dàng

Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            if st.button("📝 Tạo file text mẫu", key="create_sample"):
                try:
                    with open(current_text_file, 'w', encoding='utf-8') as f:
                        f.write(sample_content)
                    st.success(f"✅ Đã tạo file {current_text_file}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi khi tạo file: {str(e)}")
    
    # Hướng dẫn sử dụng và xử lý sự cố
    with st.expander("ℹ️ Hướng dẫn sử dụng & Xử lý sự cố"):
        st.markdown("""
        ### Các bước sử dụng:
        1. **Chọn track** từ danh sách bên trái
        2. **Điều khiển phát nhạc** bằng các nút: Phát, Tạm dừng, Dừng
        3. **Chuyển track** bằng nút Trước/Tiếp
        4. **Điều chỉnh âm lượng** bằng thanh trượt trong audio player
        5. **Điều chỉnh tốc độ phát** bằng thanh trượt tốc độ
        6. **Xem nội dung text** tương ứng với track hiện tại
        
        ### Nếu không thấy nội dung text:
        1. **Kiểm tra file có tồn tại không** - xem phần Debug Information
        2. **Kiểm tra encoding của file** - thử mở bằng Notepad++ hoặc VS Code
        3. **Tạo file mẫu** bằng nút "Tạo file text mẫu"
        4. **Kiểm tra quyền truy cập** - đảm bảo ứng dụng có quyền đọc file
        
        ### Định dạng file hỗ trợ:
        - **Audio**: MP3, WAV
        - **Text**: UTF-8, UTF-8-SIG, Latin-1, CP1258, ISO-8859-1
        """)

if __name__ == "__main__":
    main()
