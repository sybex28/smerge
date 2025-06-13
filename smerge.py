import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import traceback
import logging
from datetime import datetime

# Настройка логирования
log_filename = f"smerge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class AudioMerger:
    def __init__(self):
        logging.info("Initializing Audio Merger application")
        self.window = tk.Tk()
        self.window.title("Audio Merger")
        self.window.minsize(500, 150)
        self.window.resizable(True, False)
        
        # Темная цветовая схема
        self.colors = {
            'bg': '#1e1e1e',           # Основной фон
            'secondary_bg': '#2d2d2d',  # Вторичный фон
            'accent': '#0d7377',        # Акцентный цвет
            'accent_hover': '#14a085',  # Акцент при наведении
            'text': '#ffffff',          # Основной текст
            'text_secondary': '#b0b0b0', # Вторичный текст
            'border': '#404040',        # Границы
            'success': '#4caf50',       # Успех
            'error': '#f44336',         # Ошибка
            'warning': '#ff9800'        # Предупреждение
        }
        
        self.selected_files = []
        self.output_path = ""
        self.merge_btn = None
        
        # Настройка темной темы
        self.setup_dark_theme()
        
        # Настройка адаптивной сетки
        self.window.grid_columnconfigure(0, weight=1)
        
        # Create GUI elements
        self.create_widgets()
        
    def setup_dark_theme(self):
        """Настройка темной темы для приложения"""
        # Основные настройки окна
        self.window.configure(bg=self.colors['bg'])
        
        # Создание стиля для ttk виджетов
        self.style = ttk.Style()
        
        # Настройка темы для различных виджетов
        self.style.theme_use('clam')
        
        # Настройка стилей для Frame
        self.style.configure('Dark.TFrame', 
                           background=self.colors['bg'],
                           borderwidth=0)
        
        self.style.configure('Card.TFrame',
                           background=self.colors['secondary_bg'],
                           relief='flat',
                           borderwidth=1)
        
        # Настройка стилей для Label
        self.style.configure('Dark.TLabel',
                           background=self.colors['bg'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 10))
        
        self.style.configure('Card.TLabel',
                           background=self.colors['secondary_bg'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 10))
        
        self.style.configure('Title.TLabel',
                           background=self.colors['bg'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 12, 'bold'))
        
        self.style.configure('Status.TLabel',
                           background=self.colors['bg'],
                           foreground=self.colors['text_secondary'],
                           font=('Segoe UI', 9))
        
        self.style.configure('Files.TLabel',
                           background=self.colors['bg'],
                           foreground=self.colors['text_secondary'],
                           font=('Segoe UI', 9))
        
        # Настройка стилей для Button
        self.style.configure('Accent.TButton',
                           background=self.colors['accent'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(20, 10))
        
        self.style.map('Accent.TButton',
                      background=[('active', self.colors['accent_hover']),
                                ('pressed', self.colors['accent'])])
        
        self.style.configure('Secondary.TButton',
                           background=self.colors['secondary_bg'],
                           foreground=self.colors['text'],
                           borderwidth=1,
                           focuscolor='none',
                           font=('Segoe UI', 10),
                           padding=(15, 8))
        
        self.style.map('Secondary.TButton',
                      background=[('active', self.colors['border']),
                                ('pressed', self.colors['secondary_bg'])],
                      bordercolor=[('focus', self.colors['accent'])])
        
        # Настройка стилей для Entry
        self.style.configure('Dark.TEntry',
                           fieldbackground=self.colors['secondary_bg'],
                           background=self.colors['secondary_bg'],
                           foreground=self.colors['text'],
                           bordercolor=self.colors['border'],
                           insertcolor=self.colors['text'],
                           font=('Segoe UI', 10),
                           padding=8)
        
        self.style.map('Dark.TEntry',
                      bordercolor=[('focus', self.colors['accent'])])
        
        # Настройка стилей для Progressbar
        self.style.configure('Dark.Horizontal.TProgressbar',
                           background=self.colors['accent'],
                           troughcolor=self.colors['secondary_bg'],
                           borderwidth=0,
                           lightcolor=self.colors['accent'],
                           darkcolor=self.colors['accent'])
        
    def create_widgets(self):
        # Основной контейнер с отступами
        main_container = ttk.Frame(self.window, style='Dark.TFrame')
        main_container.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_container, text="🎵 Audio Merger", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Кнопка выбора файлов
        self.select_btn = ttk.Button(main_container, text="📁 Select Audio Files", 
                                   command=self.select_files, style='Accent.TButton')
        self.select_btn.grid(row=1, column=0, pady=(0, 10), sticky='ew')
        
        # Лейбл со списком выбранных файлов
        self.files_label = ttk.Label(main_container, text="", style='Files.TLabel', wraplength=450)
        self.files_label.grid(row=2, column=0, pady=(0, 15), sticky='ew')
        
        # Карточка настроек вывода
        self.output_card = ttk.Frame(main_container, style='Card.TFrame')
        self.output_card.grid(row=3, column=0, sticky='ew', pady=(0, 15))
        self.output_card.grid_columnconfigure(1, weight=1)
        self.output_card.grid_remove()  # Скрыто по умолчанию
        
        output_title = ttk.Label(self.output_card, text="Output Settings", style='Card.TLabel', font=('Segoe UI', 10, 'bold'))
        output_title.grid(row=0, column=0, columnspan=2, sticky='w', padx=15, pady=(15, 10))
        
        filename_label = ttk.Label(self.output_card, text="Filename:", style='Card.TLabel')
        filename_label.grid(row=1, column=0, padx=15, pady=(0, 15), sticky='w')
        
        self.filename_entry = ttk.Entry(self.output_card, style='Dark.TEntry')
        self.filename_entry.insert(0, "merged_audio")
        self.filename_entry.grid(row=1, column=1, sticky='ew', padx=(10, 15), pady=(0, 15))
        
        # Прогресс бар и статус
        self.progress_frame = ttk.Frame(main_container, style='Dark.TFrame')
        self.progress_frame.grid(row=4, column=0, sticky='ew', pady=(0, 15))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_remove()
        
        self.progress = ttk.Progressbar(self.progress_frame, mode='determinate', style='Dark.Horizontal.TProgressbar')
        self.progress.grid(row=0, column=0, sticky='ew', pady=(0, 8))
        
        self.status_label = ttk.Label(self.progress_frame, text="", style='Status.TLabel')
        self.status_label.grid(row=1, column=0)
        
        # Кнопка объединения
        self.merge_frame = ttk.Frame(main_container, style='Dark.TFrame')
        self.merge_frame.grid(row=5, column=0, sticky='ew')
        self.merge_frame.grid_columnconfigure(0, weight=1)
        self.merge_frame.grid_remove()
        
        # Bind window resize event
        self.window.bind('<Configure>', self.on_window_resize)

    def on_window_resize(self, event):
        # Update label wraplength when window is resized
        if hasattr(self, 'files_label'):
            self.files_label.configure(wraplength=event.width - 80)

    def update_status(self, message, progress_value):
        self.status_label.config(text=message)
        self.progress['value'] = progress_value
        self.window.update()
        
    def select_files(self):
        logging.info("Opening file selection dialog")
        try:
            files = filedialog.askopenfilenames(
                filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.aac *.ogg")],
                title="Select Audio Files"
            )
            if files:
                logging.info(f"Selected {len(files)} files")
                def natural_keys(text):
                    import re
                    def atoi(text):
                        return int(text) if text.isdigit() else text
                    return [atoi(c) for c in re.split(r'(\d+)', os.path.basename(text))]
                
                self.selected_files = sorted(files, key=natural_keys)
                self.output_path = os.path.dirname(self.selected_files[0])
                logging.debug(f"Output path set to: {self.output_path}")
                
                # Создаем строку с именами файлов через запятую
                files_string = ", ".join([os.path.basename(f) for f in self.selected_files])
                logging.info(f"Selected files: {files_string}")
                
                self.update_ui_after_selection()
            else:
                logging.info("No files selected")
        except Exception as e:
            logging.error(f"Error in file selection: {str(e)}")
            logging.error(traceback.format_exc())
            messagebox.showerror("Error", f"Error selecting files: {str(e)}")

    def update_ui_after_selection(self):
        # Show/hide appropriate elements
        if self.selected_files:
            # Обновляем текст с выбранными файлами
            files_count = len(self.selected_files)
            files_names = [f"[{os.path.basename(f)}]" for f in self.selected_files]
            files_text = f"Selected {files_count} files: {', '.join(files_names)}"
            self.files_label.config(text=files_text)
            
            # Показать настройки вывода
            self.output_card.grid()
            
            # Create and show merge button if files are selected
            if not self.merge_btn:
                self.merge_btn = ttk.Button(self.merge_frame, text="🔗 Merge Audio Files", 
                                          command=self.merge_files, style='Accent.TButton')
                self.merge_btn.grid(row=0, column=0, sticky='ew')
            
            self.merge_frame.grid()
            
            # Обновить кнопку выбора
            self.select_btn.config(text="📁 Change Selection")
        else:
            # Hide elements if no files
            self.files_label.config(text="")
            self.output_card.grid_remove()
            self.merge_frame.grid_remove()
            self.select_btn.config(text="📁 Select Audio Files")

    def merge_files(self):
        if not self.selected_files:
            logging.warning("Attempted to merge with no files selected")
            messagebox.showwarning("Warning", "Please select files first!")
            return
        
        logging.info("Starting file merge process")
        
        # Показать прогресс, скрыть кнопку объединения
        self.merge_frame.grid_remove()
        self.progress_frame.grid()
        self.progress['value'] = 0
        
        # Отключить кнопки во время обработки
        self.select_btn.config(state='disabled')
        
        try:
            output_filename = self.filename_entry.get().strip()
            if not output_filename:
                output_filename = "merged_audio"
                
            logging.info(f"Output filename: {output_filename}")
            
            self.update_status("🔄 Preparing to merge...", 10)
            output_format = os.path.splitext(self.selected_files[0])[1]
            output_path = os.path.join(self.output_path, f"{output_filename}{output_format}")
            logging.debug(f"Full output path: {output_path}")
            
            self.update_status("📝 Creating output file...", 20)
            with open(output_path, 'wb') as outfile:
                file_count = len(self.selected_files)
                progress_per_file = 60 / file_count
                
                for i, file in enumerate(self.selected_files, 1):
                    current_file = os.path.basename(file)
                    logging.info(f"Processing file {i}/{file_count}: {current_file}")
                    self.update_status(f"🎵 Processing {i}/{file_count}: {current_file}", 
                                     20 + (i * progress_per_file))
                    
                    with open(file, 'rb') as infile:
                        outfile.write(infile.read())
            
            logging.info("Merge completed successfully")
            self.update_status("Merge complete!", 100)
            messagebox.showinfo("Success", f"Files merged successfully!\nSaved as: {output_path}")
            
        except Exception as e:
            logging.error("Error during merge process:")
            logging.error(traceback.format_exc())
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.update_status("Error occurred during merge", 0)
        finally:
            # Включить кнопки обратно
            self.select_btn.config(state='normal')
        
        self.progress_frame.grid_remove()
        self.merge_frame.grid()

if __name__ == "__main__":
    logging.info("Starting application")
    try:
        app = AudioMerger()
        app.window.mainloop()
    except Exception as e:
        logging.critical("Application crashed:")
        logging.critical(traceback.format_exc())