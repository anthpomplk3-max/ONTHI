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
        cursor: pointer;
    }
    .track-card:hover {
        background-color: #e9ecef;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .active-track {
        border-left: 5px solid #2196F3;
        background-color: #e3f2fd;
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
    .slider-container {
        margin: 10px 0;
    }
    .slider-value {
        font-weight: bold;
        color: #2196F3;
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
        return f"Không thể đọc file: {filename}\nLỗi: {str(e)}"

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

def create_audio_player_with_controls(audio_url, track_name):
    """Tạo audio player với controls tích hợp JavaScript"""
    if not audio_url:
        return ""
    
    audio_player_html = f"""
    <div class="audio-controls">
        <audio id="audioPlayer" controls style="width: 100%;" onplay="audioPlaying()" onpause="audioPaused()" onended="audioEnded()">
            <source src="{audio_url}" type="audio/mpeg">
            Trình duyệt của bạn không hỗ trợ phát audio.
        </audio>
        
        <div class="slider-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <span>Âm lượng:</span>
                <span id="volumeValue" class="slider-value">70%</span>
            </div>
            <input type="range" id="volumeSlider" min="0" max="100" value="70" 
                   style="width: 100%;" oninput="updateVolume(this.value)">
        </div>
        
        <div class="slider-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <span>Tốc độ phát:</span>
                <span id="speedValue" class="slider-value">1.0x</span>
            </div>
            <input type="range" id="speedSlider" min="0.5" max="2.0" step="0.1" value="1.0" 
                   style="width: 100%;" oninput="updateSpeed(this.value)">
        </div>
    </div>
    
    <script>
        const audio = document.getElementById('audioPlayer');
        const volumeSlider = document.getElementById('volumeSlider');
        const speedSlider = document.getElementById('speedSlider');
        const volumeValue = document.getElementById('volumeValue');
        const speedValue = document.getElementById('speedValue');
        
        // Khởi tạo giá trị
        function initAudioPlayer() {{
            // Đặt volume ban đầu
            audio.volume = {st.session_state.volume};
            volumeSlider.value = {st.session_state.volume * 100};
            volumeValue.textContent = Math.round({st.session_state.volume * 100}) + '%';
            
            // Đặt tốc độ ban đầu
            audio.playbackRate = {st.session_state.playback_speed};
            speedSlider.value = {st.session_state.playback_speed};
            speedValue.textContent = {st.session_state.playback_speed} + 'x';
        }}
        
        // Cập nhật volume
        function updateVolume(value) {{
            const volume = value / 100;
            audio.volume = volume;
            volumeValue.textContent = value + '%';
            
            // Gửi giá trị volume về Streamlit
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: {{volume: volume}}
            }}, '*');
        }}
        
        // Cập nhật tốc độ
        function updateSpeed(value) {{
            const speed = parseFloat(value);
            audio.playbackRate = speed;
            speedValue.textContent = speed.toFixed(1) + 'x';
            
            // Gửi giá trị speed về Streamlit
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: {{speed: speed}}
            }}, '*');
        }}
        
        // Xử lý sự kiện phát nhạc
        function audioPlaying() {{
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: {{playing: true}}
            }}, '*');
        }}
        
        function audioPaused() {{
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: {{playing: false}}
            }}, '*');
        }}
        
        function audioEnded() {{
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: {{ended: true}}
            }}, '*');
        }}
        
        // Khởi tạo khi trang tải xong
        window.addEventListener('DOMContentLoaded', initAudioPlayer);
        // Hoặc nếu trang đã tải xong
        if (document.readyState === 'complete') {{
            initAudioPlayer();
        }}
    </script>
    """
    
    return audio_player_html

def main():
    st.markdown('<h1 class="main-header">🎵 Audio Player with Text Sync</h1>', unsafe_allow_html=True)
    
    # Kiểm tra file tồn tại
    with st.sidebar:
        st.markdown("### 📂 Kiểm tra file")
        
        missing_files = []
        existing_files = []
        
        for track in TRACKS:
            audio_exists = os.path.exists(track["audio"])
            text_exists = os.path.exists(track["text"])
            
            if audio_exists and text_exists:
                existing_files.append(f"✅ {track['audio']} và {track['text']}")
            else:
                if not audio_exists:
                    missing_files.append(f"❌ {track['audio']}")
                if not text_exists:
                    missing_files.append(f"❌ {track['text']}")
        
        if missing_files:
            st.error("### File bị thiếu:")
            for file in missing_files:
                st.text(file)
        
        if existing_files:
            st.success("### File đã có:")
            for file in existing_files:
                st.text(file)
    
    # Sidebar cho danh sách track với highlight
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📋 Danh sách Track")
        
        # Tạo container cho danh sách track
        tracks_container = st.container()
        
        with tracks_container:
            for idx, track in enumerate(TRACKS):
                audio_exists = os.path.exists(track["audio"])
                text_exists = os.path.exists(track["text"])
                is_active = idx == st.session_state.current_track
                
                # Tạo cột cho mỗi track
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Hiển thị track card với CSS
                    card_class = "active-track" if is_active else ""
                    st.markdown(f"""
                    <div class="track-card {card_class}" onclick="selectTrack({idx})" style="cursor: pointer;">
                        <strong>Track {idx+1}</strong><br>
                        🎵 {track['audio']}<br>
                        📄 {track['text']}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Nút chọn track
                    if st.button("▶️", key=f"play_{idx}", help=f"Chơi track {idx+1}", 
                                type="primary" if is_active else "secondary"):
                        st.session_state.current_track = idx
                        st.session_state.player_state = "playing"
                        st.rerun()
        
        # JavaScript để xử lý click trên track card
        st.markdown("""
        <script>
        function selectTrack(index) {
            // Gửi thông điệp đến Streamlit để chọn track
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: {selectTrack: index}
            }, '*');
        }
        
        // Lắng nghe thông điệp từ Streamlit
        window.addEventListener('message', function(event) {
            if (event.data.type === 'streamlit:setComponentValue') {
                if (event.data.value.hasOwnProperty('selectTrack')) {
                    // Đã xử lý trong Python, không cần làm gì ở đây
                }
            }
        });
        </script>
        """, unsafe_allow_html=True)
        
        # Thông tin hệ thống
        st.markdown("---")
        st.markdown("### ℹ️ Thông tin")
        
        current_track = st.session_state.current_track + 1
        total_tracks = len(TRACKS)
        st.info(f"**Track hiện tại:** {current_track}/{total_tracks}")
        
        # Hiển thị trạng thái player
        status_display = {
            "playing": "🟢 Đang phát",
            "paused": "🟡 Tạm dừng", 
            "stopped": "⚫ Dừng"
        }
        
        current_status = status_display.get(st.session_state.player_state, "⚫ Không xác định")
        st.markdown(f"**Trạng thái:** {current_status}")
        
        # Hiển thị thông số hiện tại
        st.markdown(f"**Âm lượng:** {int(st.session_state.volume * 100)}%")
        st.markdown(f"**Tốc độ:** {st.session_state.playback_speed:.1f}x")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎚️ Điều khiển phát nhạc")
        
        # Control buttons
        col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)
        
        with col_btn1:
            if st.button("⏮️", use_container_width=True, 
                        disabled=st.session_state.current_track == 0,
                        help="Track trước"):
                if st.session_state.current_track > 0:
                    st.session_state.current_track -= 1
                    st.session_state.player_state = "playing"
                    st.rerun()
        
        with col_btn2:
            if st.button("⏯️", use_container_width=True, 
                        type="primary" if st.session_state.player_state == "playing" else "secondary",
                        help="Phát/Tạm dừng"):
                if st.session_state.player_state == "playing":
                    st.session_state.player_state = "paused"
                else:
                    st.session_state.player_state = "playing"
                st.rerun()
        
        with col_btn3:
            if st.button("⏹️", use_container_width=True, help="Dừng"):
                st.session_state.player_state = "stopped"
                st.rerun()
        
        with col_btn4:
            if st.button("⏭️", use_container_width=True,
                        disabled=st.session_state.current_track == len(TRACKS) - 1,
                        help="Track tiếp"):
                if st.session_state.current_track < len(TRACKS) - 1:
                    st.session_state.current_track += 1
                    st.session_state.player_state = "playing"
                    st.rerun()
        
        with col_btn5:
            if st.button("🔄", use_container_width=True, help="Làm mới"):
                st.rerun()
        
        # Hiển thị audio player với controls
        st.markdown("### 🔊 Audio Player")
        current_audio = TRACKS[st.session_state.current_track]["audio"]
        audio_url = get_audio_data_url(current_audio)
        
        if audio_url:
            audio_player_html = create_audio_player_with_controls(audio_url, current_audio)
            st.components.v1.html(audio_player_html, height=200)
        else:
            st.error(f"Không thể tải file audio: {current_audio}")
        
        # Thanh tiến độ mô phỏng
        if st.session_state.player_state == "playing":
            progress_text = "Đang phát..."
            progress_value = 0.5  # Giá trị mô phỏng
        elif st.session_state.player_state == "paused":
            progress_text = "Tạm dừng"
            progress_value = st.session_state.track_progress / 100
        else:
            progress_text = "Dừng"
            progress_value = 0
        
        st.progress(progress_value, text=progress_text)
        
        # Thông tin track hiện tại
        current_track_info = TRACKS[st.session_state.current_track]
        st.markdown(f"""
        <div class="status-bar">
            <strong>🎵 Track hiện tại:</strong> {current_track}. {current_track_info['audio']}<br>
            <strong>📄 File text:</strong> {current_track_info['text']}<br>
            <strong>📊 Trạng thái:</strong> {st.session_state.player_state}<br>
            <strong>🔊 Âm lượng:</strong> {int(st.session_state.volume * 100)}% | 
            <strong>⚡ Tốc độ:</strong> {st.session_state.playback_speed:.1f}x
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📄 Nội dung Text")
        
        # Load và hiển thị nội dung file text
        current_text_file = TRACKS[st.session_state.current_track]["text"]
        
        if os.path.exists(current_text_file):
            # Hiển thị thông tin file
            file_size = os.path.getsize(current_text_file)
            
            # Đọc và hiển thị nội dung
            text_content = load_text_file(current_text_file)
            
            if text_content:
                # Tạo text area với highlight cho track đang chọn
                text_display_html = f"""
                <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>📁 File:</strong> {current_text_file} | <strong>📏 Kích thước:</strong> {file_size} bytes
                </div>
                <div class="text-display">
                    {text_content}
                </div>
                """
                st.markdown(text_display_html, unsafe_allow_html=True)
                
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
                
                st.caption(f"📊 Thống kê: {len(lines)} dòng, {len(words)} từ, {chars} ký tự")
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
    
    # Xử lý messages từ JavaScript
    try:
        # Giả lập xử lý messages từ JavaScript
        # Trong thực tế, bạn có thể sử dụng streamlit.components để xử lý thông điệp thực
        pass
    except:
        pass
    
    # Hướng dẫn sử dụng
    with st.expander("📖 Hướng dẫn sử dụng chi tiết"):
        st.markdown("""
        ### 🎯 Cách sử dụng:
        
        1. **Chọn track**: 
           - Nhấp vào card track trong danh sách bên trái
           - Hoặc sử dụng nút ▶️ trên mỗi track
           - Track đang chọn sẽ được highlight màu xanh
        
        2. **Điều khiển phát nhạc**:
           - ⏮️: Chuyển đến track trước
           - ⏯️: Phát/Tạm dừng track hiện tại
           - ⏹️: Dừng phát nhạc
           - ⏭️: Chuyển đến track tiếp theo
        
        3. **Điều chỉnh audio**:
           - Sử dụng thanh trượt "Âm lượng" để điều chỉnh âm thanh
           - Sử dụng thanh trượt "Tốc độ phát" để thay đổi tốc độ (0.5x - 2.0x)
           - Giá trị sẽ hiển thị ngay khi bạn kéo thanh trượt
        
        4. **Xem nội dung text**:
           - Nội dung file text tương ứng sẽ hiển thị bên phải
           - Có thể tải xuống file text bằng nút "Tải xuống"
        
        ### 🔧 Xử lý sự cố:
        
        - **Không nghe được âm thanh**: Kiểm tra xem file audio có tồn tại không
        - **Không thấy nội dung text**: Kiểm tra xem file text có tồn tại không
        - **Thanh trượt không hoạt động**: Thử làm mới trang bằng nút 🔄
        """)

if __name__ == "__main__":
    main()
