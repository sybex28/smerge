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
        self.window.minsize(400, 300)
        self.window.resizable(True, True)
        
        # Скрываем окно при запуске
        self.window.withdraw()
        
        # Обновленная цветовая схема с новыми цветами кнопок
        self.colors = {
            'bg': '#1e1e1e',           # Основной фон
            'secondary_bg': '#2d2d2d',  # Вторичный фон
            'accent': '#6366f1',        # Новый фиолетовый акцент
            'accent_hover': '#8b5cf6',  # Светло-фиолетовый при наведении
            'secondary_accent': '#10b981', # Зеленый для второстепенных кнопок
            'secondary_hover': '#34d399',  # Светло-зеленый при наведении
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
        self.interface_created = False
        
        # Настройка темной темы
        self.setup_dark_theme()
        
        # Настройка полностью адаптивной сетки
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Сразу открываем диалог выбора файлов
        self.window.after(100, self.select_files)
        
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

                           font=('Segoe UI', 8))  # Уменьшили с 9 до 8
        
        # Обновленные стили для кнопок
        # Основная акцентная кнопка (фиолетовая)
        self.style.configure('Accent.TButton',
                           background=self.colors['accent'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(20, 12))
        
        self.style.map('Accent.TButton',
                      background=[('active', self.colors['accent_hover']),
                                ('pressed', self.colors['accent'])])
        



        # Голубая кнопка для merge
        self.style.configure('Blue.TButton',
                           background='#0ea5e9',  # Голубой
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(15, 10))
        



        self.style.map('Blue.TButton',
                      background=[('active', '#38bdf8'),  # Светло-голубой при наведении
                                ('pressed', '#0ea5e9')])
        



        # Серая кнопка для change selection
        self.style.configure('Gray.TButton',
                           background='#6b7280',  # Серый
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(20, 12))
        



        self.style.map('Gray.TButton',
                      background=[('active', '#9ca3af'),  # Светло-серый при наведении
                                ('pressed', '#6b7280')])
        
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
                           background='#0ea5e9',  # Голубой цвет как у кнопки merge
                           troughcolor=self.colors['secondary_bg'],
                           borderwidth=0,
                           lightcolor='#0ea5e9',  # Голубой цвет
                           darkcolor='#0ea5e9')   # Голубой цвет)
        
    def create_widgets(self):
        # Основной контейнер с отступами
        main_container = ttk.Frame(self.window, style='Dark.TFrame')
        main_container.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_container, text="🎵 Audio Merger", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 10))
        

        # Кнопка выбора файлов (теперь серая)
        self.select_btn = ttk.Button(main_container, text="📁 Change Selection", 

                                   command=self.select_files, style='Gray.TButton')
        self.select_btn.grid(row=1, column=0, pady=(0, 6), sticky='ew')
        


        # Лейбл со списком выбранных файлов с настройкой переноса по словам
        self.files_label = ttk.Label(main_container, text="", style='Files.TLabel', 
                                   wraplength=350, justify='left')
        self.files_label.grid(row=2, column=0, pady=(0, 8), sticky='ew')
        
        # Карточка настроек вывода
        self.output_card = ttk.Frame(main_container, style='Card.TFrame')
        self.output_card.grid(row=3, column=0, sticky='ew', pady=(0, 8))
        self.output_card.grid_columnconfigure(1, weight=1)
        
        filename_label = ttk.Label(self.output_card, text="Filename:", style='Card.TLabel')
        filename_label.grid(row=0, column=0, padx=15, pady=(10, 10), sticky='w')
        
        self.filename_entry = ttk.Entry(self.output_card, style='Dark.TEntry')
        self.filename_entry.grid(row=0, column=1, sticky='ew', padx=(10, 15), pady=(10, 10))
        
        # Прогресс бар и статус
        self.progress_frame = ttk.Frame(main_container, style='Dark.TFrame')
        self.progress_frame.grid(row=4, column=0, sticky='ew', pady=(0, 8))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_remove()
        
        self.progress = ttk.Progressbar(self.progress_frame, mode='determinate', style='Dark.Horizontal.TProgressbar')
        self.progress.grid(row=0, column=0, sticky='ew', pady=(0, 4))
        
        self.status_label = ttk.Label(self.progress_frame, text="", style='Status.TLabel')
        self.status_label.grid(row=1, column=0)
        
        # Кнопка объединения
        self.merge_frame = ttk.Frame(main_container, style='Dark.TFrame')
        self.merge_frame.grid(row=5, column=0, sticky='ew')
        self.merge_frame.grid_columnconfigure(0, weight=1)
        
        self.merge_btn = ttk.Button(self.merge_frame, text="🔗 Merge Audio Files", 
                                  command=self.merge_files, style='Blue.TButton')
        self.merge_btn.grid(row=0, column=0, sticky='ew')
        
        # Bind window resize event
        self.window.bind('<Configure>', self.on_window_resize)
        
        self.interface_created = True

    def update_min_size(self):
        """Обновляет минимальный размер окна на основе содержимого"""
        self.window.update_idletasks()
        # Получаем требуемый размер для всех элементов
        req_width = self.window.winfo_reqwidth()
        req_height = self.window.winfo_reqheight()
        
        # Добавляем больший запас для всех элементов
        min_width = max(500, req_width + 80)  # Изменили с 450 на 500
        min_height = max(240, req_height + 40)
        
        self.window.minsize(min_width, min_height)

    def on_window_resize(self, event):
        # Update label wraplength when window is resized
        if hasattr(self, 'files_label') and event.widget == self.window:
            # Адаптивная ширина с минимумом для правильного переноса слов
            new_width = max(300, event.width - 80)
            self.files_label.configure(wraplength=new_width)

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
                
                # Создаем интерфейс только после выбора файлов
                if not self.interface_created:
                    self.create_widgets()
                    self.window.deiconify()  # Показываем окно
                
                self.update_ui_after_selection()
            else:
                logging.info("No files selected")
                # Если файлы не выбраны, закрываем приложение
                if not self.interface_created:
                    self.window.quit()
        except Exception as e:
            logging.error(f"Error in file selection: {str(e)}")
            logging.error(traceback.format_exc())
            if self.interface_created:
                messagebox.showerror("Error", f"Error selecting files: {str(e)}")
            else:
                self.window.quit()

    def update_ui_after_selection(self):
        # Show/hide appropriate elements
        if self.selected_files:
            # Обновляем текст с выбранными файлами и путем к папке
            files_count = len(self.selected_files)
            files_names = [f"[{os.path.basename(f)}]" for f in self.selected_files]
            folder_path = os.path.dirname(self.selected_files[0])
            
            # Создаем текст в формате: Selected X files: [список] from путь
            files_text = f"Selected {files_count} files: {', '.join(files_names)} from {folder_path}"
            self.files_label.config(text=files_text)
            
            # Пересчитываем минимальный размер окна после добавления элементов
            self.window.after(50, self.update_min_size)

    def merge_files(self):
        if not self.selected_files:
            logging.warning("Attempted to merge with no files selected")
            self.show_completion_message("⚠️ Please select files first!", is_error=True)
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
                output_filename = "merged_audio"  # Используем по умолчанию если поле пустое
                
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
            
            # Показать информацию о завершении в интерфейсе вместо popup
            self.show_completion_message(f"✅ Files merged successfully!\nSaved as: {os.path.basename(output_path)}\nLocation: {os.path.dirname(output_path)}")
            
        except Exception as e:
            logging.error("Error during merge process:")
            logging.error(traceback.format_exc())
            self.show_completion_message(f"❌ An error occurred: {str(e)}", is_error=True)
        finally:
            # Включить кнопки обратно
            self.select_btn.config(state='normal')
        
        self.progress_frame.grid_remove()
        self.merge_frame.grid()

    def show_completion_message(self, message, is_error=False):
        """Показывает сообщение о завершении в интерфейсе"""
        # Скрыть прогрессбар
        self.progress_frame.grid_remove()
        
        # Создать фрейм для сообщения о завершении
        if not hasattr(self, 'completion_frame'):
            self.completion_frame = ttk.Frame(self.merge_frame.master, style='Dark.TFrame')
        
        # Очистить фрейм
        for widget in self.completion_frame.winfo_children():
            widget.destroy()
        
        # Создать лейбл с сообщением
        completion_style = 'Dark.TLabel'
        if is_error:
            # Можно добавить специальный стиль для ошибок
            completion_style = 'Dark.TLabel'
        
        completion_label = ttk.Label(self.completion_frame, text=message, 
                                   style=completion_style, justify='center',
                                   font=('Segoe UI', 10))
        completion_label.grid(row=0, column=0, pady=(0, 10))
        
        # Кнопка для нового объединения
        new_merge_btn = ttk.Button(self.completion_frame, text="🔗 Merge Again", 
                                 command=self.reset_for_new_merge, style='Blue.TButton')
        new_merge_btn.grid(row=1, column=0, sticky='ew')
        
        # Показать фрейм завершения
        self.completion_frame.grid(row=5, column=0, sticky='ew')
        self.completion_frame.grid_columnconfigure(0, weight=1)

    def reset_for_new_merge(self):
        """Сброс интерфейса для нового объединения"""
        # Скрыть фрейм завершения
        if hasattr(self, 'completion_frame'):
            self.completion_frame.grid_remove()
        
        # Показать обратно кнопку merge
        self.merge_frame.grid()

if __name__ == "__main__":
    logging.info("Starting application")
    try:
        app = AudioMerger()
        app.window.mainloop()
    except Exception as e:
        logging.critical("Application crashed:")
        logging.critical(traceback.format_exc())