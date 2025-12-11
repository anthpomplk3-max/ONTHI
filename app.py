import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pygame
import os
import threading
import time

class AudioPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Player with Text Display")
        self.root.geometry("1000x700")
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Variables
        self.audio_files = [
            "QT 5.8.mp3", "QT 7.2.mp3", "QT 8.8.mp3", "QT 8.8.mp3"
        ]
        self.text_files = [
            "QT 5.8.txt", "QT 7.2.txt", "QT 8.8.txt", "QT 8.8.txt"
        ]
        self.current_track = 0
        self.playing = False
        self.paused = False
        self.volume = 0.7
        self.speed = 1.0
        
        # Setup GUI
        self.setup_ui()
        
        # Load first track
        self.load_track(0)
    
    def setup_ui(self):
        # Create main frames
        control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        display_frame = ttk.LabelFrame(self.root, text="Text Display", padding=10)
        display_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Control buttons
        btn_style = ttk.Style()
        btn_style.configure('Control.TButton', font=('Arial', 10))
        
        self.play_btn = ttk.Button(control_frame, text="▶ Play", command=self.play, style='Control.TButton')
        self.play_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.pause_btn = ttk.Button(control_frame, text="⏸ Pause", command=self.pause, style='Control.TButton')
        self.pause_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⏹ Stop", command=self.stop, style='Control.TButton')
        self.stop_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.prev_btn = ttk.Button(control_frame, text="⏮ Previous", command=self.prev_track, style='Control.TButton')
        self.prev_btn.grid(row=0, column=3, padx=5, pady=5)
        
        self.next_btn = ttk.Button(control_frame, text="⏭ Next", command=self.next_track, style='Control.TButton')
        self.next_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # Volume control
        ttk.Label(control_frame, text="Volume:").grid(row=1, column=0, sticky="w", padx=5)
        self.volume_scale = ttk.Scale(control_frame, from_=0, to=100, 
                                      command=self.set_volume, orient="horizontal")
        self.volume_scale.set(70)
        self.volume_scale.grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=10)
        
        # Speed control
        ttk.Label(control_frame, text="Speed:").grid(row=1, column=4, sticky="w", padx=5)
        self.speed_scale = ttk.Scale(control_frame, from_=0.5, to=2.0, 
                                     command=self.set_speed, orient="horizontal")
        self.speed_scale.set(1.0)
        self.speed_scale.grid(row=1, column=5, sticky="ew", padx=5, pady=10)
        
        # Track info
        info_frame = ttk.Frame(control_frame)
        info_frame.grid(row=2, column=0, columnspan=6, sticky="ew", pady=10)
        
        self.track_label = ttk.Label(info_frame, text="Track: 0/0", font=('Arial', 10, 'bold'))
        self.track_label.pack(side="left", padx=10)
        
        self.time_label = ttk.Label(info_frame, text="00:00 / 00:00", font=('Arial', 10))
        self.time_label.pack(side="right", padx=10)
        
        # Track list
        list_frame = ttk.LabelFrame(self.root, text="Playlist", padding=10)
        list_frame.pack(fill="x", padx=10, pady=5)
        
        self.track_listbox = tk.Listbox(list_frame, height=5, font=('Arial', 10))
        self.track_listbox.pack(fill="x", padx=5, pady=5)
        
        for i, (audio, text) in enumerate(zip(self.audio_files, self.text_files)):
            self.track_listbox.insert(tk.END, f"{i+1}. {audio} / {text}")
        
        self.track_listbox.bind('<<ListboxSelect>>', self.on_track_select)
        
        # Text display area
        self.text_display = scrolledtext.ScrolledText(display_frame, 
                                                     wrap=tk.WORD, 
                                                     font=('Arial', 12),
                                                     bg='#f0f0f0',
                                                     padx=10,
                                                     pady=10)
        self.text_display.pack(fill="both", expand=True)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_track(self, index):
        if 0 <= index < len(self.audio_files):
            self.current_track = index
            self.track_listbox.selection_clear(0, tk.END)
            self.track_listbox.selection_set(index)
            self.track_listbox.activate(index)
            
            # Update track info
            self.track_label.config(text=f"Track: {index + 1}/{len(self.audio_files)} - {self.audio_files[index]}")
            
            # Load and display text file
            try:
                text_file = self.text_files[index]
                if os.path.exists(text_file):
                    with open(text_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.text_display.delete(1.0, tk.END)
                    self.text_display.insert(1.0, content)
                    self.status_bar.config(text=f"Loaded: {self.audio_files[index]} and {text_file}")
                else:
                    self.text_display.delete(1.0, tk.END)
                    self.text_display.insert(1.0, f"Text file not found: {text_file}")
                    self.status_bar.config(text=f"Text file not found: {text_file}")
            except Exception as e:
                self.text_display.delete(1.0, tk.END)
                self.text_display.insert(1.0, f"Error loading text file: {str(e)}")
                self.status_bar.config(text=f"Error: {str(e)}")
    
    def play(self):
        if not self.playing:
            try:
                pygame.mixer.music.load(self.audio_files[self.current_track])
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play()
                self.playing = True
                self.paused = False
                self.play_btn.config(text="⏸ Pause", command=self.pause)
                self.status_bar.config(text=f"Playing: {self.audio_files[self.current_track]}")
                
                # Start time update thread
                threading.Thread(target=self.update_time, daemon=True).start()
            except Exception as e:
                messagebox.showerror("Error", f"Could not play audio file: {str(e)}")
        elif self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.play_btn.config(text="⏸ Pause", command=self.pause)
            self.status_bar.config(text=f"Resumed: {self.audio_files[self.current_track]}")
    
    def pause(self):
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.play_btn.config(text="▶ Resume", command=self.play)
            self.status_bar.config(text=f"Paused: {self.audio_files[self.current_track]}")
    
    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.play_btn.config(text="▶ Play", command=self.play)
        self.time_label.config(text="00:00 / 00:00")
        self.status_bar.config(text="Stopped")
    
    def set_volume(self, val):
        self.volume = float(val) / 100
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self.volume)
    
    def set_speed(self, val):
        self.speed = float(val)
        # Note: pygame doesn't natively support speed control
        # This would require a more advanced audio library
        self.status_bar.config(text=f"Speed set to: {self.speed:.1f}x")
    
    def prev_track(self):
        if self.current_track > 0:
            self.stop()
            self.load_track(self.current_track - 1)
            self.play()
    
    def next_track(self):
        if self.current_track < len(self.audio_files) - 1:
            self.stop()
            self.load_track(self.current_track + 1)
            self.play()
    
    def on_track_select(self, event):
        selection = self.track_listbox.curselection()
        if selection:
            index = selection[0]
            if index != self.current_track:
                self.stop()
                self.load_track(index)
    
    def update_time(self):
        while self.playing and pygame.mixer.music.get_busy():
            # Get current position and total length
            # Note: pygame.mixer.music doesn't provide position info directly
            # This is a simplified version
            try:
                pos = pygame.mixer.music.get_pos() / 1000  # Convert to seconds
                if pos >= 0:
                    mins, secs = divmod(int(pos), 60)
                    self.time_label.config(text=f"{mins:02d}:{secs:02d}")
            except:
                pass
            time.sleep(0.5)
    
    def on_closing(self):
        self.stop()
        pygame.mixer.quit()
        self.root.destroy()

def main():
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')
    
    app = AudioPlayerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
