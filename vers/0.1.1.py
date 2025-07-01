import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import traceback
import logging
from datetime import datetime
import hashlib  # Добавляем для более точной проверки дубликатов
import wave
import struct

# Настройка логирования
log_filename = "smerge.log"
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
        logging.info("Initializing smerge application")
        self.window = tk.Tk()
        self.window.title("smerge")

        self.window.minsize(500, 200)  # Минимальный размер 500x200
        self.window.resizable(True, True)  # Изменили с (True, False) на (True, True) - теперь можно изменять и по высоте
        
        # Скрываем окно при запуске
        self.window.withdraw()
        
        # Обновленная цветовая схема с новыми цветами кнопок
        self.colors = {
            'bg': '#141E1B',           # Основной фон (темно-зеленый)
            'secondary_bg': '#1D2B27',  # Вторичный фон (чуть светлее основного)
            'accent': '#9D7CFF',        # Новый фиолетовый акцент
            'accent_hover': '#B49DFF',  # Светло-фиолетовый при наведении
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

    def get_audio_duration(self, file_path):
        """Получает продолжительность аудиофайла"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.wav':
                return self.get_wav_duration(file_path)
            elif file_ext == '.mp3':
                return self.get_mp3_duration(file_path)
            else:
                # Для других форматов пытаемся определить по размеру файла (приблизительно)
                return self.estimate_duration_by_size(file_path)
                
        except Exception as e:
            logging.warning(f"Could not determine duration for {file_path}: {str(e)}")
            return None

    def get_wav_duration(self, file_path):
        """Получает продолжительность WAV файла"""
        try:
            with wave.open(file_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / float(sample_rate)
                return duration
        except Exception as e:
            logging.warning(f"Error reading WAV file {file_path}: {str(e)}")
            return None

    def get_mp3_duration(self, file_path):
        """Получает приблизительную продолжительность MP3 файла"""
        try:
            # Простая оценка для MP3 на основе размера файла и битрейта
            file_size = os.path.getsize(file_path)
            
            # Пытаемся найти MP3 заголовок для определения битрейта
            with open(file_path, 'rb') as f:
                # Ищем MP3 frame header
                data = f.read(4096)  # Читаем первые 4KB
                
                for i in range(len(data) - 4):
                    if data[i] == 0xFF and (data[i + 1] & 0xE0) == 0xE0:
                        # Найден потенциальный MP3 header
                        header = struct.unpack('>I', data[i:i+4])[0]
                        bitrate = self.get_mp3_bitrate_from_header(header)
                        if bitrate > 0:
                            # Приблизительная продолжительность = размер_файла / (битрейт / 8)
                            duration = (file_size * 8) / (bitrate * 1000)
                            return duration
                        break
            
            # Если не удалось определить битрейт, используем средний битрейт 128 kbps
            duration = (file_size * 8) / (128 * 1000)
            return duration
            
        except Exception as e:
            logging.warning(f"Error reading MP3 file {file_path}: {str(e)}")
            return None

    def get_mp3_bitrate_from_header(self, header):
        """Извлекает битрейт из MP3 заголовка"""
        try:
            # MP3 bitrate table (MPEG-1 Layer III)
            bitrate_table = [
                0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0
            ]
            
            bitrate_index = (header >> 12) & 0xF
            if 0 < bitrate_index < 15:
                return bitrate_table[bitrate_index]
            return 0
        except:
            return 0

    def estimate_duration_by_size(self, file_path):
        """Приблизительная оценка продолжительности по размеру файла"""
        try:
            file_size = os.path.getsize(file_path)
            # Используем средний битрейт 128 kbps для оценки
            duration = (file_size * 8) / (128 * 1000)
            return duration
        except:
            return None

    def format_duration(self, seconds):
        """Форматирует продолжительность в читаемый вид"""
        if seconds is None:
            return "unknown duration"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
        
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
                           background='#141E1B',  # Используем основной фон
                           relief='flat',
                           borderwidth=1)
        
        # Настройка стилей для Label
        self.style.configure('Dark.TLabel',
                           background=self.colors['bg'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 10))
        
        self.style.configure('Card.TLabel',
                           background='#141E1B',  # Используем основной фон
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
                           font=('Segoe UI', 8))
        
        # Добавляем стиль для жирного текста файлов (без изменения фона)
        self.style.configure('FilesBold.TLabel',
                           background=self.colors['bg'],  # Тот же фон
                           foreground=self.colors['text_secondary'],  # Тот же цвет текста
                           font=('Segoe UI', 8, 'bold'))  # Только жирный шрифт
        
        # Добавляем стиль для успешного сообщения (зеленый цвет + жирный шрифт)
        self.style.configure('Success.TLabel',
                           background=self.colors['bg'],
                           foreground='#00e39a',  # Зеленый цвет как у кнопки merge
                           font=('Segoe UI', 10, 'bold'))  # Добавили 'bold'
        
        # Обновленные стили для кнопок
        # Основная акцентная кнопка (фиолетовая)
        self.style.configure('Accent.TButton',
                           background=self.colors['accent'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(20, 12),
                           justify='center')
        
        self.style.map('Accent.TButton',
                      background=[('active', self.colors['accent_hover']),
                                ('pressed', self.colors['accent'])])

        # Зеленая кнопка для merge
        self.style.configure('Blue.TButton',
                           background='#00e39a',  # Зеленый
                           foreground='#021b18',  # Темно-зеленый текст
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(15, 10),
                           justify='center')

        self.style.map('Blue.TButton',
                      background=[('active', '#34f5b5'),  # Светло-зеленый при наведении
                                ('pressed', '#00e39a')])

        # Фиолетовая кнопка для change selection
        self.style.configure('Gray.TButton',
                           background='#8556f6',  # Фиолетовый
                           foreground='white',    # Белый текст
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(20, 12),
                           justify='center')

        self.style.map('Gray.TButton',
                      background=[('active', '#9d7cff'),  # Светло-фиолетовый при наведении
                                ('pressed', '#8556f6')])
        
        # Настройка стилей для Entry
        self.style.configure('Dark.TEntry',
                           fieldbackground='#141E1B',  # Основной фон
                           background='#141E1B',  # Основной фон
                           foreground=self.colors['text'],
                           bordercolor=self.colors['border'],
                           insertcolor=self.colors['text'],
                           font=('Segoe UI', 10, 'bold'),
                           padding=(10, 8))
        
        self.style.map('Dark.TEntry',
                      bordercolor=[('focus', '#9D7CFF')],  # Фиолетовая подсветка при фокусе
                      fieldbackground=[('focus', '#374151')])  # Немного светлее фон при фокусе
        
        # Настройка стилей для Progressbar
        self.style.configure('Dark.Horizontal.TProgressbar',
                           background='#00e39a',  # Зеленый цвет как у кнопки merge
                           troughcolor=self.colors['secondary_bg'],
                           borderwidth=0,
                           lightcolor='#00e39a',  # Зеленый цвет
                           darkcolor='#00e39a')   # Зеленый цвет)
        
    def create_widgets(self):
        # Основной контейнер с отступами
        main_container = ttk.Frame(self.window, style='Dark.TFrame')
        main_container.grid(row=0, column=0, sticky='nsew', padx=10, pady=15)  # Одинаковые отступы сверху и снизу
        main_container.grid_columnconfigure(0, weight=1)
        self.main_container = main_container  # Сохраняем ссылку для доступа в других методах

        # Кнопка выбора файлов (без иконки)
        self.select_btn = ttk.Button(main_container, text="Change Selection", 
                                   command=self.select_files, style='Gray.TButton')
        self.select_btn.grid(row=0, column=0, pady=(0, 6), padx=5, sticky='ew')  # Растягиваем на всю ширину
        
        # Лейбл для информации о файлах
        self.files_info_label = ttk.Label(main_container, text="", style='Files.TLabel', 
                                        wraplength=380, justify='left')
        self.files_info_label.grid(row=1, column=0, pady=(0, 8), sticky='ew', padx=5)
        
        # Фрейм для поля ввода, прогрессбара и результата с фиксированной высотой
        self.input_frame = ttk.Frame(main_container, style='Dark.TFrame', height=40)
        self.input_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=(0, 8))
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_propagate(False)  # Запрещаем изменение размера
        
        # Поле ввода имени файла
        self.filename_entry = ttk.Entry(self.input_frame, style='Dark.TEntry')
        self.filename_entry.grid(row=0, column=0, sticky='ew', pady=5)
        
        # Привязываем нажатие Enter к функции объединения файлов
        self.filename_entry.bind('<Return>', lambda event: self.merge_files())
        
        # Прогресс бар (скрыт изначально, занимает то же место что и поле ввода)
        self.progress = ttk.Progressbar(self.input_frame, mode='determinate', style='Dark.Horizontal.TProgressbar')
        self.progress.grid(row=0, column=0, sticky='ew', pady=5)
        self.progress.grid_remove()  # Скрываем изначально
        
        # Лейбл для результата (скрыт изначально, занимает то же место)
        self.result_label = ttk.Label(self.input_frame, text="", style='Success.TLabel', 
                                    wraplength=400, justify='center')
        self.result_label.grid(row=0, column=0, sticky='ew', pady=5)
        self.result_label.grid_remove()  # Скрываем изначально
        

        
        # Кнопка объединения (всегда видна, но может быть отключена)
        self.merge_frame = ttk.Frame(main_container, style='Dark.TFrame')
        self.merge_frame.grid(row=4, column=0, sticky='ew', pady=(0, 0))  # Убираем отступ, так как увеличили высоту окна
        self.merge_frame.grid_columnconfigure(0, weight=1)
        
        self.merge_btn = ttk.Button(self.merge_frame, text="Merge Audio Files", 
                                  command=self.merge_files, style='Blue.TButton', state='disabled')
        self.merge_btn.grid(row=0, column=0, sticky='ew', padx=5)
        
        # Bind window resize event
        self.window.bind('<Configure>', self.on_window_resize)
        
        self.interface_created = True

    def update_min_size(self):
        """Устанавливает оптимальный размер окна"""
        # Устанавливаем размер 500x200
        self.window.geometry("500x200")

    def on_window_resize(self, event):
        # Обновляем wraplength при ручном изменении размера окна
        if event.widget == self.window:
            new_width = max(300, event.width - 50)
            if hasattr(self, 'files_info_label'):
                self.files_info_label.configure(wraplength=new_width)

    def update_status(self, message, progress_value):
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
                
                # Создаем интерфейс только после выбора файлов
                if not self.interface_created:
                    self.create_widgets()
                    self.update_min_size()  # Устанавливаем фиксированный размер
                    self.window.deiconify()  # Показываем окно
                
                # Сбрасываем интерфейс при выборе новых файлов
                if hasattr(self, 'filename_entry'):
                    self.reset_for_new_merge()
                
                # Показываем информацию о файлах
                self.show_files_info()
                
                # Запускаем процесс загрузки файлов
                self.window.after(200, self.load_files)
                
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








    def show_files_info(self):
        """Показывает информацию о выбранных файлах"""
        files_count = len(self.selected_files)
        files_names = [f"{os.path.basename(f)}" for f in self.selected_files]
        folder_path = os.path.dirname(self.selected_files[0])
        
        # Объединяем всю информацию в одну строку
        files_text = ', '.join(files_names)
        full_text = f"Selected {files_count} files from {folder_path}: {files_text}"
        
        # Полностью обновляем лейбл
        self.files_info_label.config(text=full_text)

    def check_for_duplicates(self):
        """Проверяет файлы на дубликаты по размеру и содержимому"""
        logging.info("Checking for duplicate files")
        
        file_info = {}
        duplicates = []
        
        for i, file_path in enumerate(self.selected_files, 1):
            try:
                # Получаем размер файла
                file_size = os.path.getsize(file_path)
                
                # Обновляем прогресс
                progress_value = (i / len(self.selected_files)) * 50  # Первые 50% прогресса
                self.update_status(f"Analyzing {i}/{len(self.selected_files)}: {os.path.basename(file_path)}", progress_value)
                
                # Создаем ключ для группировки (размер файла)
                size_key = file_size
                
                if size_key not in file_info:
                    file_info[size_key] = []
                
                file_info[size_key].append(file_path)
                
            except Exception as e:
                logging.warning(f"Could not analyze file {file_path}: {str(e)}")
        
        # Проверяем группы файлов с одинаковым размером
        for size, files in file_info.items():
            if len(files) > 1:
                # Если файлы одинакового размера, проверяем их содержимое более детально
                confirmed_duplicates = self.check_file_content_similarity(files)
                if confirmed_duplicates:
                    duplicates.extend(confirmed_duplicates)
        
        return duplicates

    def check_file_content_similarity(self, files):
        """Проверяет похожесть содержимого файлов через хеш первых и последних байтов"""
        file_hashes = {}
        duplicates = []
        
        for file_path in files:
            try:
                # Читаем первые и последние 8KB файла для быстрого сравнения
                with open(file_path, 'rb') as f:
                    # Первые 8KB
                    first_chunk = f.read(8192)
                    # Переходим к концу файла
                    f.seek(-min(8192, os.path.getsize(file_path)), 2)
                    last_chunk = f.read(8192)
                    
                    # Создаем хеш из первого и последнего куска
                    content_hash = hashlib.md5(first_chunk + last_chunk).hexdigest()
                    
                    if content_hash not in file_hashes:
                        file_hashes[content_hash] = []
                    
                    file_hashes[content_hash].append(file_path)
                    
            except Exception as e:
                logging.warning(f"Could not read file content {file_path}: {str(e)}")
        
        # Находим группы с одинаковыми хешами
        for hash_key, hash_files in file_hashes.items():
            if len(hash_files) > 1:
                duplicates.append(hash_files)
        
        return duplicates

    def load_files(self):
        """Загрузка файлов с проверкой на дубликаты"""
        logging.info("Starting files loading process")
        
        # Отключить кнопку выбора во время загрузки
        self.select_btn.config(state='disabled')
        
        # Кнопка merge уже показана, просто отключаем её
        self.merge_btn.config(state='disabled')
        
        # Скрыть поле ввода и показать прогрессбар на его месте
        self.filename_entry.grid_remove()
        self.progress.grid()
        self.progress['value'] = 0
        
        try:
            # Сначала проверяем на дубликаты
            duplicates = self.check_for_duplicates()
            
            if duplicates:
                # Формируем сообщение о найденных дубликатах
                duplicate_message = "Found potentially duplicate files:\n\n"
                for i, duplicate_group in enumerate(duplicates, 1):
                    duplicate_message += f"Group {i}:\n"
                    for file_path in duplicate_group:
                        duplicate_message += f"  • {os.path.basename(file_path)}\n"
                    duplicate_message += "\n"
                
                duplicate_message += "These files have the same size and similar content.\nDo you want to continue anyway?"
                
                # Показываем предупреждение
                result = messagebox.askyesno(
                    "Duplicate Files Detected", 
                    duplicate_message,
                    icon='warning'
                )
                
                if not result:
                    logging.info("User chose to cancel due to duplicates")
                    self.progress_frame.grid_remove()
                    self.select_btn.config(state='normal')
                    return
                else:
                    logging.info("User chose to continue despite duplicates")
            
            # Продолжаем загрузку файлов
            file_count = len(self.selected_files)
            
            for i, file in enumerate(self.selected_files, 1):
                current_file = os.path.basename(file)
                logging.info(f"Loading file {i}/{file_count}: {current_file}")
                
                # Обновляем прогресс (вторые 50%)
                progress_value = 50 + ((i / file_count) * 50)
                self.update_status(f"Loading {i}/{file_count}: {current_file}", progress_value)
                
                # Имитация времени загрузки
                import time
                time.sleep(0.05)  # Уменьшили время для более быстрой загрузки
            
            logging.info("Files loaded successfully")
            
            # Показываем интерфейс объединения сразу
            self.show_merge_interface()
            
        except Exception as e:
            logging.error("Error during files loading:")
            logging.error(traceback.format_exc())
            self.update_status(f"Error loading files: {str(e)}", 0)
        finally:
            # Включить кнопку выбора обратно
            self.select_btn.config(state='normal')

    def show_merge_interface(self):
        """Показывает интерфейс для объединения после загрузки файлов"""
        # Скрыть прогрессбар
        self.progress.grid_remove()
        
        # Показать поле ввода на месте прогрессбара
        self.filename_entry.grid()
        
        # Кнопка merge уже показана, просто включаем её
        self.merge_btn.config(state='normal')
        
        # Включаем текстовое поле
        self.filename_entry.config(state='normal')
        
        # Устанавливаем фокус на поле ввода и выделяем весь текст
        self.focus_filename_entry()

    def focus_filename_entry(self):
        """Устанавливает фокус на поле ввода имени файла и выделяет текст"""
        if hasattr(self, 'filename_entry'):
            self.filename_entry.focus_set()  # Устанавливаем фокус
            self.filename_entry.select_range(0, tk.END)  # Выделяем весь текст

    def merge_files(self):
        if not self.selected_files:
            logging.warning("Attempted to merge with no files selected")

            self.show_completion_message("Please select files first!", is_error=True)
            return
        
        # Проверяем имя файла и существование
        output_filename = self.filename_entry.get().strip()
        if not output_filename:
            self.show_completion_message("Please enter a filename!", is_error=True)
            return
            
        output_format = os.path.splitext(self.selected_files[0])[1]
        output_path = os.path.join(self.output_path, f"{output_filename}{output_format}")
        
        # Проверяем, существует ли файл
        if os.path.exists(output_path):
            logging.info(f"File already exists: {output_path}")
            result = messagebox.askyesno(
                "File Exists", 
                f"File '{output_filename}{output_format}' already exists.\n\nDo you want to replace it?",
                icon='warning'
            )
            if not result:
                logging.info("User chose not to replace existing file")
                return
            else:
                logging.info("User chose to replace existing file")
        
        logging.info("Starting file merge process")
        
        # Показать прогресс, скрыть поле ввода
        self.filename_entry.grid_remove()
        self.progress.grid()
        self.progress['value'] = 0
        
        # Отключить кнопки во время обработки
        self.select_btn.config(state='disabled')
        self.filename_entry.config(state='disabled')
        
        try:




            logging.info(f"Output filename: {output_filename}")




            logging.debug(f"Full output path: {output_path}")
            

            self.update_status("Preparing to merge...", 10)
            
            self.update_status("Creating output file...", 20)
            with open(output_path, 'wb') as outfile:
                file_count = len(self.selected_files)
                progress_per_file = 60 / file_count
                
                for i, file in enumerate(self.selected_files, 1):
                    current_file = os.path.basename(file)
                    logging.info(f"Processing file {i}/{file_count}: {current_file}")

                    self.update_status(f"Processing {i}/{file_count}: {current_file}", 
                                     20 + (i * progress_per_file))
                    
                    with open(file, 'rb') as infile:
                        outfile.write(infile.read())
            
            logging.info("Merge completed successfully")
            self.update_status("Merge complete!", 100)
            
            # Показать информацию о завершении в интерфейсе (нормализуем путь для правильных разделителей)
            normalized_path = os.path.normpath(output_path)

            # Получаем продолжительность выходного файла
            output_duration = self.get_audio_duration(output_path)
            duration_text = self.format_duration(output_duration)

            self.show_completion_message(f"Files merged successfully! (Duration: {duration_text})\nSaved as: {normalized_path}")
            
        except Exception as e:
            logging.error("Error during merge process:")
            logging.error(traceback.format_exc())


            self.show_completion_message(f"An error occurred: {str(e)}", is_error=True)
        finally:
            # Включить кнопки обратно
            self.select_btn.config(state='normal')
            # Не отключаем поле ввода здесь - это будет сделано в show_completion_message

    def show_completion_message(self, message, is_error=False):
        """Показывает сообщение о завершении в области ввода"""
        # Скрыть прогрессбар
        self.progress.grid_remove()
        
        # Показать результат в области ввода
        if is_error:
            self.result_label.config(text=message, style='Dark.TLabel')
        else:
            # Для успеха показываем только первую строку (без пути к файлу)
            lines = message.split('\n')
            self.result_label.config(text=lines[0], style='Success.TLabel')
        
        self.result_label.grid()
        
        # Включаем кнопку merge для повторного использования
        self.merge_btn.config(state='normal')

    def reset_for_new_merge(self):
        """Сброс интерфейса для нового объединения"""
        # Скрыть результат и показать поле ввода
        self.result_label.grid_remove()
        self.filename_entry.grid()
        
        # Включить поле ввода обратно
        self.filename_entry.config(state='normal')
        self.filename_entry.delete(0, tk.END)  # Очищаем поле
        
        # Установить фокус на поле ввода
        self.focus_filename_entry()
    
    def run(self):
        """Запуск приложения"""
        self.window.mainloop()

if __name__ == "__main__":
    logging.info("Starting application")
    try:
        app = AudioMerger()
        app.run()
    except Exception as e:
        logging.critical("Application crashed:")
        logging.critical(traceback.format_exc())