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
        self.window.minsize(400, 120)  # Уменьшаем минимальную высоту
        self.window.resizable(True, False)  # Запрещаем изменение высоты окна
        
        self.selected_files = []
        self.output_path = ""
        self.merge_btn = None  # Initialize merge button as None
        
        # Настройка адаптивной сетки
        self.window.grid_columnconfigure(0, weight=1)
        # Убираем растягивание последней строки
        # self.window.grid_rowconfigure(3, weight=1)  # Удаляем эту строку
    
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Files list frame with selected files
        files_frame = ttk.Frame(self.window)
        files_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        files_frame.grid_columnconfigure(0, weight=1)

        self.files_label = ttk.Label(files_frame, wraplength=380)
        self.files_label.grid(row=0, column=0, sticky='ew')

        # Button frame with Select/Merge buttons
        button_frame = ttk.Frame(self.window)
        button_frame.grid(row=1, column=0, pady=5, sticky='ew')
        button_frame.grid_columnconfigure(0, weight=1)

        self.select_btn = ttk.Button(button_frame, text="Select Files", command=self.select_files)
        self.select_btn.grid(row=0, column=0, padx=10, sticky='ew')

        # Progress/Merge frame
        self.progress_frame = ttk.Frame(self.window)
        self.progress_frame.grid(row=2, column=0, pady=5, sticky='ew')
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky='ew', padx=10)
        self.progress.grid_remove()

        self.status_label = ttk.Label(self.progress_frame, text="")
        self.status_label.grid(row=1, column=0, pady=(2,0))
        self.status_label.grid_remove()

        # Merge frame
        self.merge_frame = ttk.Frame(self.window)
        self.merge_frame.grid(row=2, column=0, pady=5, sticky='ew')
        self.merge_frame.grid_columnconfigure(0, weight=1)
        self.merge_frame.grid_remove()

        # Filename frame
        filename_frame = ttk.Frame(self.window)
        filename_frame.grid(row=3, column=0, pady=(0,5), sticky='ew')
        filename_frame.grid_columnconfigure(1, weight=1)

        self.filename_label = ttk.Label(filename_frame, text="Output filename:")
        self.filename_label.grid(row=0, column=0, padx=5)
        self.filename_entry = ttk.Entry(filename_frame)
        self.filename_entry.insert(0, "merged_audio")
        self.filename_entry.grid(row=0, column=1, sticky='ew', padx=5)

        # Bind window resize event
        self.window.bind('<Configure>', self.on_window_resize)

    def on_window_resize(self, event):
        # Update label wraplength when window is resized
        if hasattr(self, 'files_label'):
            self.files_label.configure(wraplength=event.width - 40)

    def update_status(self, message, progress_value):
        self.status_label.config(text=message)
        self.progress['value'] = progress_value
        self.window.update()
        
    def select_files(self):
        logging.info("Opening file selection dialog")
        try:
            files = filedialog.askopenfilenames(
                filetypes=[("Audio Files", "*.mp3 *.wav")],
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
                self.update_files_label()
            else:
                logging.info("No files selected")
        except Exception as e:
            logging.error(f"Error in file selection: {str(e)}")
            logging.error(traceback.format_exc())
            messagebox.showerror("Error", f"Error selecting files: {str(e)}")

    def update_files_label(self):
        files_text = "Selected files: " + ", ".join(
            [os.path.basename(f) for f in self.selected_files]
        )
        self.files_label.config(text=files_text)
    
        # Show/hide appropriate elements
        if self.selected_files:
            # Create and show merge button if files are selected
            if not self.merge_btn:
                self.merge_btn = ttk.Button(self.merge_frame, text="Merge Files", command=self.merge_files)
                self.merge_btn.grid(row=0, column=0, padx=5, sticky='ew')
            self.progress.grid_remove()
            self.status_label.grid_remove()
            self.merge_frame.grid()
        else:
            # Hide merge button if no files
            if self.merge_btn:
                self.merge_btn.grid_remove()
            self.merge_frame.grid_remove()

    def merge_files(self):
        if not self.selected_files:
            logging.warning("Attempted to merge with no files selected")
            messagebox.showwarning("Warning", "Please select files first!")
            return
        
        logging.info("Starting file merge process")
        self.merge_frame.grid_remove()
        self.progress.grid()
        self.status_label.grid()
        self.progress['value'] = 0
        
        try:
            output_filename = self.filename_entry.get()
            logging.info(f"Output filename: {output_filename}")
            
            self.update_status("Preparing to merge...", 10)
            output_format = os.path.splitext(self.selected_files[0])[1]
            output_path = os.path.join(self.output_path, f"{output_filename}{output_format}")
            logging.debug(f"Full output path: {output_path}")
            
            self.update_status("Creating output file...", 20)
            with open(output_path, 'wb') as outfile:
                file_count = len(self.selected_files)
                progress_per_file = 60 / file_count
                
                for i, file in enumerate(self.selected_files, 1):
                    current_file = os.path.basename(file)
                    logging.info(f"Processing file {i}/{file_count}: {current_file}")
                    self.update_status(f"Processing file {i} of {file_count}: {current_file}", 
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
        
        self.progress.grid_remove()
        self.status_label.grid_remove()
        self.merge_frame.grid()

if __name__ == "__main__":
    logging.info("Starting application")
    try:
        app = AudioMerger()
        app.window.mainloop()
    except Exception as e:
        logging.critical("Application crashed:")
        logging.critical(traceback.format_exc())