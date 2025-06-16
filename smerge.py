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

        self.window.minsize(500, 210)  # Увеличили минимальную высоту со 120 до 210
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
                           foreground='#29FFA9',  # Зеленый цветт как у кнопки merge
                           font=('Segoe UI', 10, 'bold'))  # Добавили 'bold'
        
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

        # Фиолетовая кнопка для merge
        self.style.configure('Blue.TButton',
                           background='#9D7CFF',  # Фиолетовый
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(15, 10))

        self.style.map('Blue.TButton',
                      background=[('active', '#B49DFF'),  # Светло-фиолетовый при наведении
                                ('pressed', '#9D7CFF')])

        # Серая кнопка для change selection (темнее)
        self.style.configure('Gray.TButton',
                           background='#4b5563',  # Темно-серый
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(20, 12))

        self.style.map('Gray.TButton',
                      background=[('active', '#6b7280'),  # Серый при наведении
                                ('pressed', '#4b5563')])
        
        # Настройка стилей для Entry
        self.style.configure('Dark.TEntry',
                           fieldbackground='#141E1B',  # Основной фон
                           background='#141E1B',  # Основной фон
                           foreground=self.colors['text'],
                           bordercolor=self.colors['border'],
                           insertcolor=self.colors['text'],
                           font=('Segoe UI', 10),
                           padding=8)
        
        self.style.map('Dark.TEntry',
                      bordercolor=[('focus', '#9D7CFF')],  # Фиолетовая подсветка при фокусе
                      fieldbackground=[('focus', '#374151')])  # Немного светлее фон при фокусе
        
        # Настройка стилей для Progressbar
        self.style.configure('Dark.Horizontal.TProgressbar',
                           background='#9D7CFF',  # Фиолетовый цвет как у кнопки merge
                           troughcolor=self.colors['secondary_bg'],
                           borderwidth=0,
                           lightcolor='#9D7CFF',  # Фиолетовый цвет
                           darkcolor='#9D7CFF')   # Фиолетовый цвет)
        
    def create_widgets(self):
        # Основной контейнер с отступами
        main_container = ttk.Frame(self.window, style='Dark.TFrame')
        main_container.grid(row=0, column=0, sticky='nsew', padx=20, pady=(8, 10))  # Увеличили нижний отступ с 5 до 10
        main_container.grid_columnconfigure(0, weight=1)

        # Кнопка выбора файлов (без иконки)
        self.select_btn = ttk.Button(main_container, text="Change Selection", 
                                   command=self.select_files, style='Gray.TButton')
        self.select_btn.grid(row=0, column=0, pady=(0, 6), sticky='ew')  # Изменили row с 1 на 0
        
        # Фрейм для информации о файлах
        self.files_info_frame = ttk.Frame(main_container, style='Dark.TFrame')
        self.files_info_frame.grid(row=1, column=0, pady=(0, 8), sticky='ew')  # Изменили row с 2 на 1
        self.files_info_frame.grid_columnconfigure(0, weight=1)
        
        # Лейбл с информацией о количестве файлов и пути (обычный шрифт)
        self.files_info_label = ttk.Label(self.files_info_frame, text="", style='Files.TLabel', 
                                        wraplength=350, justify='left')
        self.files_info_label.grid(row=0, column=0, sticky='ew')
        
        # Лейбл со списком файлов (жирный шрифт)
        self.files_list_label = ttk.Label(self.files_info_frame, text="", style='FilesBold.TLabel', 
                                        wraplength=350, justify='left')
        self.files_list_label.grid(row=1, column=0, sticky='ew')
        
        # Карточка настроек вывода
        self.output_card = ttk.Frame(main_container, style='Card.TFrame')

        self.output_card.grid(row=2, column=0, sticky='ew', pady=(0, 8))  # Изменили row с 3 на 2
        self.output_card.grid_columnconfigure(1, weight=1)
        
        filename_label = ttk.Label(self.output_card, text="Filename:", style='Card.TLabel')
        filename_label.grid(row=0, column=0, padx=15, pady=(10, 10), sticky='w')
        
        self.filename_entry = ttk.Entry(self.output_card, style='Dark.TEntry')
        self.filename_entry.grid(row=0, column=1, sticky='ew', padx=(10, 15), pady=(10, 10))
        
        # Привязываем нажатие Enter к функции объединения файлов
        self.filename_entry.bind('<Return>', lambda event: self.merge_files())
        
        # Прогресс бар и статус (скрыт изначально)
        self.progress_frame = ttk.Frame(main_container, style='Dark.TFrame')

        self.progress_frame.grid(row=3, column=0, sticky='ew', pady=(0, 8))  # Изменили row с 4 на 3
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_remove()  # Скрываем изначально
        
        self.progress = ttk.Progressbar(self.progress_frame, mode='determinate', style='Dark.Horizontal.TProgressbar')
        self.progress.grid(row=0, column=0, sticky='ew', pady=(0, 4))
        
        self.status_label = ttk.Label(self.progress_frame, text="", style='Status.TLabel')
        self.status_label.grid(row=1, column=0)
        
        # Кнопка объединения (скрыта до загрузки файлов)
        self.merge_frame = ttk.Frame(main_container, style='Dark.TFrame')

        self.merge_frame.grid(row=4, column=0, sticky='ew')  # Изменили row с 5 на 4
        self.merge_frame.grid_columnconfigure(0, weight=1)
        self.merge_frame.grid_remove()  # Скрываем до загрузки файлов
        

        self.merge_btn = ttk.Button(self.merge_frame, text="Merge Audio Files", 
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
        
        # Получаем текущий минимальный размер
        current_min_width = self.window.minsize()[0]
        
        # Ширину оставляем как есть, только высоту обновляем


        min_width = current_min_width
        min_height = max(200, req_height + 20)  # Уменьшили запас с 40 до 20
        
        self.window.minsize(min_width, min_height)
        
        # Если текущий размер окна меньше требуемого по высоте, увеличиваем его
        current_width = self.window.winfo_width()
        current_height = self.window.winfo_height()
        
        if current_height < min_height:

            self.window.geometry(f"{current_width}x{min_height}")

    def on_window_resize(self, event):
        # Update label wraplength when window is resized
        if event.widget == self.window:
            # Адаптивная ширина с минимумом для правильного переноса слов
            new_width = max(300, event.width - 80)
            if hasattr(self, 'files_info_label'):
                self.files_info_label.configure(wraplength=new_width)
            if hasattr(self, 'files_list_label'):
                self.files_list_label.configure(wraplength=new_width)

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
                




                # Создаем интерфейс только после выбора файлов
                if not self.interface_created:
                    self.create_widgets()
                    self.window.deiconify()  # Показываем окно
                

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
        files_names = [f"[{os.path.basename(f)}]" for f in self.selected_files]
        folder_path = os.path.dirname(self.selected_files[0])
        
        # Разделяем на два лейбла: информация и список файлов
        info_text = f"Selected {files_count} files from {folder_path}:"
        files_text = ', '.join(files_names)
        
        self.files_info_label.config(text=info_text)
        self.files_list_label.config(text=files_text)

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
        
        # Показать прогрессбар
        self.progress_frame.grid()
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
            self.update_status("Files loaded successfully!", 100)
            
            # Небольшая пауза перед показом интерфейса объединения
            self.window.after(500, self.show_merge_interface)
            
        except Exception as e:
            logging.error("Error during files loading:")
            logging.error(traceback.format_exc())
            self.update_status(f"Error loading files: {str(e)}", 0)
        finally:
            # Включить кнопку выбора обратно
            self.select_btn.config(state='normal')

    def show_merge_interface(self):
        """Показывает интерфейс для объединения после загрузки файлов"""
        # Скрыть прогрессбар загрузки
        self.progress_frame.grid_remove()
        
        # Показать кнопку объединения
        self.merge_frame.grid()
        
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
        
        # Показать прогресс, скрыть кнопку объединения
        self.merge_frame.grid_remove()
        self.progress_frame.grid()
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
            self.filename_entry.config(state='disabled')  # Оставляем отключенным до нового объединения
        
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
        
        if is_error:
            # Для ошибок показываем весь текст обычным стилем
            completion_label = ttk.Label(self.completion_frame, text=message, 
                                       style='Dark.TLabel', justify='left',
                                       font=('Segoe UI', 10))

            completion_label.grid(row=0, column=0, pady=(0, 8), sticky='w')  # Уменьшили с 10 до 8
        else:
            # Для успеха разделяем сообщение на части
            lines = message.split('\n')
            

            # Первая строка голубым цветом и жирным шрифтом
            success_label = ttk.Label(self.completion_frame, text=lines[0], 
                                    style='Success.TLabel', justify='left')

            success_label.configure(font=('Segoe UI', 10, 'bold'))
            success_label.grid(row=0, column=0, sticky='w')
            
            # Остальные строки обычным цветом
            if len(lines) > 1:
                remaining_text = '\n'.join(lines[1:])
                details_label = ttk.Label(self.completion_frame, text=remaining_text, 
                                        style='Dark.TLabel', justify='left',
                                        font=('Segoe UI', 10))

                details_label.grid(row=1, column=0, pady=(2, 8), sticky='w')  # Уменьшили с 10 до 8
            else:
                # Если только одна строка, добавляем отступ

                success_label.grid(pady=(0, 8))  # Уменьшили с 10 до 8
        
        # Кнопка для нового объединения
        new_merge_btn = ttk.Button(self.completion_frame, text="Merge Again", 
                                 command=self.reset_for_new_merge, style='Blue.TButton')
        new_merge_btn.grid(row=2, column=0, sticky='ew')
        
        # Показать фрейм завершения
        self.completion_frame.grid(row=4, column=0, sticky='ew')
        self.completion_frame.grid_columnconfigure(0, weight=1)
        
        # Обновить размер окна после добавления элементов
        self.window.after(50, self.update_min_size)

    def reset_for_new_merge(self):
        """Сброс интерфейса для нового объединения"""
        # Скрыть фрейм завершения
        if hasattr(self, 'completion_frame'):
            self.completion_frame.grid_remove()
        
        # Включить поле ввода обратно
        self.filename_entry.config(state='normal')
        
        # Показать обратно кнопку merge
        self.merge_frame.grid()
        
        # Установить фокус на поле ввода
        self.focus_filename_entry()

if __name__ == "__main__":
    logging.info("Starting application")
    try:
        app = AudioMerger()
        app.window.mainloop()
    except Exception as e:
        logging.critical("Application crashed:")
        logging.critical(traceback.format_exc())