import streamlit as st
import os
import time
from pathlib import Path
import base64
import json

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
        cursor: pointer;
    }
    .track-card:hover {
        background-color: #e9ecef;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .active-track {
        border-left: 5px solid #2196F3;
        background-color: #e3f2fd !important;
        box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
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
        border: 2px solid #2196F3;
    }
    .text-highlight {
        background-color: #fffacd;
        padding: 2px 4px;
        border-radius: 3px;
    }
    .control-button {
        margin: 5px;
    }
    .status-bar {
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        border-left: 5px solid #4CAF50;
    }
    .slider-container {
        margin: 15px 0;
        padding: 10px;
        background-color: #f5f5f5;
        border-radius: 8px;
    }
    .slider-value {
        font-weight: bold;
        color: #2196F3;
        font-size: 1.1em;
    }
    .control-group {
        display: flex;
        justify-content: space-between;
        margin: 15px 0;
        gap: 10px;
    }
    .control-btn {
        flex: 1;
        padding: 12px;
        font-size: 1.1em;
    }
    .track-list {
        max-height: 400px;
        overflow-y: auto;
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
if 'volume' not in st.session_state:
    st.session_state.volume = 70  # 0-100
if 'playback_speed' not in st.session_state:
    st.session_state.playback_speed = 1.0
if 'player_state' not in st.session_state:
    st.session_state.player_state = "stopped"
if 'audio_data_urls' not in st.session_state:
    st.session_state.audio_data_urls = {}
if 'last_action' not in st.session_state:
    st.session_state.last_action = None

def load_text_file(filename):
    """Load nội dung file text với multiple encoding fallback"""
    if not os.path.exists(filename):
        return f"File không tồn tại: {filename}"
    
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1258', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                return f.read()
        except:
            continue
    
    try:
        with open(filename, 'rb') as f:
            content = f.read()
        return content.decode('utf-8', errors='replace')
    except Exception as e:
        return f"Lỗi đọc file: {str(e)}"

def get_audio_data_url(audio_file):
    """Chuyển đổi audio file thành data URL để phát"""
    if audio_file in st.session_state.audio_data_urls:
        return st.session_state.audio_data_urls[audio_file]
    
    try:
        if os.path.exists(audio_file):
            with open(audio_file, "rb") as f:
                data = f.read()
                base64_encoded = base64.b64encode(data).decode()
                mime_type = "audio/mpeg" if audio_file.endswith('.mp3') else "audio/wav"
                data_url = f"data:{mime_type};base64,{base64_encoded}"
                st.session_state.audio_data_urls[audio_file] = data_url
                return data_url
        return None
    except Exception as e:
        st.error(f"Lỗi khi đọc file audio: {str(e)}")
        return None

def create_audio_player():
    """Tạo HTML audio player với controls"""
    current_audio = TRACKS[st.session_state.current_track]["audio"]
    audio_url = get_audio_data_url(current_audio)
    
    if not audio_url:
        return f"""
        <div class="audio-controls">
            <div style="color: red; padding: 20px; text-align: center;">
                Không thể tải file audio: {current_audio}
            </div>
        </div>
        """
    
    audio_player_html = f"""
    <div class="audio-controls">
        <audio id="audioPlayer" controls style="width: 100%;">
            <source src="{audio_url}" type="audio/mpeg">
            Trình duyệt của bạn không hỗ trợ phát audio.
        </audio>
        
        <div class="slider-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: bold;">Âm lượng:</span>
                <span id="volumeValue" class="slider-value">{st.session_state.volume}%</span>
            </div>
            <input type="range" id="volumeSlider" min="0" max="100" value="{st.session_state.volume}" 
                   style="width: 100%; height: 10px;" 
                   oninput="document.getElementById('volumeValue').textContent = this.value + '%'; updateStreamlit('volume', this.value);">
        </div>
        
        <div class="slider-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: bold;">Tốc độ phát:</span>
                <span id="speedValue" class="slider-value">{st.session_state.playback_speed:.1f}x</span>
            </div>
            <input type="range" id="speedSlider" min="0.5" max="2.0" step="0.1" value="{st.session_state.playback_speed}" 
                   style="width: 100%; height: 10px;" 
                   oninput="document.getElementById('speedValue').textContent = parseFloat(this.value).toFixed(1) + 'x'; updateStreamlit('speed', this.value);">
        </div>
        
        <div style="display: flex; gap: 10px; margin-top: 15px;">
            <button onclick="playAudio()" style="flex:1; padding:10px; background:#4CAF50; color:white; border:none; border-radius:5px; cursor:pointer;">▶ Phát</button>
            <button onclick="pauseAudio()" style="flex:1; padding:10px; background:#FF9800; color:white; border:none; border-radius:5px; cursor:pointer;">⏸ Tạm dừng</button>
            <button onclick="stopAudio()" style="flex:1; padding:10px; background:#F44336; color:white; border:none; border-radius:5px; cursor:pointer;">⏹ Dừng</button>
        </div>
    </div>
    
    <script>
        const audio = document.getElementById('audioPlayer');
        
        function updateStreamlit(key, value) {{
            // Lưu giá trị vào localStorage để Streamlit có thể đọc
            localStorage.setItem('streamlit_{key}', value);
            
            // Gửi sự kiện đến Streamlit (nếu được hỗ trợ)
            if (window.parent && window.parent.streamlit) {{
                window.parent.streamlit.setComponentValue({{'{key}': value}});
            }}
        }}
        
        function playAudio() {{
            audio.play();
            updateStreamlit('player_state', 'playing');
        }}
        
        function pauseAudio() {{
            audio.pause();
            updateStreamlit('player_state', 'paused');
        }}
        
        function stopAudio() {{
            audio.pause();
            audio.currentTime = 0;
            updateStreamlit('player_state', 'stopped');
        }}
        
        // Khởi tạo giá trị
        audio.volume = {st.session_state.volume / 100};
        audio.playbackRate = {st.session_state.playback_speed};
        
        // Lắng nghe sự kiện
        audio.addEventListener('play', function() {{
            updateStreamlit('player_state', 'playing');
        }});
        
        audio.addEventListener('pause', function() {{
            updateStreamlit('player_state', 'paused');
        }});
        
        audio.addEventListener('ended', function() {{
            updateStreamlit('player_state', 'stopped');
        }});
    </script>
    """
    return audio_player_html

def main():
    st.markdown('<h1 class="main-header">🎵 Audio Player with Text Sync</h1>', unsafe_allow_html=True)
    
    # Kiểm tra file tồn tại
    with st.sidebar:
        st.markdown("### 📂 Kiểm tra file")
        
        for idx, track in enumerate(TRACKS):
            audio_exists = os.path.exists(track["audio"])
            text_exists = os.path.exists(track["text"])
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Track {idx+1}**")
                if audio_exists:
                    st.success(f"✅ {track['audio']}")
                else:
                    st.error(f"❌ {track['audio']}")
                
                if text_exists:
                    st.success(f"✅ {track['text']}")
                else:
                    st.error(f"❌ {track['text']}")
            
            with col2:
                # Nút chọn track
                if st.button("Chọn", key=f"sidebar_select_{idx}", use_container_width=True):
                    st.session_state.current_track = idx
                    st.session_state.last_action = f"selected_track_{idx}"
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎛️ Cài đặt")
        
        # Điều chỉnh volume bằng Streamlit slider
        new_volume = st.slider("Âm lượng", 0, 100, st.session_state.volume, key="volume_slider")
        if new_volume != st.session_state.volume:
            st.session_state.volume = new_volume
            st.session_state.last_action = "volume_changed"
            st.rerun()
        
        # Điều chỉnh tốc độ bằng Streamlit slider
        new_speed = st.slider("Tốc độ phát", 0.5, 2.0, float(st.session_state.playback_speed), 0.1, key="speed_slider")
        if new_speed != st.session_state.playback_speed:
            st.session_state.playback_speed = new_speed
            st.session_state.last_action = "speed_changed"
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ Thông tin")
        st.info(f"**Track:** {st.session_state.current_track + 1}/{len(TRACKS)}")
        st.info(f"**Trạng thái:** {st.session_state.player_state}")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎛️ Điều khiển phát nhạc")
        
        # Control buttons - Sử dụng Streamlit buttons
        col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)
        
        with col_btn1:
            if st.button("⏮️", key="btn_prev", use_container_width=True, 
                        disabled=st.session_state.current_track == 0):
                st.session_state.current_track = max(0, st.session_state.current_track - 1)
                st.session_state.player_state = "playing"
                st.session_state.last_action = "prev_track"
                st.rerun()
        
        with col_btn2:
            btn_text = "⏸️" if st.session_state.player_state == "playing" else "▶️"
            if st.button(btn_text, key="btn_play_pause", use_container_width=True):
                if st.session_state.player_state == "playing":
                    st.session_state.player_state = "paused"
                else:
                    st.session_state.player_state = "playing"
                st.session_state.last_action = "play_pause"
                st.rerun()
        
        with col_btn3:
            if st.button("⏹️", key="btn_stop", use_container_width=True):
                st.session_state.player_state = "stopped"
                st.session_state.last_action = "stop"
                st.rerun()
        
        with col_btn4:
            if st.button("⏭️", key="btn_next", use_container_width=True,
                        disabled=st.session_state.current_track == len(TRACKS) - 1):
                st.session_state.current_track = min(len(TRACKS) - 1, st.session_state.current_track + 1)
                st.session_state.player_state = "playing"
                st.session_state.last_action = "next_track"
                st.rerun()
        
        with col_btn5:
            if st.button("🔄", key="btn_refresh", use_container_width=True):
                st.session_state.last_action = "refresh"
                st.rerun()
        
        # Track selection buttons
        st.markdown("### 📋 Chọn Track")
        track_cols = st.columns(4)
        for idx in range(len(TRACKS)):
            with track_cols[idx]:
                is_active = idx == st.session_state.current_track
                btn_type = "primary" if is_active else "secondary"
                if st.button(f"Track {idx+1}", key=f"track_btn_{idx}", 
                           type=btn_type, use_container_width=True):
                    st.session_state.current_track = idx
                    st.session_state.player_state = "playing"
                    st.session_state.last_action = f"track_selected_{idx}"
                    st.rerun()
        
        # Hiển thị audio player
        st.markdown("### 🔊 Audio Player")
        audio_player_html = create_audio_player()
        st.components.v1.html(audio_player_html, height=250)
        
        # Thông tin track hiện tại
        current_track_info = TRACKS[st.session_state.current_track]
        st.markdown(f"""
        <div class="status-bar">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <strong>🎵 Track hiện tại:</strong> {st.session_state.current_track + 1}. {current_track_info['audio']}<br>
                    <strong>📄 File text:</strong> {current_track_info['text']}
                </div>
                <div style="text-align: right;">
                    <strong>🔊 Âm lượng:</strong> {st.session_state.volume}%<br>
                    <strong>⚡ Tốc độ:</strong> {st.session_state.playback_speed:.1f}x
                </div>
            </div>
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;">
                <strong>📊 Trạng thái:</strong> <span style="color: {'#4CAF50' if st.session_state.player_state == 'playing' else '#FF9800' if st.session_state.player_state == 'paused' else '#F44336'}">{st.session_state.player_state.upper()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📄 Nội dung Text")
        
        # Load và hiển thị nội dung file text
        current_text_file = TRACKS[st.session_state.current_track]["text"]
        
        if os.path.exists(current_text_file):
            # Hiển thị thông tin file với highlight
            file_size = os.path.getsize(current_text_file)
            
            # Tạo header với highlight
            st.markdown(f"""
            <div style="background-color: #2196F3; color: white; padding: 15px; border-radius: 10px 10px 0 0; margin-bottom: 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: white;">📁 {current_text_file}</h4>
                        <p style="margin: 5px 0 0 0; font-size: 0.9em;">Kích thước: {file_size:,} bytes</p>
                    </div>
                    <div style="background-color: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 20px;">
                        Track {st.session_state.current_track + 1}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Đọc và hiển thị nội dung
            text_content = load_text_file(current_text_file)
            
            if text_content:
                # Tạo text display với scroll và highlight
                st.markdown(f"""
                <div class="text-display">
                    {text_content}
                </div>
                """, unsafe_allow_html=True)
                
                # Thống kê và download button
                col_info, col_download = st.columns([2, 1])
                
                with col_info:
                    lines = text_content.split('\n')
                    words = text_content.split()
                    chars = len(text_content)
                    st.caption(f"📊 Thống kê: {len(lines)} dòng, {len(words)} từ, {chars:,} ký tự")
                
                with col_download:
                    with open(current_text_file, "rb") as f:
                        st.download_button(
                            label="📥 Tải xuống",
                            data=f,
                            file_name=current_text_file,
                            mime="text/plain",
                            use_container_width=True
                        )
            else:
                st.warning("File text tồn tại nhưng không có nội dung hoặc không thể đọc.")
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
    
    # Hướng dẫn sử dụng
    with st.expander("📖 Hướng dẫn sử dụng"):
        st.markdown("""
        ### 🎯 Cách sử dụng:
        
        1. **Chọn track**: 
           - Nhấp vào nút "Track 1", "Track 2", ... trong phần "Chọn Track"
           - Hoặc nhấp nút "Chọn" trong sidebar
           - Track đang chọn sẽ được highlight bằng màu xanh
        
        2. **Điều khiển phát nhạc**:
           - ⏮️: Chuyển đến track trước
           - ▶️/⏸️: Phát/Tạm dừng track hiện tại
           - ⏹️: Dừng phát nhạc
           - ⏭️: Chuyển đến track tiếp theo
           - 🔄: Làm mới trang
        
        3. **Điều chỉnh audio**:
           - Sử dụng thanh trượt "Âm lượng" trong sidebar hoặc trong audio player
           - Sử dụng thanh trượt "Tốc độ phát" trong sidebar hoặc trong audio player
           - Giá trị sẽ được cập nhật ngay lập tức
        
        4. **Xem nội dung text**:
           - Nội dung file text tương ứng sẽ hiển thị trong khung màu xanh
           - Có thể tải xuống file text bằng nút "Tải xuống"
        
        ### 🔧 Xử lý sự cố:
        
        - **Nút không hoạt động**: Nhấp nút 🔄 để làm mới trang
        - **Không nghe được âm thanh**: Kiểm tra xem file audio có tồn tại không
        - **Không thấy nội dung text**: Kiểm tra xem file text có tồn tại không
        """)

if __name__ == "__main__":
    main()
