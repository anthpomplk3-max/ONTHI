import streamlit as st
import os
import base64
from pydub import AudioSegment

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="QT Audio Player Pro", page_icon="🎧", layout="wide")

# --- CÁC HÀM XỬ LÝ ---

def get_audio_duration(audio_file):
    """Lấy độ dài file âm thanh (giây)"""
    try:
        audio = AudioSegment.from_file(audio_file)
        return len(audio) / 1000.0
    except Exception as e:
        st.error(f"Không đọc được độ dài audio. Hãy cài đặt ffmpeg. Lỗi: {e}")
        return 0

def load_text_lines(txt_file):
    """Đọc file text và trả về danh sách dòng"""
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        return lines
    except:
        # Thử encoding khác nếu utf-8 lỗi
        try:
            with open(txt_file, 'r', encoding='latin-1') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            return lines
        except:
            return ["Lỗi đọc file văn bản."]

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    return bin_str

# --- LOGIC TÌM FILE ---
def check_files():
    """Kiểm tra các cặp file QT có sẵn trong thư mục"""
    available_files = {}
    target_numbers = [58, 72, 83, 85] # Danh sách file yêu cầu
    
    files_in_dir = os.listdir('.')
    
    for num in target_numbers:
        # Các biến thể tên file có thể gặp
        patterns = [
            (f"QT {num}.mp3", f"QT {num}.txt"),
            (f"QT{num}.mp3", f"QT{num}.txt"),
            (f"qt {num}.mp3", f"qt {num}.txt")
        ]
        
        for mp3_name, txt_name in patterns:
            if mp3_name in files_in_dir and txt_name in files_in_dir:
                available_files[num] = {'mp3': mp3_name, 'txt': txt_name}
                break
    
    return available_files

# --- GIAO DIỆN CHÍNH ---

st.title("🎧 Trình phát Audio QT: 58, 72, 83, 85")
st.markdown("---")

# 1. Sidebar chọn bài
available_files = check_files()

with st.sidebar:
    st.header("📂 Danh sách bài")
    
    if not available_files:
        st.warning("⚠️ Không tìm thấy file QT (mp3/txt) nào.")
        st.info("Vui lòng copy các file `QT 58.mp3`, `QT 58.txt`... vào cùng thư mục với file code này.")
    
    selected_qt = st.radio(
        "Chọn bài học:",
        options=list(available_files.keys()),
        format_func=lambda x: f"Bài QT {x}",
        index=0 if available_files else None
    )

    st.markdown("---")
    st.markdown("**Hướng dẫn:**")
    st.caption("1. Chọn bài học bên trên.")
    st.caption("2. Bấm vào dòng văn bản để nhảy Audio đến đoạn đó.")
    st.caption("3. Điều chỉnh tốc độ nếu nghe không kịp.")

# Khởi tạo biến Session State
if 'current_qt' not in st.session_state:
    st.session_state.current_qt = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'highlight_line' not in st.session_state:
    st.session_state.highlight_line = -1

# Nếu người dùng đổi bài
if selected_qt and selected_qt != st.session_state.current_qt:
    st.session_state.current_qt = selected_qt
    st.session_state.start_time = 0
    st.session_state.highlight_line = -1
    st.rerun()

# --- XỬ LÝ NỘI DUNG ---
if st.session_state.current_qt:
    files = available_files[st.session_state.current_qt]
    
    # Load dữ liệu
    lines = load_text_lines(files['txt'])
    duration = get_audio_duration(files['mp3'])
    
    # Tính thời gian trung bình mỗi dòng (Ước lượng để map dòng -> thời gian)
    if len(lines) > 0 and duration > 0:
        time_per_line = duration / len(lines)
    else:
        time_per_line = 0

    # --- KHU VỰC PLAYER & ĐIỀU KHIỂN ---
    col_player, col_settings = st.columns([3, 1])
    
    with col_settings:
        st.subheader("⚙️ Cài đặt")
        playback_rate = st.select_slider(
            "Tốc độ phát (Speed):",
            options=[0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
            value=1.0
        )
        
    with col_player:
        st.subheader(f"Đang phát: {files['mp3']}")
        
        # Đọc file audio để nhúng vào HTML
        audio_base64 = get_binary_file_downloader_html(files['mp3'])
        
        # Tạo Audio Player HTML tùy chỉnh với JS để xử lý seek và speed
        # Lưu ý: autoplay=True để khi bấm dòng văn bản nó tự phát ngay
        audio_html = f"""
            <audio id="audioPlayer" controls autoplay style="width: 100%;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            
            <script>
                var audio = document.getElementById("audioPlayer");
                
                // Thiết lập tốc độ
                audio.playbackRate = {playback_rate};
                
                // Thiết lập thời gian bắt đầu (nếu có yêu cầu seek)
                // Chỉ set currentTime 1 lần khi load để tránh loop
                var setTime = {st.session_state.start_time};
                if(setTime > 0) {{
                    audio.currentTime = setTime;
                    audio.play(); 
                }}
            </script>
        """
        st.components.v1.html(audio_html, height=60)

    # --- KHU VỰC VĂN BẢN (CLICK ĐỂ NGHE) ---
    st.subheader("📝 Nội dung bài học (Kích vào dòng để nghe)")
    
    # Container cuộn cho văn bản
    with st.container(height=600):
        for idx, line in enumerate(lines):
            # Tính toán style: Nếu là dòng đang chọn -> Highlight
            is_active = (idx == st.session_state.highlight_line)
            
            # Sử dụng st.button để làm dòng văn bản có thể click được
            # Nếu active, dùng type="primary" để đổi màu
            btn_type = "primary" if is_active else "secondary"
            
            # Logic click:
            if st.button(f"{idx + 1}. {line}", key=f"line_{idx}", use_container_width=True, type=btn_type):
                # Khi click vào dòng:
                # 1. Tính thời gian tương ứng
                new_time = idx * time_per_line
                # 2. Cập nhật state
                st.session_state.start_time = new_time
                st.session_state.highlight_line = idx
                # 3. Rerun để Player nhận start_time mới trong HTML
                st.rerun()

else:
    st.write("Vui lòng tải file lên server hoặc đặt vào thư mục chạy ứng dụng.")
