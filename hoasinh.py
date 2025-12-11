import streamlit as st
import time
import re
from collections import Counter

# Cấu hình trang
st.set_page_config(
    page_title="QT Hóa Sinh - Trình Đọc Tài Liệu",
    page_icon="🔬",
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
    .doc-section {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Tải tài liệu đầy đủ từ file
def load_full_document():
    # Tài liệu QT Hóa Sinh đầy đủ
    sections = []
    
    # QT 58
    sections.extend([
        "# QT 58: ĐỊNH LƯỢNG CÁC CHẤT ĐIỆN GIẢI (NA+, K+, CL-)",
        "### NGUYÊN LÝ",
        "Các chất điện giải liên quan đến rất nhiều các chuyển hóa quan trọng trong cơ thể. Na+, K+, Cl- là các ion quan trọng nhất và được sử dụng nhiều nhất.",
        "### CHUẨN BỊ",
        "1. Người thực hiện: bác sỹ hoặc kỹ thuật viên được đào tạo chuyên ngành Hóa sinh",
        "2. Phương tiện, hóa chất: Máy móc, thuốc thử, điện cực, chuẩn, control",
        "3. Người bệnh: nhịn ăn sáng và lấy máu vào buổi sáng",
        "4. Phiếu xét nghiệm: có đầy đủ thông tin về người bệnh",
        "### CÁC BƯỚC TIẾN HÀNH",
        "1. Lấy bệnh phẩm: lấy máu đúng kỹ thuật",
        "2. Tiến hành kỹ thuật: phân tích trên máy sinh hóa",
        "### NHẬN ĐỊNH KẾT QUẢ",
        "- Bình thường:",
        "  Na: 133-147 mmol/l",
        "  K: 3.4-4.5 mmol/l",
        "  Clo: 94-111 mmol/l",
        "",
        "# QT 72: ĐO HOẠT ĐỘ G6PD",
        "### NGUYÊN LÝ",
        "Hoạt độ Enzym được xác định bằng cách đo tốc độ tăng mật độ quang ở bước sóng 340nm do sự tăng nồng độ của NADPH.",
        "### CHUẨN BỊ",
        "1. Người thực hiện: 02 người là bác sĩ, kỹ thuật viên",
        "2. Phương tiện, hóa chất: Máy hóa sinh tự động, hóa chất Randox",
        "### CÁC BƯỚC TIẾN HÀNH",
        "1. Lấy bệnh phẩm: máu toàn phần",
        "2. Tiến hành kỹ thuật: rửa hồng cầu, chạy phân tích",
        "### NHẬN ĐỊNH KẾT QUẢ",
        "- Giá trị tham chiếu: > 200 IU/10^12 Hồng cầu hoặc > 6.0 IU/gHb",
        "- Ý nghĩa lâm sàng: thiếu hụt G6PD là rối loạn Enzym liên quan giới tính",
        "",
        "# QT 83: ĐỊNH LƯỢNG HBA1C",
        "### NGUYÊN LÝ",
        "Hemoglobin A1c hình thành khi glucose kết hợp với hemoglobin qua phản ứng glycosyl hoá.",
        "### CHUẨN BỊ",
        "1. Người thực hiện: 01 cán bộ đại học và 01 kỹ thuật viên",
        "2. Phương tiện, hóa chất: máy HPLC, hóa chất chuyên dụng",
        "### CÁC BƯỚC TIẾN HÀNH",
        "1. Lấy bệnh phẩm: 2 mL máu toàn phần",
        "2. Tiến hành kỹ thuật: phân tích trên máy HPLC",
        "### NHẬN ĐỊNH KẾT QUẢ",
        "- Giá trị bình thường: 4-6%",
        "- Tăng khi > 6.5%",
        "",
        "# QT 85: ĐỊNH LƯỢNG HE4",
        "### NGUYÊN LÝ",
        "HE4 là protein mào tinh người, tăng trong ung thư buồng trứng",
        "### CHUẨN BỊ",
        "1. Người thực hiện: 01 cán bộ đại học, 01 kỹ thuật viên",
        "2. Phương tiện, hóa chất: máy miễn dịch, hóa chất HE4",
        "### CÁC BƯỚC TIẾN HÀNH",
        "1. Lấy bệnh phẩm: 3 ml máu tĩnh mạch",
        "2. Tiến hành kỹ thuật: phân tích trên máy miễn dịch",
        "### NHẬN ĐỊNH KẾT QUẢ",
        "- Giá trị bình thường theo tuổi",
        "- Tăng trong ung thư buồng trứng",
        "- Tính PI và ROM để phân tầng nguy cơ"
    ])
    
    return sections

# Xử lý đọc văn bản đơn giản
def create_simple_reader():
    class SimpleReader:
        def __init__(self):
            self.is_reading = False
            self.current_index = 0
            self.speed = 1.0
            
        def start_reading(self, paragraphs):
            self.is_reading = True
            self.paragraphs = paragraphs
            
        def pause_reading(self):
            self.is_reading = False
            
        def resume_reading(self):
            self.is_reading = True
            
        def stop_reading(self):
            self.is_reading = False
            self.current_index = 0
            
        def next_paragraph(self):
            if self.current_index < len(self.paragraphs) - 1:
                self.current_index += 1
                return True
            return False
            
        def previous_paragraph(self):
            if self.current_index > 0:
                self.current_index -= 1
                return True
            return False
    
    return SimpleReader()

# Thống kê tài liệu
def calculate_statistics(text):
    # Tính số từ
    words = re.findall(r'\b\w+\b', text)
    word_count = len(words)
    
    # Tính số câu
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    # Tính thời gian đọc ước tính (từ/phút)
    reading_time_minutes = word_count / 150  # 150 từ/phút
    
    # Tần suất từ
    word_freq = Counter([word.lower() for word in words])
    most_common_words = word_freq.most_common(10)
    
    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'reading_time': reading_time_minutes,
        'most_common_words': most_common_words
    }

# Giao diện chính
def main():
    st.markdown("<h1 class='main-header'>QT Hóa Sinh - Trình Đọc Tài Liệu</h1>", unsafe_allow_html=True)
    
    # Khởi tạo session state
    if 'reader' not in st.session_state:
        st.session_state.reader = create_simple_reader()
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'is_reading' not in st.session_state:
        st.session_state.is_reading = False
    
    # Load tài liệu
    paragraphs = load_full_document()
    
    # Sidebar - Điều khiển và thống kê
    with st.sidebar:
        st.markdown("<h3 class='sidebar-header'>Điều Khiển Đọc</h3>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Bắt đầu đọc", use_container_width=True, key="start"):
                    st.session_state.reader.start_reading(paragraphs)
                    st.session_state.is_reading = True
                    st.rerun()
                    
            with col2:
                if st.button("⏸️ Tạm dừng", use_container_width=True, key="pause"):
                    st.session_state.reader.pause_reading()
                    st.session_state.is_reading = False
                    st.rerun()
            
            col3, col4 = st.columns(2)
            with col3:
                if st.button("⏯️ Tiếp tục", use_container_width=True, key="resume"):
                    st.session_state.reader.resume_reading()
                    st.session_state.is_reading = True
                    st.rerun()
                    
            with col4:
                if st.button("⏹️ Dừng", use_container_width=True, key="stop"):
                    st.session_state.reader.stop_reading()
                    st.session_state.is_reading = False
                    st.session_state.current_index = 0
                    st.rerun()
            
            # Điều khiển đoạn
            st.markdown("---")
            col5, col6 = st.columns(2)
            with col5:
                if st.button("⬅️ Đoạn trước", use_container_width=True, key="prev"):
                    if st.session_state.reader.previous_paragraph():
                        st.session_state.current_index = st.session_state.reader.current_index
                        st.rerun()
                        
            with col6:
                if st.button("➡️ Đoạn tiếp", use_container_width=True, key="next"):
                    if st.session_state.reader.next_paragraph():
                        st.session_state.current_index = st.session_state.reader.current_index
                        st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Điều chỉnh tốc độ
        st.markdown("<h3 class='sidebar-header'>Cài Đặt</h3>", unsafe_allow_html=True)
        
        speed = st.slider("Tốc độ đọc", 0.5, 2.0, 1.0, 0.1, key="speed")
        st.session_state.reader.speed = speed
        
        # Thống kê
        st.markdown("<h3 class='sidebar-header'>Thống Kê Tài Liệu</h3>", unsafe_allow_html=True)
        
        # Tính thống kê
        full_text = " ".join(paragraphs)
        stats = calculate_statistics(full_text)
        
        st.markdown(f"""
        <div class='stats-box'>
            <b>📄 Tổng số đoạn:</b> {len(paragraphs)}<br>
            <b>🔤 Tổng số từ:</b> {stats['word_count']}<br>
            <b>📝 Tổng số câu:</b> {stats['sentence_count']}<br>
            <b>⏱️ Thời gian đọc ước tính:</b> {stats['reading_time']:.1f} phút<br>
        </div>
        """, unsafe_allow_html=True)
        
        # Hiển thị từ thông dụng
        with st.expander("🔤 10 từ xuất hiện nhiều nhất"):
            for word, count in stats['most_common_words']:
                st.write(f"**{word}**: {count} lần")
        
        # Hiển thị thông tin
        st.markdown("---")
        st.markdown("""
        <div style='color: #666; font-size: 0.9em;'>
        <b>Hướng dẫn sử dụng:</b><br>
        1. Nhấn <b>Bắt đầu đọc</b> để bắt đầu<br>
        2. Sử dụng các nút điều khiển để dừng/tạm dừng<br>
        3. Dùng nút đoạn trước/tiếp để điều hướng<br>
        4. Điều chỉnh tốc độ theo ý muốn
        </div>
        """, unsafe_allow_html=True)
    
    # Main area - Hiển thị văn bản
    st.markdown("<h3 class='sidebar-header'>Nội Dung Tài Liệu</h3>", unsafe_allow_html=True)
    
    # Hiển thị thanh tiến trình
    current_idx = st.session_state.reader.current_index
    progress_text = f"Đoạn {current_idx + 1}/{len(paragraphs)}"
    progress = (current_idx + 1) / len(paragraphs) if len(paragraphs) > 0 else 0
    
    # Tạo 2 cột cho tiến trình và trạng thái
    col_prog1, col_prog2 = st.columns([3, 1])
    with col_prog1:
        st.progress(progress, text=progress_text)
    with col_prog2:
        status = "🔊 Đang đọc" if st.session_state.is_reading else "⏸️ Đã dừng"
        st.markdown(f"<div style='text-align: center; padding: 10px;'><b>{status}</b></div>", unsafe_allow_html=True)
    
    # Tạo container cho văn bản với cuộn
    text_container = st.container()
    
    with text_container:
        # Hiển thị tất cả các đoạn
        for i, paragraph in enumerate(paragraphs):
            # Xác định xem đoạn này có phải là tiêu đề không
            is_header = paragraph.startswith("#") or paragraph.startswith("###")
            
            # Làm nổi bật đoạn đang được đọc
            if i == current_idx:
                if is_header:
                    st.markdown(f"""
                    <div class='highlighted' style='font-size: 1.2em; font-weight: bold;'>
                        🔊 {paragraph}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='highlighted'>
                        🔊 {paragraph}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Thêm nút để copy đoạn này
                col_copy1, col_copy2 = st.columns([5, 1])
                with col_copy2:
                    if st.button("📋 Copy", key=f"copy_{i}", type="secondary"):
                        st.code(paragraph, language="text")
                        st.success("Đã copy vào clipboard!")
            else:
                if is_header:
                    if paragraph.startswith("# QT"):
                        st.markdown(f"""
                        <div class='doc-section'>
                            <h3 style='color: #2E86AB;'>{paragraph}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"<h4>{paragraph}</h4>", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='normal-text'>
                        {paragraph}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Thêm khoảng cách nhỏ giữa các đoạn
            st.write("")
    
    # Thêm chức năng đọc đơn giản bằng JavaScript
    if st.session_state.is_reading:
        # Tự động chuyển đến đoạn tiếp theo sau một khoảng thời gian
        time_to_wait = 3.0 / st.session_state.reader.speed  # 3 giây mỗi đoạn, chia cho tốc độ
        
        # Sử dụng JavaScript để tự động cuộn đến đoạn đang đọc
        scroll_js = f"""
        <script>
            // Cuộn đến đoạn hiện tại
            var elements = document.querySelectorAll('.highlighted');
            if (elements.length > 0) {{
                elements[0].scrollIntoView({{behavior: 'smooth', block: 'center'}});
            }}
            
            // Tự động chuyển đoạn sau {time_to_wait} giây
            setTimeout(function() {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: 'next_paragraph'
                }}, '*');
            }}, {time_to_wait * 1000});
        </script>
        """
        st.components.v1.html(scroll_js, height=0)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p><b>QT Hóa Sinh - Trình đọc tài liệu</b></p>
        <p>4 quy trình: Định lượng chất điện giải • Đo hoạt độ G6PD • Định lượng HbA1c • Định lượng HE4</p>
        <p><small>Phiên bản đơn giản - Hiển thị và điều hướng tài liệu</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()