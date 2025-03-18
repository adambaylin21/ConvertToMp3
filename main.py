import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import subprocess
import threading
import time
from tqdm import tqdm
import shutil
from pathlib import Path
import re

class ModernVideoToMP3Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("Chuyển đổi Video sang MP3")
        self.root.geometry("700x600")
        
        # Thiết lập style hiện đại
        self.setup_styles()
        
        # Khởi tạo biến
        self.video_paths = []
        self.output_dir = None
        self.conversion_threads = []
        self.is_converting = False
        
        # Tạo các thành phần giao diện
        self.create_widgets()
        
    def setup_styles(self):
        # Tạo style hiện đại cho ứng dụng
        self.style = ttk.Style()
        
        # Cấu hình style cho các widget
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", font=("Helvetica", 10, "bold"), padding=10)
        self.style.configure("TLabel", font=("Helvetica", 10), background="#f0f0f0")
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), background="#f0f0f0")
        self.style.configure("Status.TLabel", font=("Helvetica", 9), background="#f0f0f0")
        
        # Style cho thanh tiến trình
        self.style.configure("TProgressbar", thickness=20, background="#4CAF50")
        
        # Thiết lập màu nền cho cửa sổ chính
        self.root.configure(background="#f0f0f0")

    def create_widgets(self):
        # Tạo main frame
        main_frame = ttk.Frame(self.root, padding="20 20 20 20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        header_label = ttk.Label(main_frame, text="Chuyển đổi Video sang MP3", style="Header.TLabel")
        header_label.pack(pady=(0, 20))
        
        # Frame chứa các nút chọn file
        file_frame = ttk.Frame(main_frame, style="TFrame")
        file_frame.pack(fill=tk.X, pady=10)
        
        # Nút chọn file video
        self.select_file_button = ttk.Button(
            file_frame,
            text="Chọn File Video",
            command=self.select_videos,
            style="TButton"
        )
        self.select_file_button.pack(side=tk.LEFT, padx=5)
        
        # Nút chọn thư mục video
        self.select_folder_button = ttk.Button(
            file_frame,
            text="Chọn Thư Mục Video",
            command=self.select_video_folder,
            style="TButton"
        )
        self.select_folder_button.pack(side=tk.LEFT, padx=5)
        
        # Nút xóa danh sách
        self.clear_button = ttk.Button(
            file_frame,
            text="Xóa Danh Sách",
            command=self.clear_file_list,
            style="TButton"
        )
        self.clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Frame hiển thị danh sách file
        list_frame = ttk.Frame(main_frame, style="TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Label danh sách file
        file_list_label = ttk.Label(list_frame, text="Danh sách file video:", style="TLabel")
        file_list_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Tạo listbox và scrollbar
        list_container = ttk.Frame(list_frame, style="TFrame")
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.file_listbox = tk.Listbox(
            list_container,
            width=70,
            height=10,
            font=("Helvetica", 9),
            selectmode=tk.EXTENDED,
            bg="white",
            bd=1,
            relief=tk.SOLID
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        # Frame chọn thư mục đầu ra
        output_frame = ttk.Frame(main_frame, style="TFrame")
        output_frame.pack(fill=tk.X, pady=10)
        
        # Nút chọn thư mục đầu ra
        self.output_button = ttk.Button(
            output_frame,
            text="Chọn Thư Mục Lưu File",
            command=self.select_output_dir,
            style="TButton"
        )
        self.output_button.pack(side=tk.LEFT)
        
        # Hiển thị đường dẫn thư mục đầu ra
        self.output_label = ttk.Label(
            output_frame,
            text="Chưa chọn thư mục lưu",
            style="TLabel",
            wraplength=500
        )
        self.output_label.pack(side=tk.LEFT, padx=10)
        
        # Frame chứa thanh tiến trình và trạng thái
        progress_frame = ttk.Frame(main_frame, style="TFrame")
        progress_frame.pack(fill=tk.X, pady=10)
        
        # Label hiển thị file đang xử lý
        self.current_file_label = ttk.Label(
            progress_frame,
            text="",
            style="Status.TLabel"
        )
        self.current_file_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Thanh tiến trình tổng thể
        self.progress_label = ttk.Label(
            progress_frame,
            text="Tiến trình tổng thể:",
            style="TLabel"
        )
        self.progress_label.pack(anchor=tk.W)
        
        self.progress = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            length=650,
            mode="determinate",
            style="TProgressbar"
        )
        self.progress.pack(fill=tk.X, pady=5)
        
        # Thanh tiến trình file hiện tại
        self.file_progress_label = ttk.Label(
            progress_frame,
            text="Tiến trình file hiện tại:",
            style="TLabel"
        )
        self.file_progress_label.pack(anchor=tk.W)
        
        self.file_progress = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            length=650,
            mode="determinate",
            style="TProgressbar"
        )
        self.file_progress.pack(fill=tk.X, pady=5)
        
        # Frame chứa nút chuyển đổi và trạng thái
        control_frame = ttk.Frame(main_frame, style="TFrame")
        control_frame.pack(fill=tk.X, pady=10)
        
        # Nút chuyển đổi
        self.convert_button = ttk.Button(
            control_frame,
            text="Chuyển Đổi",
            command=self.start_conversion,
            state="disabled",
            style="TButton"
        )
        self.convert_button.pack(pady=10)
        
        # Label trạng thái
        self.status_label = ttk.Label(
            control_frame,
            text="",
            style="Status.TLabel",
            wraplength=650
        )
        self.status_label.pack(pady=5)

    def select_videos(self):
        file_paths = filedialog.askopenfilenames(
            title="Chọn file video",
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov *.flv *.webm")]
        )
        if file_paths:
            for path in file_paths:
                if path not in self.video_paths:
                    self.video_paths.append(path)
                    self.file_listbox.insert(tk.END, os.path.basename(path))
            self.update_convert_button()

    def select_video_folder(self):
        folder_path = filedialog.askdirectory(title="Chọn thư mục chứa video")
        if folder_path:
            video_extensions = (".mp4", ".avi", ".mkv", ".mov", ".flv", ".webm")
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(video_extensions):
                        full_path = os.path.join(root, file)
                        if full_path not in self.video_paths:
                            self.video_paths.append(full_path)
                            self.file_listbox.insert(tk.END, file)
            self.update_convert_button()

    def clear_file_list(self):
        self.file_listbox.delete(0, tk.END)
        self.video_paths = []
        self.update_convert_button()

    def select_output_dir(self):
        dir_path = filedialog.askdirectory(title="Chọn thư mục lưu file MP3")
        if dir_path:
            self.output_dir = dir_path
            self.output_label.config(text=f"Thư mục lưu: {dir_path}")
            self.update_convert_button()

    def update_convert_button(self):
        if len(self.video_paths) > 0 and self.output_dir is not None:
            self.convert_button.config(state="normal")
        else:
            self.convert_button.config(state="disabled")

    def check_ffmpeg(self):
        return shutil.which('ffmpeg') is not None

    def get_video_duration(self, video_path):
        try:
            # Sử dụng ffprobe để lấy thông tin thời lượng video
            command = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            duration = float(result.stdout.strip())
            return duration
        except Exception as e:
            print(f"Không thể lấy thời lượng video: {e}")
            return None

    def start_conversion(self):
        if not self.check_ffmpeg():
            messagebox.showerror(
                "Lỗi",
                "ffmpeg chưa được cài đặt. Vui lòng cài đặt ffmpeg để sử dụng ứng dụng."
            )
            return
        
        if self.is_converting:
            return
        
        self.is_converting = True
        self.convert_button.config(state="disabled")
        self.select_file_button.config(state="disabled")
        self.select_folder_button.config(state="disabled")
        self.clear_button.config(state="disabled")
        self.output_button.config(state="disabled")
        
        # Bắt đầu thread chuyển đổi
        conversion_thread = threading.Thread(target=self.convert_all_files)
        conversion_thread.daemon = True
        conversion_thread.start()

    def convert_all_files(self):
        try:
            total_files = len(self.video_paths)
            self.progress["maximum"] = total_files
            self.progress["value"] = 0
            
            successful_conversions = 0
            failed_conversions = 0
            
            for index, video_path in enumerate(self.video_paths):
                try:
                    # Cập nhật trạng thái
                    file_name = os.path.basename(video_path)
                    self.current_file_label.config(text=f"Đang xử lý: {file_name} ({index+1}/{total_files})")
                    self.status_label.config(text=f"Đang chuyển đổi file {index+1}/{total_files}...")
                    self.root.update()
                    
                    # Đặt lại thanh tiến trình file
                    self.file_progress["value"] = 0
                    self.file_progress["maximum"] = 100
                    
                    # Lấy tên file từ đường dẫn video
                    video_filename = os.path.splitext(os.path.basename(video_path))[0]
                    output_path = os.path.join(self.output_dir, f"{video_filename}.mp3")
                    
                    # Lấy thông tin thời lượng video
                    duration = self.get_video_duration(video_path)
                    
                    # Chuẩn bị lệnh ffmpeg
                    command = [
                        'ffmpeg',
                        '-i', video_path,
                        '-vn',  # Bỏ qua phần video
                        '-acodec', 'libmp3lame',  # Sử dụng codec MP3
                        '-q:a', '2',  # Chất lượng âm thanh (0-9, 0=tốt nhất)
                        '-y',  # Ghi đè file nếu đã tồn tại
                        output_path
                    ]
                    
                    # Khởi tạo process chuyển đổi
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    
                    start_time = time.time()
                    last_update_time = start_time
                    
                    # Theo dõi tiến trình
                    while process.poll() is None:
                        # Đọc output từ stderr của ffmpeg
                        line = process.stderr.readline()
                        if line:
                            # Tìm thông tin thời gian trong output
                            time_match = re.search(r'time=([0-9:.]+)', line)
                            if time_match and duration:
                                current_time = self._parse_time(time_match.group(1))
                                progress = min(100, int((current_time / duration) * 100))
                                
                                # Cập nhật thanh tiến trình mỗi 100ms
                                current_time = time.time()
                                if current_time - last_update_time >= 0.1:
                                    self.file_progress["value"] = progress
                                    self.root.update()
                                    last_update_time = current_time
                    
                    # Kiểm tra kết quả
                    return_code = process.wait()
                    if return_code == 0:
                        successful_conversions += 1
                        self.file_progress["value"] = 100
                    else:
                        failed_conversions += 1
                        error_output = process.stderr.read()
                        print(f"Lỗi khi chuyển đổi {file_name}: {error_output}")
                        
                except Exception as e:
                    failed_conversions += 1
                    print(f"Lỗi khi xử lý {file_name}: {str(e)}")
                    messagebox.showerror("Lỗi", f"Không thể chuyển đổi file {file_name}:\n{str(e)}")
                
                # Cập nhật thanh tiến trình tổng thể
                self.progress["value"] = index + 1
                self.root.update()
            
            # Hiển thị thông báo kết quả
            completion_message = f"Hoàn thành chuyển đổi!\n"
            completion_message += f"Thành công: {successful_conversions} file(s)\n"
            if failed_conversions > 0:
                completion_message += f"Thất bại: {failed_conversions} file(s)"
            
            self.status_label.config(text=completion_message)
            messagebox.showinfo("Hoàn thành", completion_message)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi trong quá trình chuyển đổi:\n{str(e)}")
        
        finally:
            # Khôi phục trạng thái các nút
            self.is_converting = False
            self.convert_button.config(state="normal")
            self.select_file_button.config(state="normal")
            self.select_folder_button.config(state="normal")
            self.clear_button.config(state="normal")
            self.output_button.config(state="normal")
    
    def _parse_time(self, time_str):
        """Chuyển đổi chuỗi thời gian từ ffmpeg sang số giây"""
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                hours = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            return 0
        except:
            return 0

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernVideoToMP3Converter(root)
    root.mainloop()