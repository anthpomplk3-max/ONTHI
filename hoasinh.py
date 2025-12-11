import streamlit as st
import pyttsx3
import threading
import time
import re
from collections import Counter

# Cấu hình trang
st.set_page_config(
    page_title="QT Hóa Sinh - TTS Reader",
    page_icon="🔬",  # Đã sửa lỗi ở đây
    layout="wide"
)

# CSS tùy chỉnh
st.markdown("""
<style>
    .main-header {
        color: #2E86AB;
        text-align: center;
        padding: 1rem;
        border-bottom: 3px solid #2E86AB;
        margin-bottom: 2rem;
    }
    .highlighted {
        background-color: #FFE066;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        transition: background-color 0.3s;
        border-left: 4px solid #2E86AB;
    }
    .normal-text {
        padding: 8px;
        margin: 5px 0;
        border-left: 4px solid transparent;
    }
    .sidebar-header {
        color: #2E86AB;
        font-weight: bold;
        margin-top: 1rem;
    }
    .stats-box {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin: 10px 0;
    }
    .control-panel {
        background-color: #E9F5FB;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo engine TTS
@st.cache_resource
def init_tts_engine():
    engine = pyttsx3.init()
    return engine

# Tải tài liệu
def load_document():
    # Tài liệu QT Hóa Sinh (đã rút gọn)
    document_content = """
    # QT 58: ĐỊNH LƯỢNG CÁC CHẤT ĐIỆN GIẢI (NA+, K+, CL-)
    
    ## NGUYÊN LÝ
    Các chất điện giải liên quan đến rất nhiều các chuyển hóa quan trọng trong cơ thể.
    Na+, K+, Cl- là các ion quan trọng nhất và được sử dụng nhiều nhất.
    
    ## CHUẨN BỊ
    1. Người thực hiện: bác sỹ hoặc kỹ thuật viên được đào tạo chuyên ngành Hóa sinh
    2. Phương tiện, hóa chất: Máy móc, thuốc thử, điện cực, chuẩn, control
    3. Người bệnh: nhịn ăn sáng và lấy máu vào buổi sáng
    4. Phiếu xét nghiệm: có đầy đủ thông tin về người bệnh
    
    ## CÁC BƯỚC TIẾN HÀNH
    1. Lấy bệnh phẩm: lấy máu đúng kỹ thuật
    2. Tiến hành kỹ thuật: phân tích trên máy sinh hóa
    
    ## NHẬN ĐỊNH KẾT QUẢ
    - Bình thường:
      Na: 133-147 mmol/l
      K: 3.4-4.5 mmol/l
      Clo: 94-111 mmol/l
    
    # QT 72: ĐO HOẠT ĐỘ G6PD
    
    ## NGUYÊN LÝ
    Hoạt độ Enzym được xác định bằng cách đo tốc độ tăng mật độ quang
    
    ## CHUẨN BỊ
    1. Người thực hiện: 02 người là bác sĩ, kỹ thuật viên
    2. Phương tiện, hóa chất: Máy hóa sinh tự động, hóa chất Randox
    
    ## CÁC BƯỚC TIẾN HÀNH
    1. Lấy bệnh phẩm: máu toàn phần
    2. Tiến hành kỹ thuật: rửa hồng cầu, chạy phân tích
    
    ## NHẬN ĐỊNH KẾT QUẢ
    - Giá trị tham chiếu: > 200 IU/10^12 Hồng cầu
    - Ý nghĩa lâm sàng: thiếu hụt G6PD là rối loạn Enzym liên quan giới tính
    
    # QT 83: ĐỊNH LƯỢNG HBA1C
    
    ## NGUYÊN LÝ
    Hemoglobin A1c hình thành khi glucose kết hợp với hemoglobin
    
    ## CHUẨN BỊ
    1. Người thực hiện: 01 cán bộ đại học và 01 kỹ thuật viên
    2. Phương tiện, hóa chất: máy HPLC, hóa chất chuyên dụng
    
    ## CÁC BƯỚC TIẾN HÀNH
    1. Lấy bệnh phẩm: 2 mL máu toàn phần
    2. Tiến hành kỹ thuật: phân tích trên máy HPLC
    
    ## NHẬN ĐỊNH KẾT QUẢ
    - Giá trị bình thường: 4-6%
    - Tăng khi > 6.5%
    
    # QT 85: ĐỊNH LƯỢNG HE4
    
    ## NGUYÊN LÝ
    HE4 là protein mào tinh người, tăng trong ung thư buồng trứng
    
    ## CHUẨN BỊ
    1. Người thực hiện: 01 cán bộ đại học, 01 kỹ thuật viên
    2. Phương tiện, hóa chất: máy miễn dịch, hóa chất HE4
    
    ## CÁC BƯỚC TIẾN HÀNH
    1. Lấy bệnh phẩm: 3 ml máu tĩnh mạch
    2. Tiến hành kỹ thuật: phân tích trên máy miễn dịch
    
    ## NHẬN ĐỊNH KẾT QUẢ
    - Giá trị bình thường theo tuổi
    - Tăng trong ung thư buồng trứng
    """
    
    # Chia thành các đoạn
    paragraphs = []
    for line in document_content.strip().split('\n'):
        if line.strip():
            paragraphs.append(line.strip())
    
    return paragraphs

# Xử lý đọc văn bản
class TextToSpeechPlayer:
    def __init__(self):
        self.engine = init_tts_engine()
        self.is_playing = False
        self.current_index = 0
        self.paragraphs = []
        self.thread = None
        self.stop_flag = False
        self.volume = 0.7
        self.rate = 150
        
    def set_text(self, paragraphs):
        self.paragraphs = paragraphs
        
    def start_reading(self):
        if not self.is_playing and self.paragraphs:
            self.is_playing = True
            self.stop_flag = False
            self.thread = threading.Thread(target=self._read_all)
            self.thread.start()
            
    def stop_reading(self):
        self.stop_flag = True
        self.is_playing = False
        if hasattr(self.engine, '_inLoop') and self.engine._inLoop:
            self.engine.stop()
        
    def pause_reading(self):
        self.is_playing = False
        if hasattr(self.engine, '_inLoop') and self.engine._inLoop:
            self.engine.stop()
            
    def resume_reading(self):
        if not self.is_playing and self.current_index < len(self.paragraphs):
            self.is_playing = True
            self.stop_flag = False
            self.thread = threading.Thread(target=self._read_from_current)
            self.thread.start()
            
    def _read_all(self):
        self.current_index = 0
        self._read_segments()
        
    def _read_from_current(self):
        self._read_segments()
        
    def _read_segments(self):
        self.engine.setProperty('rate', self.rate)
        self.engine.setProperty('volume', self.volume)
        
        for i in range(self.current_index, len(self.paragraphs)):
            if self.stop_flag:
                break
                
            if self.is_playing:
                self.current_index = i
                # Cập nhật trạng thái trong session
                if 'current_index' in st.session_state:
                    st.session_state.current_index = i
                if 'is_playing' in st.session_state:
                    st.session_state.is_playing = True
                
                # Đọc đoạn văn bản
                self.engine.say(self.paragraphs[i])
                self.engine.runAndWait()
                
                # Nghỉ ngắn giữa các đoạn
                time.sleep(0.3)
            else:
                break
                
        self.is_playing = False
        if 'is_playing' in st.session_state:
            st.session_state.is_playing = False

# Thống kê tài liệu
def calculate_statistics(text):
    # Tính số từ
    words = re.findall(r'\b\w+\b', text)
    word_count = len(words)
    
    # Tính số câu
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    # Tính số đoạn
    paragraphs = [p for p in text.split('\n') if p.strip()]
    paragraph_count = len(paragraphs)
    
    # Tính thời gian đọc ước tính (từ/phút)
    reading_time_minutes = word_count / 150  # 150 từ/phút
    
    # Tần suất từ
    word_freq = Counter([word.lower() for word in words])
    most_common_words = word_freq.most_common(10)
    
    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'paragraph_count': paragraph_count,
        'reading_time': reading_time_minutes,
        'most_common_words': most_common_words
    }

# Giao diện chính
def main():
    st.markdown("<h1 class='main-header'>QT Hóa Sinh - Trình Đọc Tài Liệu</h1>", unsafe_allow_html=True)
    
    # Khởi tạo session state
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False
    if 'player' not in st.session_state:
        st.session_state.player = TextToSpeechPlayer()
    
    # Sidebar - Điều khiển và thống kê
    with st.sidebar:
        st.markdown("<h3 class='sidebar-header'>Điều Khiển Đọc</h3>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Bắt đầu đọc", use_container_width=True):
                    st.session_state.player.start_reading()
                    
            with col2:
                if st.button("⏸️ Tạm dừng", use_container_width=True):
                    st.session_state.player.pause_reading()
            
            col3, col4 = st.columns(2)
            with col3:
                if st.button("⏯️ Tiếp tục", use_container_width=True):
                    st.session_state.player.resume_reading()
                    
            with col4:
                if st.button("⏹️ Dừng", use_container_width=True):
                    st.session_state.player.stop_reading()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Điều chỉnh âm lượng và tốc độ
        st.markdown("<h3 class='sidebar-header'>Cài Đặt</h3>", unsafe_allow_html=True)
        
        volume = st.slider("Âm lượng", 0.0, 1.0, 0.7, 0.1)
        st.session_state.player.volume = volume
        
        rate = st.slider("Tốc độ đọc", 100, 300, 150, 10)
        st.session_state.player.rate = rate
        
        # Thống kê
        st.markdown("<h3 class='sidebar-header'>Thống Kê Tài Liệu</h3>", unsafe_allow_html=True)
        
        # Tải tài liệu
        paragraphs = load_document()
        full_text = " ".join(paragraphs)
        stats = calculate_statistics(full_text)
        
        st.markdown(f"""
        <div class='stats-box'>
            <b>Tổng số đoạn:</b> {stats['paragraph_count']}<br>
            <b>Tổng số từ:</b> {stats['word_count']}<br>
            <b>Tổng số câu:</b> {stats['sentence_count']}<br>
            <b>Thời gian đọc ước tính:</b> {stats['reading_time']:.1f} phút<br>
        </div>
        """, unsafe_allow_html=True)
        
        # Hiển thị từ thông dụng
        with st.expander("10 từ xuất hiện nhiều nhất"):
            for word, count in stats['most_common_words']:
                st.write(f"**{word}**: {count} lần")
    
    # Main area - Hiển thị văn bản
    st.markdown("<h3 class='sidebar-header'>Nội Dung Tài Liệu</h3>", unsafe_allow_html=True)
    
    # Tải và hiển thị văn bản
    paragraphs = load_document()
    st.session_state.player.set_text(paragraphs)
    
    # Hiển thị thanh tiến trình
    progress_text = f"Đang đọc: Đoạn {st.session_state.current_index + 1}/{len(paragraphs)}"
    progress = (st.session_state.current_index + 1) / len(paragraphs) if len(paragraphs) > 0 else 0
    st.progress(progress, text=progress_text)
    
    # Tạo container cho văn bản với cuộn
    text_container = st.container()
    
    with text_container:
        for i, paragraph in enumerate(paragraphs):
            # Làm nổi bật đoạn đang được đọc
            if i == st.session_state.current_index and st.session_state.is_playing:
                st.markdown(f"""
                <div class='highlighted'>
                    <b>Đang đọc:</b> {paragraph}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='normal-text'>
                    {paragraph}
                </div>
                """, unsafe_allow_html=True)
            
            # Thêm khoảng cách nhỏ giữa các đoạn
            st.write("")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>QT Hóa Sinh - Trình đọc tài liệu | Sử dụng pyttsx3 & Streamlit</p>
        <p>Chức năng: Đọc toàn bộ tài liệu • Highlight phần đang đọc • Điều chỉnh âm lượng/tốc độ • Thống kê</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()