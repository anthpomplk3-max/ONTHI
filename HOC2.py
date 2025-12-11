import streamlit as st
import tempfile
import os
import json
from pathlib import Path
import base64
import hashlib
import time

# Cấu hình trang
st.set_page_config(
    page_title="Học Tập Y Khoa - Lưu Trữ File",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh
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
    .file-manager {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        border: 2px dashed #dee2e6;
    }
    .file-item {
        background: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        border-left: 5px solid #007bff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .file-icon {
        font-size: 24px;
        margin-right: 10px;
    }
    .delete-btn {
        background: #dc3545;
        color: white;
        border: none;
        padding: 5px 15px;
        border-radius: 5px;
        cursor: pointer;
    }
    .upload-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        border: 2px dashed #6c757d;
    }
    .storage-info {
        background: #28a745;
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .share-link {
        background: #17a2b8;
        color: white;
        padding: 10px;
        border-radius: 5px;
        word-break: break-all;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo session state
def init_session_state():
    if 'huyet_hoc_files' not in st.session_state:
        st.session_state.huyet_hoc_files = {'doc': [], 'audio': []}
    if 'hoa_sinh_files' not in st.session_state:
        st.session_state.hoa_sinh_files = {'doc': [], 'audio': []}
    if 'file_storage' not in st.session_state:
        st.session_state.file_storage = {}
    if 'share_key' not in st.session_state:
        # Tạo key duy nhất cho phiên hiện tại
        st.session_state.share_key = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

# Khởi tạo
init_session_state()

# Hàm lưu file vào storage
def save_file(uploaded_file, category, subject):
    """Lưu file vào session storage"""
    if uploaded_file is not None:
        # Tạo ID duy nhất cho file
        file_id = hashlib.md5(
            f"{uploaded_file.name}_{uploaded_file.size}_{time.time()}".encode()
        ).hexdigest()[:12]
        
        # Lưu file info
        file_info = {
            'id': file_id,
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'type': uploaded_file.type,
            'category': category,  # 'doc' hoặc 'audio'
            'subject': subject,  # 'huyet_hoc' hoặc 'hoa_sinh'
            'timestamp': time.time(),
            'data': base64.b64encode(uploaded_file.getvalue()).decode()
        }
        
        # Lưu vào storage
        st.session_state.file_storage[file_id] = file_info
        
        # Thêm vào danh sách file của môn học
        if subject == 'huyet_hoc':
            st.session_state.huyet_hoc_files[category].append(file_id)
        else:
            st.session_state.hoa_sinh_files[category].append(file_id)
        
        return file_info

# Hàm xóa file
def delete_file(file_id):
    """Xóa file khỏi storage"""
    if file_id in st.session_state.file_storage:
        file_info = st.session_state.file_storage[file_id]
        category = file_info['category']
        subject = file_info['subject']
        
        # Xóa khỏi danh sách môn học
        if subject == 'huyet_hoc':
            if file_id in st.session_state.huyet_hoc_files[category]:
                st.session_state.huyet_hoc_files[category].remove(file_id)
        else:
            if file_id in st.session_state.hoa_sinh_files[category]:
                st.session_state.hoa_sinh_files[category].remove(file_id)
        
        # Xóa khỏi storage
        del st.session_state.file_storage[file_id]
        return True
    return False

# Hàm tải file từ storage
def load_file(file_id):
    """Tải file từ storage"""
    if file_id in st.session_state.file_storage:
        file_info = st.session_state.file_storage[file_id]
        file_data = base64.b64decode(file_info['data'])
        
        # Tạo file object
        import io
        return io.BytesIO(file_data)
    return None

# Hàm tạo share link
def create_share_link():
    """Tạo link chia sẻ với tất cả file"""
    # Tạo dữ liệu chia sẻ
    share_data = {
        'huyet_hoc_files': st.session_state.huyet_hoc_files,
        'hoa_sinh_files': st.session_state.hoa_sinh_files,
        'file_storage': st.session_state.file_storage,
        'timestamp': time.time()
    }
    
    # Mã hóa thành JSON string
    import json
    json_str = json.dumps(share_data)
    
    # Mã hóa base64 để dễ chia sẻ
    encoded = base64.b64encode(json_str.encode()).decode()
    
    # Tạo URL
    base_url = st.experimental_get_query_params().get('base_url', [''])[0]
    if not base_url:
        base_url = st.experimental_get_query_params().get('url', [''])[0]
    
    if base_url:
        share_url = f"{base_url}?shared={encoded}"
    else:
        share_url = f"?shared={encoded}"
    
    return share_url

# Hàm import dữ liệu chia sẻ
def import_shared_data(shared_data):
    """Import dữ liệu từ link chia sẻ"""
    try:
        data = json.loads(shared_data)
        
        # Cập nhật session state
        st.session_state.huyet_hoc_files = data.get('huyet_hoc_files', {'doc': [], 'audio': []})
        st.session_state.hoa_sinh_files = data.get('hoa_sinh_files', {'doc': [], 'audio': []})
        st.session_state.file_storage = data.get('file_storage', {})
        
        st.success("Đã nhập dữ liệu chia sẻ thành công!")
        return True
    except:
        st.error("Không thể nhập dữ liệu chia sẻ")
        return False

# Kiểm tra nếu có dữ liệu chia sẻ trong URL
query_params = st.experimental_get_query_params()
if 'shared' in query_params:
    shared_encoded = query_params['shared'][0]
    try:
        shared_data = base64.b64decode(shared_encoded).decode()
        if st.button("Nhập dữ liệu chia sẻ"):
            import_shared_data(shared_data)
    except:
        pass

# Header
st.markdown('''
<div class="main-header">
    <h1>📚 HỆ THỐNG HỌC TẬP Y KHOA</h1>
    <h3>Lưu trữ & Chia sẻ File - Huyết học & Hóa sinh</h3>
</div>
''', unsafe_allow_html=True)

# Sidebar với thông tin storage
with st.sidebar:
    st.markdown("### 💾 LƯU TRỮ")
    
    # Tính toán tổng dung lượng
    total_size = sum(file['size'] for file in st.session_state.file_storage.values())
    total_size_mb = total_size / (1024 * 1024)
    
    st.metric("Tổng dung lượng", f"{total_size_mb:.2f} MB")
    st.metric("Tổng số file", len(st.session_state.file_storage))
    
    # Chia sẻ dữ liệu
    st.markdown("---")
    st.markdown("### 🔗 CHIA SẺ")
    
    if st.button("Tạo link chia sẻ"):
        share_link = create_share_link()
        st.markdown('<div class="share-link">', unsafe_allow_html=True)
        st.text(share_link)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Copy to clipboard
        st.code(share_link, language="text")
    
    st.markdown("---")
    st.markdown("### ⚙️ QUẢN LÝ")
    
    if st.button("Xóa tất cả file"):
        st.session_state.huyet_hoc_files = {'doc': [], 'audio': []}
        st.session_state.hoa_sinh_files = {'doc': [], 'audio': []}
        st.session_state.file_storage = {}
        st.success("Đã xóa tất cả file!")
    
    st.markdown("---")
    st.markdown("### 📊 THỐNG KÊ")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Huyết học", f"{len(st.session_state.huyet_hoc_files['doc'])} docs, {len(st.session_state.huyet_hoc_files['audio'])} audio")
    with col2:
        st.metric("Hóa sinh", f"{len(st.session_state.hoa_sinh_files['doc'])} docs, {len(st.session_state.hoa_sinh_files['audio'])} audio")

# Tạo tabs
tab1, tab2 = st.tabs(["🔬 **HUYẾT HỌC**", "🧪 **HÓA SINH**"])

with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2c3e50;'>📚 HUYẾT HỌC - Quản lý File</h2>", unsafe_allow_html=True)
    
    # Phần tải lên file mới
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("### 📤 TẢI LÊN FILE MỚI")
    
    col_upload1, col_upload2 = st.columns(2)
    
    with col_upload1:
        st.markdown("#### 📄 File tài liệu (.docx, .pdf, .txt)")
        new_doc = st.file_uploader(
            "Chọn file tài liệu",
            type=['docx', 'pdf', 'txt', 'doc'],
            key="huyethoc_new_doc"
        )
        if new_doc and st.button("Lưu file tài liệu", key="save_huyethoc_doc"):
            file_info = save_file(new_doc, 'doc', 'huyet_hoc')
            if file_info:
                st.success(f"Đã lưu file: {file_info['name']}")
    
    with col_upload2:
        st.markdown("#### 🎵 File âm thanh (.mp3, .wav, .ogg)")
        new_audio = st.file_uploader(
            "Chọn file âm thanh",
            type=['mp3', 'wav', 'ogg', 'm4a'],
            key="huyethoc_new_audio"
        )
        if new_audio and st.button("Lưu file âm thanh", key="save_huyethoc_audio"):
            file_info = save_file(new_audio, 'audio', 'huyet_hoc')
            if file_info:
                st.success(f"Đã lưu file: {file_info['name']}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Hiển thị danh sách file đã lưu
    st.markdown('<div class="file-manager">', unsafe_allow_html=True)
    st.markdown("### 📁 FILE ĐÃ LƯU")
    
    # File tài liệu
    st.markdown("#### 📄 Tài liệu đã lưu")
    if st.session_state.huyet_hoc_files['doc']:
        for file_id in st.session_state.huyet_hoc_files['doc']:
            if file_id in st.session_state.file_storage:
                file_info = st.session_state.file_storage[file_id]
                col1, col2, col3 = st.columns([6, 2, 1])
                with col1:
                    st.markdown(f"""
                    <div style='padding: 10px;'>
                        <span class='file-icon'>📄</span>
                        <strong>{file_info['name']}</strong><br>
                        <small>Kích thước: {file_info['size'] / 1024:.1f} KB</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("Tải xuống", key=f"download_doc_{file_id}"):
                        file_data = load_file(file_id)
                        if file_data:
                            st.download_button(
                                label="Click để tải",
                                data=file_data,
                                file_name=file_info['name'],
                                mime=file_info['type'],
                                key=f"dl_{file_id}"
                            )
                with col3:
                    if st.button("🗑️", key=f"delete_doc_{file_id}"):
                        if delete_file(file_id):
                            st.success("Đã xóa file!")
                            st.rerun()
    else:
        st.info("Chưa có file tài liệu nào")
    
    st.markdown("---")
    
    # File âm thanh
    st.markdown("#### 🎵 Âm thanh đã lưu")
    if st.session_state.huyet_hoc_files['audio']:
        for file_id in st.session_state.huyet_hoc_files['audio']:
            if file_id in st.session_state.file_storage:
                file_info = st.session_state.file_storage[file_id]
                col1, col2, col3 = st.columns([6, 2, 1])
                with col1:
                    st.markdown(f"""
                    <div style='padding: 10px;'>
                        <span class='file-icon'>🎵</span>
                        <strong>{file_info['name']}</strong><br>
                        <small>Kích thước: {file_info['size'] / 1024:.1f} KB</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("Nghe", key=f"play_audio_{file_id}"):
                        file_data = load_file(file_id)
                        if file_data:
                            st.audio(file_data, format=file_info['type'].split('/')[-1])
                with col3:
                    if st.button("🗑️", key=f"delete_audio_{file_id}"):
                        if delete_file(file_id):
                            st.success("Đã xóa file!")
                            st.rerun()
    else:
        st.info("Chưa có file âm thanh nào")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Player và xem file
    if st.session_state.huyet_hoc_files['doc'] or st.session_state.huyet_hoc_files['audio']:
        st.markdown("### 🎧 NGHE VÀ XEM")
        
        col_play1, col_play2 = st.columns(2)
        
        with col_play1:
            st.markdown("#### Chọn file âm thanh để nghe")
            audio_files = [st.session_state.file_storage[fid] for fid in st.session_state.huyet_hoc_files['audio'] 
                          if fid in st.session_state.file_storage]
            if audio_files:
                audio_options = {f['name']: f['id'] for f in audio_files}
                selected_audio = st.selectbox("Chọn file âm thanh", list(audio_options.keys()))
                if selected_audio:
                    file_id = audio_options[selected_audio]
                    file_data = load_file(file_id)
                    if file_data:
                        st.audio(file_data, format=st.session_state.file_storage[file_id]['type'].split('/')[-1])
            else:
                st.info("Chưa có file âm thanh")
        
        with col_play2:
            st.markdown("#### Chọn file tài liệu để xem")
            doc_files = [st.session_state.file_storage[fid] for fid in st.session_state.huyet_hoc_files['doc'] 
                        if fid in st.session_state.file_storage]
            if doc_files:
                doc_options = {f['name']: f['id'] for f in doc_files}
                selected_doc = st.selectbox("Chọn file tài liệu", list(doc_options.keys()))
                if selected_doc:
                    file_id = doc_options[selected_doc]
                    file_data = load_file(file_id)
                    if file_data:
                        # Hiển thị nội dung tùy theo loại file
                        file_info = st.session_state.file_storage[file_id]
                        if file_info['name'].endswith('.txt'):
                            content = file_data.getvalue().decode('utf-8')
                            st.text_area("Nội dung", content, height=200)
                        else:
                            st.download_button(
                                "Tải xuống để xem",
                                file_data,
                                file_info['name'],
                                key=f"view_{file_id}"
                            )
            else:
                st.info("Chưa có file tài liệu")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2c3e50;'>🧬 HÓA SINH - Quản lý File</h2>", unsafe_allow_html=True)
    
    # Phần tải lên file mới
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("### 📤 TẢI LÊN FILE MỚI")
    
    col_upload1, col_upload2 = st.columns(2)
    
    with col_upload1:
        st.markdown("#### 📄 File tài liệu (.docx, .pdf, .txt)")
        new_doc = st.file_uploader(
            "Chọn file tài liệu",
            type=['docx', 'pdf', 'txt', 'doc'],
            key="hoasinh_new_doc"
        )
        if new_doc and st.button("Lưu file tài liệu", key="save_hoasinh_doc"):
            file_info = save_file(new_doc, 'doc', 'hoa_sinh')
            if file_info:
                st.success(f"Đã lưu file: {file_info['name']}")
    
    with col_upload2:
        st.markdown("#### 🎵 File âm thanh (.mp3, .wav, .ogg)")
        new_audio = st.file_uploader(
            "Chọn file âm thanh",
            type=['mp3', 'wav', 'ogg', 'm4a'],
            key="hoasinh_new_audio"
        )
        if new_audio and st.button("Lưu file âm thanh", key="save_hoasinh_audio"):
            file_info = save_file(new_audio, 'audio', 'hoa_sinh')
            if file_info:
                st.success(f"Đã lưu file: {file_info['name']}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Hiển thị danh sách file đã lưu
    st.markdown('<div class="file-manager">', unsafe_allow_html=True)
    st.markdown("### 📁 FILE ĐÃ LƯU")
    
    # File tài liệu
    st.markdown("#### 📄 Tài liệu đã lưu")
    if st.session_state.hoa_sinh_files['doc']:
        for file_id in st.session_state.hoa_sinh_files['doc']:
            if file_id in st.session_state.file_storage:
                file_info = st.session_state.file_storage[file_id]
                col1, col2, col3 = st.columns([6, 2, 1])
                with col1:
                    st.markdown(f"""
                    <div style='padding: 10px;'>
                        <span class='file-icon'>📄</span>
                        <strong>{file_info['name']}</strong><br>
                        <small>Kích thước: {file_info['size'] / 1024:.1f} KB</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("Tải xuống", key=f"download_doc_hs_{file_id}"):
                        file_data = load_file(file_id)
                        if file_data:
                            st.download_button(
                                label="Click để tải",
                                data=file_data,
                                file_name=file_info['name'],
                                mime=file_info['type'],
                                key=f"dl_hs_{file_id}"
                            )
                with col3:
                    if st.button("🗑️", key=f"delete_doc_hs_{file_id}"):
                        if delete_file(file_id):
                            st.success("Đã xóa file!")
                            st.rerun()
    else:
        st.info("Chưa có file tài liệu nào")
    
    st.markdown("---")
    
    # File âm thanh
    st.markdown("#### 🎵 Âm thanh đã lưu")
    if st.session_state.hoa_sinh_files['audio']:
        for file_id in st.session_state.hoa_sinh_files['audio']:
            if file_id in st.session_state.file_storage:
                file_info = st.session_state.file_storage[file_id]
                col1, col2, col3 = st.columns([6, 2, 1])
                with col1:
                    st.markdown(f"""
                    <div style='padding: 10px;'>
                        <span class='file-icon'>🎵</span>
                        <strong>{file_info['name']}</strong><br>
                        <small>Kích thước: {file_info['size'] / 1024:.1f} KB</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("Nghe", key=f"play_audio_hs_{file_id}"):
                        file_data = load_file(file_id)
                        if file_data:
                            st.audio(file_data, format=file_info['type'].split('/')[-1])
                with col3:
                    if st.button("🗑️", key=f"delete_audio_hs_{file_id}"):
                        if delete_file(file_id):
                            st.success("Đã xóa file!")
                            st.rerun()
    else:
        st.info("Chưa có file âm thanh nào")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Player và xem file
    if st.session_state.hoa_sinh_files['doc'] or st.session_state.hoa_sinh_files['audio']:
        st.markdown("### 🎧 NGHE VÀ XEM")
        
        col_play1, col_play2 = st.columns(2)
        
        with col_play1:
            st.markdown("#### Chọn file âm thanh để nghe")
            audio_files = [st.session_state.file_storage[fid] for fid in st.session_state.hoa_sinh_files['audio'] 
                          if fid in st.session_state.file_storage]
            if audio_files:
                audio_options = {f['name']: f['id'] for f in audio_files}
                selected_audio = st.selectbox("Chọn file âm thanh", list(audio_options.keys()), key="audio_hs")
                if selected_audio:
                    file_id = audio_options[selected_audio]
                    file_data = load_file(file_id)
                    if file_data:
                        st.audio(file_data, format=st.session_state.file_storage[file_id]['type'].split('/')[-1], key="player_hs")
            else:
                st.info("Chưa có file âm thanh")
        
        with col_play2:
            st.markdown("#### Chọn file tài liệu để xem")
            doc_files = [st.session_state.file_storage[fid] for fid in st.session_state.hoa_sinh_files['doc'] 
                        if fid in st.session_state.file_storage]
            if doc_files:
                doc_options = {f['name']: f['id'] for f in doc_files}
                selected_doc = st.selectbox("Chọn file tài liệu", list(doc_options.keys()), key="doc_hs")
                if selected_doc:
                    file_id = doc_options[selected_doc]
                    file_data = load_file(file_id)
                    if file_data:
                        file_info = st.session_state.file_storage[file_id]
                        if file_info['name'].endswith('.txt'):
                            content = file_data.getvalue().decode('utf-8')
                            st.text_area("Nội dung", content, height=200, key="content_hs")
                        else:
                            st.download_button(
                                "Tải xuống để xem",
                                file_data,
                                file_info['name'],
                                key=f"view_hs_{file_id}"
                            )
            else:
                st.info("Chưa có file tài liệu")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Hướng dẫn sử dụng
with st.expander("📘 **HƯỚNG DẪN SỬ DỤNG**"):
    st.markdown("""
    ## 🚀 **CÁCH SỬ DỤNG HỆ THỐNG LƯU TRỮ FILE**
    
    ### **1. TẢI FILE LÊN**
    - Mỗi tab (Huyết học/Hóa sinh) có phần tải file riêng
    - Có thể tải nhiều file cùng loại
    - Hỗ trợ file tài liệu: .docx, .pdf, .txt, .doc
    - Hỗ trợ file âm thanh: .mp3, .wav, .ogg, .m4a
    
    ### **2. QUẢN LÝ FILE**
    - **Xem danh sách**: Tất cả file đã tải hiển thị trong danh sách
    - **Xóa file**: Nhấn nút 🗑️ để xóa file không cần thiết
    - **Tải xuống**: Nhấn "Tải xuống" để lấy file về máy
    - **Nghe trực tiếp**: Nhấn "Nghe" để phát file âm thanh
    
    ### **3. CHIA SẺ DỮ LIỆU**
    - **Tạo link chia sẻ**: Nhấn "Tạo link chia sẻ" trong sidebar
    - **Chia sẻ link**: Gửi link cho người khác
    - **Nhập dữ liệu**: Khi mở link chia sẻ, hệ thống tự động đề xuất nhập dữ liệu
    
    ### **4. LƯU Ý QUAN TRỌNG**
    - Dữ liệu được lưu trong phiên làm việc hiện tại
    - Khi tạo link chia sẻ, tất cả file được đóng gói vào link
    - Link có thể dài, hãy dùng dịch vụ rút gọn link nếu cần
    - Dung lượng tối đa khuyến nghị: 100MB
    
    ### **5. BẢO MẬT**
    - File được mã hóa trong link chia sẻ
    - Chỉ người có link mới xem được file
    - Không lưu trữ file trên server lâu dài
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>💾 Hệ thống lưu trữ file học tập y khoa - Phiên bản 3.0</p>
        <p>🔗 Chia sẻ dữ liệu dễ dàng • Không cần đăng nhập</p>
        <p style='font-size: 12px; margin-top: 10px;'>
            Mã phiên: <strong>{}</strong> • Dung lượng: {:.2f} MB
        </p>
    </div>
    """.format(st.session_state.share_key, total_size_mb), 
    unsafe_allow_html=True
)