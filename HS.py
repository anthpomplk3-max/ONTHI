import tkinter as tk
from tkinter import ttk, filedialog
import pygame
import os
import threading
import time

class AudioBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QT Audio Player")
        self.root.geometry("900x700")
        
        # Khởi tạo pygame mixer
        pygame.mixer.init()
        
        # Biến lưu trữ
        self.current_audio = None
        self.current_text_file = None
        self.text_lines = []
        self.is_playing = False
        self.current_position = 0
        self.audio_length = 0
        self.play_thread = None
        self.highlight_index = -1
        
        # Cấu hình style
        self.setup_styles()
        
        # Tạo giao diện
        self.create_widgets()
        
        # Tải danh sách file
        self.load_file_list()
        
    def setup_styles(self):
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Highlight.TLabel", 
                       background="yellow", 
                       relief="solid", 
                       borderwidth=1)
        
    def create_widgets(self):
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text="QT Audio Player", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame chọn file
        file_frame = ttk.LabelFrame(main_frame, text="Chọn File Âm Thanh", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Nút chọn file
        self.qt58_btn = ttk.Button(file_frame, text="QT 58", command=lambda: self.load_files(58))
        self.qt58_btn.grid(row=0, column=0, padx=5)
        
        self.qt72_btn = ttk.Button(file_frame, text="QT 72", command=lambda: self.load_files(72))
        self.qt72_btn.grid(row=0, column=1, padx=5)
        
        self.qt83_btn = ttk.Button(file_frame, text="QT 83", command=lambda: self.load_files(83))
        self.qt83_btn.grid(row=0, column=2, padx=5)
        
        self.qt85_btn = ttk.Button(file_frame, text="QT 85", command=lambda: self.load_files(85))
        self.qt85_btn.grid(row=0, column=3, padx=5)
        
        # Frame hiển thị file đang chọn
        self.current_file_label = ttk.Label(main_frame, text="Chưa chọn file")
        self.current_file_label.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        # Frame điều khiển
        control_frame = ttk.LabelFrame(main_frame, text="Điều Khiển", padding="10")
        control_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Nút điều khiển
        self.play_btn = ttk.Button(control_frame, text="▶ Phát", command=self.play_audio)
        self.play_btn.grid(row=0, column=0, padx=5)
        
        self.pause_btn = ttk.Button(control_frame, text="⏸ Dừng", command=self.pause_audio)
        self.pause_btn.grid(row=0, column=1, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⏹ Dừng hẳn", command=self.stop_audio)
        self.stop_btn.grid(row=0, column=2, padx=5)
        
        # Thanh điều khiển âm lượng
        volume_frame = ttk.Frame(control_frame)
        volume_frame.grid(row=0, column=3, padx=20)
        
        ttk.Label(volume_frame, text="Âm lượng:").grid(row=0, column=0)
        self.volume_scale = ttk.Scale(volume_frame, from_=0, to=100, 
                                     orient=tk.HORIZONTAL, length=150,
                                     command=self.change_volume)
        self.volume_scale.set(70)  # Mức âm lượng mặc định
        self.volume_scale.grid(row=0, column=1)
        
        # Thanh điều khiển tốc độ
        speed_frame = ttk.Frame(control_frame)
        speed_frame.grid(row=0, column=4, padx=20)
        
        ttk.Label(speed_frame, text="Tốc độ:").grid(row=0, column=0)
        self.speed_scale = ttk.Scale(speed_frame, from_=50, to=200, 
                                    orient=tk.HORIZONTAL, length=150,
                                    command=self.change_speed)
        self.speed_scale.set(100)  # Tốc độ mặc định 100%
        self.speed_scale.grid(row=0, column=1)
        
        # Frame hiển thị văn bản
        text_frame = ttk.LabelFrame(main_frame, text="Nội dung", padding="10")
        text_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Thanh cuộn cho text
        text_scrollbar = ttk.Scrollbar(text_frame)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget để hiển thị nội dung
        self.text_display = tk.Text(text_frame, height=20, width=80,
                                   yscrollcommand=text_scrollbar.set,
                                   wrap=tk.WORD, font=("Arial", 11))
        self.text_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.text_display.yview)
        
        # Gắn sự kiện click vào text
        self.text_display.bind("<Button-1>", self.on_text_click)
        
        # Frame thông tin
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.time_label = ttk.Label(info_frame, text="Thời gian: 00:00 / 00:00")
        self.time_label.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(info_frame, text="Trạng thái: Sẵn sàng")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Cấu hình grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
    def load_file_list(self):
        """Tìm các file có sẵn trong thư mục hiện tại"""
        self.available_files = {}
        for num in [58, 72, 83, 85]:
            mp3_file = f"QT {num}.mp3"
            txt_file = f"QT {num}.txt"
            
            if os.path.exists(mp3_file) and os.path.exists(txt_file):
                self.available_files[num] = {
                    'mp3': mp3_file,
                    'txt': txt_file
                }
    
    def load_files(self, file_number):
        """Tải file âm thanh và văn bản tương ứng"""
        if file_number in self.available_files:
            # Dừng audio đang phát
            self.stop_audio()
            
            # Tải file mới
            files = self.available_files[file_number]
            self.current_audio = files['mp3']
            self.current_text_file = files['txt']
            
            # Tải nội dung văn bản
            self.load_text_content()
            
            # Tải audio
            pygame.mixer.music.load(self.current_audio)
            
            # Lấy độ dài audio (ước tính)
            sound = pygame.mixer.Sound(self.current_audio)
            self.audio_length = sound.get_length()
            
            # Cập nhật giao diện
            self.current_file_label.config(
                text=f"Đang chọn: QT {file_number}.mp3 | QT {file_number}.txt"
            )
            self.status_label.config(text="Trạng thái: Đã tải file")
            
            # Đặt lại highlight
            self.highlight_index = -1
            
            # Bật nút play
            self.play_btn.config(state=tk.NORMAL)
            
            # Cập nhật thời gian
            self.update_time_display(0, self.audio_length)
            
    def load_text_content(self):
        """Đọc nội dung file văn bản"""
        self.text_lines = []
        self.text_display.delete(1.0, tk.END)
        
        try:
            with open(self.current_text_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            for i, line in enumerate(lines):
                # Lưu dòng với chỉ số
                self.text_lines.append(line.strip())
                # Hiển thị trong text widget với tag
                self.text_display.insert(tk.END, f"{i+1}. {line}")
                
                # Thêm tag cho dòng (bắt đầu từ 1)
                start_index = f"{i+1}.0"
                end_index = f"{i+1}.end"
                self.text_display.tag_add(f"line_{i}", start_index, end_index)
                
            # Thêm tag highlight
            self.text_display.tag_config("highlight", 
                                        background="yellow",
                                        relief="solid",
                                        borderwidth=1)
        except Exception as e:
            self.text_display.insert(tk.END, f"Lỗi khi đọc file: {str(e)}")
    
    def play_audio(self):
        """Phát âm thanh"""
        if self.current_audio:
            self.is_playing = True
            pygame.mixer.music.play(start=self.current_position)
            self.status_label.config(text="Trạng thái: Đang phát")
            
            # Bắt đầu thread để theo dõi thời gian
            if self.play_thread and self.play_thread.is_alive():
                self.play_thread.join(0.1)
            
            self.play_thread = threading.Thread(target=self.track_playback, daemon=True)
            self.play_thread.start()
            
            # Cập nhật nút
            self.play_btn.config(state=tk.DISABLED)
    
    def pause_audio(self):
        """Tạm dừng âm thanh"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.status_label.config(text="Trạng thái: Đã tạm dừng")
            self.play_btn.config(state=tk.NORMAL)
            self.play_btn.config(text="▶ Tiếp tục")
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.status_label.config(text="Trạng thái: Đang phát")
            self.play_btn.config(state=tk.DISABLED)
            self.play_btn.config(text="▶ Phát")
    
    def stop_audio(self):
        """Dừng hẳn âm thanh"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.current_position = 0
        self.status_label.config(text="Trạng thái: Đã dừng")
        self.play_btn.config(state=tk.NORMAL)
        self.play_btn.config(text="▶ Phát")
        
        # Xóa highlight
        self.remove_highlight()
    
    def change_volume(self, val):
        """Thay đổi âm lượng"""
        volume = float(val) / 100.0
        pygame.mixer.music.set_volume(volume)
    
    def change_speed(self, val):
        """Thay đổi tốc độ phát (giả lập bằng thay đổi vị trí)"""
        # Lưu ý: Pygame không hỗ trợ thay đổi tốc độ trực tiếp
        # Đây là cách giả lập cơ bản
        if self.is_playing:
            # Dừng và phát lại với vị trí được điều chỉnh
            current_pos = pygame.mixer.music.get_pos() / 1000.0  # Chuyển sang giây
            speed_factor = float(val) / 100.0
            
            # Điều chỉnh vị trí dựa trên tốc độ
            adjusted_pos = current_pos * speed_factor
            
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=adjusted_pos)
            self.status_label.config(text=f"Trạng thái: Đang phát (tốc độ: {val}%)")
    
    def track_playback(self):
        """Theo dõi quá trình phát và cập nhật giao diện"""
        while self.is_playing and pygame.mixer.music.get_busy():
            # Lấy vị trí hiện tại (miligiây)
            current_pos = pygame.mixer.music.get_pos() / 1000.0  # Chuyển sang giây
            
            # Cập nhật thời gian
            self.update_time_display(current_pos, self.audio_length)
            
            # Tính toán dòng cần highlight dựa trên thời gian
            if self.text_lines:
                # Giả sử mỗi dòng tương ứng với một khoảng thời gian bằng nhau
                time_per_line = self.audio_length / len(self.text_lines)
                line_index = int(current_pos / time_per_line)
                
                # Giới hạn chỉ số
                line_index = min(line_index, len(self.text_lines) - 1)
                
                # Cập nhật highlight nếu cần
                if line_index >= 0 and line_index != self.highlight_index:
                    self.update_highlight(line_index)
            
            time.sleep(0.1)  # Cập nhật mỗi 0.1 giây
    
    def update_time_display(self, current, total):
        """Cập nhật hiển thị thời gian"""
        current_str = self.format_time(current)
        total_str = self.format_time(total)
        self.time_label.config(text=f"Thời gian: {current_str} / {total_str}")
    
    def format_time(self, seconds):
        """Định dạng thời gian từ giây sang MM:SS"""
        if seconds < 0:
            seconds = 0
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def update_highlight(self, line_index):
        """Cập nhật highlight cho dòng được chọn"""
        # Xóa highlight cũ
        self.remove_highlight()
        
        # Áp dụng highlight mới
        if 0 <= line_index < len(self.text_lines):
            self.highlight_index = line_index
            
            # Tính toán vị trí trong text widget
            line_number = line_index + 1
            start_pos = f"{line_number}.0"
            end_pos = f"{line_number}.end"
            
            # Áp dụng tag highlight
            self.text_display.tag_add("highlight", start_pos, end_pos)
            self.text_display.see(start_pos)  # Cuộn đến dòng được highlight
    
    def remove_highlight(self):
        """Xóa tất cả highlight"""
        self.text_display.tag_remove("highlight", "1.0", tk.END)
    
    def on_text_click(self, event):
        """Xử lý sự kiện click vào văn bản"""
        if not self.current_audio:
            return
        
        # Lấy vị trí click
        index = self.text_display.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0]) - 1  # Chuyển về chỉ số 0-based
        
        if 0 <= line_num < len(self.text_lines):
            # Tính thời gian tương ứng với dòng
            time_per_line = self.audio_length / len(self.text_lines)
            jump_time = line_num * time_per_line
            
            # Nhảy đến thời gian đó
            self.current_position = jump_time
            
            # Nếu đang phát, dừng và phát lại từ vị trí mới
            if self.is_playing:
                pygame.mixer.music.stop()
                pygame.mixer.music.play(start=jump_time)
            else:
                # Chỉ cập nhật highlight
                self.update_highlight(line_num)
            
            # Cập nhật trạng thái
            self.status_label.config(text=f"Trạng thái: Nhảy đến dòng {line_num+1}")
    
    def on_closing(self):
        """Dọn dẹp khi đóng ứng dụng"""
        self.stop_audio()
        pygame.mixer.quit()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AudioBookApp(root)
    
    # Xử lý sự kiện đóng cửa sổ
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()