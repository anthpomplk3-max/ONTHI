import streamlit as st
import pygame
import os
import time
from pygame import mixer
import base64

# Khởi tạo pygame mixer
mixer.init()

# Hàm để định dạng thời gian
def format_time(seconds):
    if seconds < 0:
        seconds = 0
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

# Hàm để autoplay audio
def autoplay_audio(audio_file):
    with open(audio_file, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true" style="width: 100%">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(md, unsafe_allow_html=True)

# Danh sách các file có sẵn
def get_available_files():
    available = {}
    for num in [58, 72, 83, 85]:
        mp3_file = f"QT {num}.mp3"
        txt_file = f"QT {num}.txt"
        if os.path.exists(mp3_file) and os.path.exists(txt_file):
            available[num] = {'mp3': mp3_file, 'txt': txt_file}
    return available

# Đọc nội dung file văn bản
def load_text_content(txt_file):
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return [line.strip() for line in lines]
    except:
        return []

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
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'current_position' not in st.session_state:
    st.session_state.current_position = 0
if 'audio_length' not in st.session_state:
    st.session_state.audio_length = 0
if 'highlight_index' not in st.session_state:
    st.session_state.highlight_index = -1
if 'volume' not in st.session_state:
    st.session_state.volume = 70
if 'speed' not in st.session_state:
    st.session_state.speed = 100

# Sidebar để chọn file và điều khiển
with st.sidebar:
    st.header("📂 Chọn File")
    
    # Tải danh sách file
    available_files = get_available_files()
    
    # Nút chọn file
    for num in [58, 72, 83, 85]:
        if num in available_files:
            if st.button(f"QT {num}", key=f"btn_{num}", use_container_width=True):
                # Dừng audio đang phát
                if st.session_state.is_playing:
                    mixer.music.stop()
                    st.session_state.is_playing = False
                
                # Tải file mới
                files = available_files[num]
                st.session_state.current_audio = files['mp3']
                st.session_state.current_text_file = files['txt']
                st.session_state.text_lines = load_text_content(files['txt'])
                
                # Tải audio
                mixer.music.load(st.session_state.current_audio)
                
                # Lấy độ dài audio
                sound = mixer.Sound(st.session_state.current_audio)
                st.session_state.audio_length = sound.get_length()
                
                # Reset
                st.session_state.current_position = 0
                st.session_state.highlight_index = -1
                
                st.success(f"✅ Đã tải QT {num}")
        else:
            st.warning(f"QT {num} - File không tìm thấy")
    
    st.header("🎛️ Điều Khiển")
    
    col1, col2 = st.columns(2)
    with col1:
        play_btn = st.button("▶ Phát", use_container_width=True, 
                           disabled=st.session_state.current_audio is None)
        if play_btn and st.session_state.current_audio:
            if not st.session_state.is_playing:
                mixer.music.play(start=st.session_state.current_position)
                st.session_state.is_playing = True
                st.session_state.play_start_time = time.time() - st.session_state.current_position
    
    with col2:
        pause_btn = st.button("⏸ Dừng", use_container_width=True,
                            disabled=st.session_state.current_audio is None)
        if pause_btn and st.session_state.current_audio:
            if st.session_state.is_playing:
                mixer.music.pause()
                st.session_state.is_playing = False
            else:
                mixer.music.unpause()
                st.session_state.is_playing = True
    
    stop_btn = st.button("⏹ Dừng hẳn", use_container_width=True,
                        disabled=st.session_state.current_audio is None)
    if stop_btn and st.session_state.current_audio:
        mixer.music.stop()
        st.session_state.is_playing = False
        st.session_state.current_position = 0
        st.session_state.highlight_index = -1
    
    st.header("⚙️ Cài Đặt")
    
    # Âm lượng
    volume = st.slider("🔊 Âm lượng", 0, 100, 
                      st.session_state.volume, 
                      key="volume_slider")
    if volume != st.session_state.volume:
        st.session_state.volume = volume
        mixer.music.set_volume(volume / 100.0)
    
    # Tốc độ
    speed = st.slider("⚡ Tốc độ (%)", 50, 200, 
                     st.session_state.speed, 
                     key="speed_slider")
    if speed != st.session_state.speed:
        st.session_state.speed = speed
        # Lưu ý: Pygame không hỗ trợ thay đổi tốc độ trực tiếp
        # Đây chỉ là để hiển thị

# Main content - Hiển thị file hiện tại
if st.session_state.current_audio:
    st.subheader(f"🎶 Đang chọn: {os.path.basename(st.session_state.current_audio)}")
    
    # Hiển thị thanh tiến trình và thời gian
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        # Tính toán vị trí hiện tại nếu đang phát
        if st.session_state.is_playing:
            current_time = st.session_state.current_position + (time.time() - st.session_state.get('play_start_time', time.time()))
            if current_time > st.session_state.audio_length:
                current_time = st.session_state.audio_length
        else:
            current_time = st.session_state.current_position
        
        # Thanh trượt tiến độ
        new_position = st.slider(
            "Tiến độ",
            0.0,
            st.session_state.audio_length,
            current_time,
            key="progress_slider",
            format="%ds",
            label_visibility="collapsed"
        )
        
        # Nếu người dùng kéo thanh trượt
        if new_position != current_time:
            st.session_state.current_position = new_position
            if st.session_state.is_playing:
                mixer.music.stop()
                mixer.music.play(start=new_position)
                st.session_state.play_start_time = time.time() - new_position
    
    with col2:
        st.metric("Thời gian", format_time(current_time))
    with col3:
        st.metric("Tổng thời gian", format_time(st.session_state.audio_length))
    
    # Hiển thị trạng thái
    status = "▶ Đang phát" if st.session_state.is_playing else "⏸ Đã dừng"
    st.info(f"**Trạng thái:** {status}")
    
    # Hiển thị văn bản với highlight
    st.subheader("📝 Nội dung")
    
    # Tạo một container để hiển thị văn bản
    text_container = st.container()
    
    # Nếu có văn bản, hiển thị từng dòng với khả năng click
    if st.session_state.text_lines:
        # Tạo columns cho mỗi dòng
        cols = st.columns(1)
        
        # Tính toán dòng đang được phát nếu đang phát
        if st.session_state.is_playing:
            current_time_playing = st.session_state.current_position + (time.time() - st.session_state.get('play_start_time', time.time()))
            time_per_line = st.session_state.audio_length / len(st.session_state.text_lines)
            line_index = int(current_time_playing / time_per_line)
            line_index = min(line_index, len(st.session_state.text_lines) - 1)
            st.session_state.highlight_index = line_index
        
        with text_container:
            for i, line in enumerate(st.session_state.text_lines):
                # Tạo một button cho mỗi dòng
                line_display = f"{i+1}. {line}"
                
                # Nếu là dòng đang được highlight, tô màu nền
                if i == st.session_state.highlight_index:
                    st.markdown(
                        f'<div style="background-color: #FFFF99; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 5px solid #FF9900;">{line_display}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    # Tạo một expander cho mỗi dòng để có thể click
                    with st.expander(line_display, expanded=False):
                        st.write(" ")
                        # Nút để nhảy đến thời điểm của dòng này
                        if st.button(f"🎯 Nhảy đến dòng {i+1}", key=f"jump_{i}"):
                            # Tính thời gian tương ứng với dòng
                            time_per_line = st.session_state.audio_length / len(st.session_state.text_lines)
                            jump_time = i * time_per_line
                            
                            st.session_state.current_position = jump_time
                            st.session_state.highlight_index = i
                            
                            # Nếu đang phát, dừng và phát lại từ vị trí mới
                            if st.session_state.is_playing:
                                mixer.music.stop()
                                mixer.music.play(start=jump_time)
                                st.session_state.play_start_time = time.time() - jump_time
                            
                            st.rerun()
    
    # Audio player HTML5 (backup)
    st.subheader("🎧 Nghe trực tiếp")
    try:
        autoplay_audio(st.session_state.current_audio)
    except:
        st.warning("Không thể hiển thị audio player. Vui lòng sử dụng nút điều khiển bên trái.")
    
    # Cập nhật thời gian nếu đang phát
    if st.session_state.is_playing:
        current_time = st.session_state.current_position + (time.time() - st.session_state.get('play_start_time', time.time()))
        if current_time >= st.session_state.audio_length:
            # Kết thúc bài hát
            mixer.music.stop()
            st.session_state.is_playing = False
            st.session_state.current_position = 0
            st.session_state.highlight_index = -1
            st.rerun()
        else:
            # Tự động cập nhật sau 0.5 giây
            time.sleep(0.5)
            st.rerun()
            
else:
    st.info("👈 Vui lòng chọn một file từ sidebar để bắt đầu.")
    
    # Hiển thị danh sách file có sẵn
    st.subheader("📁 File có sẵn trong thư mục:")
    files = get_available_files()
    if files:
        for num, file_info in files.items():
            st.write(f"✅ **QT {num}:**")
            st.write(f"   - Âm thanh: `{file_info['mp3']}`")
            st.write(f"   - Văn bản: `{file_info['txt']}`")
    else:
        st.warning("Không tìm thấy file QT 58, 72, 83, 85 trong thư mục hiện tại.")

# Footer
st.markdown("---")
st.caption("QT Audio Player - Streamlit Version | Sử dụng Pygame và Streamlit")

# Lưu ý về requirements
with st.expander("📋 Yêu cầu hệ thống"):
    st.write("""
    1. **Thư viện cần cài đặt:**
       ```
       pip install streamlit pygame
       ```
       
    2. **Cấu trúc thư mục:**
       - Đặt file .py này cùng thư mục với các file:
         - QT 58.mp3, QT 58.txt
         - QT 72.mp3, QT 72.txt
         - QT 83.mp3, QT 83.txt
         - QT 85.mp3, QT 85.txt
       
    3. **Chạy ứng dụng:**
       ```
       streamlit run app.py
       ```
       
    4. **Lưu ý trên Streamlit Cloud:**
       - Thêm file `requirements.txt` với nội dung:
       ```
       streamlit>=1.28.0
       pygame>=2.5.0
       ```
       - Upload cả file âm thanh và văn bản lên
    """)
