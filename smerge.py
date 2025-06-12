import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

class AudioMerger:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Audio Merger")
        self.window.geometry("600x400")
        
        self.selected_files = []
        self.output_path = ""
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Files selection button
        self.select_btn = ttk.Button(self.window, text="Select Files", command=self.select_files)
        self.select_btn.pack(pady=10)
        
        # Selected files display
        self.files_label = ttk.Label(self.window, text="Selected files:", wraplength=550)
        self.files_label.pack(pady=5)
        
        # Output filename entry
        self.filename_label = ttk.Label(self.window, text="Output filename:")
        self.filename_label.pack(pady=5)
        self.filename_entry = ttk.Entry(self.window, width=50)
        self.filename_entry.insert(0, "merged_audio")
        self.filename_entry.pack(pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(self.window, length=400, mode='determinate')
        self.progress.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(self.window, text="")
        self.status_label.pack(pady=5)
        
        # Merge button
        self.merge_btn = ttk.Button(self.window, text="Merge Files", command=self.merge_files)
        self.merge_btn.pack(pady=10)

    def update_status(self, message, progress_value):
        self.status_label.config(text=message)
        self.progress['value'] = progress_value
        self.window.update()
        
    def select_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Audio Files", "*.mp3 *.wav")],
            title="Select Audio Files"
        )
        if files:
            def natural_keys(text):
                import re
                def atoi(text):
                    return int(text) if text.isdigit() else text
                return [atoi(c) for c in re.split(r'(\d+)', os.path.basename(text))]
            
            self.selected_files = sorted(files, key=natural_keys)
            self.output_path = os.path.dirname(self.selected_files[0])
            self.update_files_label()
    
    def update_files_label(self):
        files_text = "Selected files: " + ", ".join(
            [os.path.basename(f) for f in self.selected_files]
        )
        self.files_label.config(text=files_text)
    
    def merge_files(self):
        if not self.selected_files:
            messagebox.showwarning("Warning", "Please select files first!")
            return
            
        output_filename = self.filename_entry.get()
        if not output_filename:
            output_filename = "merged_audio"
        
        # Reset progress
        self.progress['value'] = 0
        
        try:
            # Determine output format and path
            self.update_status("Preparing to merge...", 10)
            output_format = os.path.splitext(self.selected_files[0])[1]
            output_path = os.path.join(self.output_path, f"{output_filename}{output_format}")
            
            # Open output file
            self.update_status("Creating output file...", 20)
            with open(output_path, 'wb') as outfile:
                # Process each input file
                file_count = len(self.selected_files)
                progress_per_file = 60 / file_count  # 60% of progress bar for file processing
                
                for i, file in enumerate(self.selected_files, 1):
                    self.update_status(f"Processing file {i} of {file_count}: {os.path.basename(file)}", 
                                     20 + (i * progress_per_file))
                    
                    # Read and write chunks without encoding
                    with open(file, 'rb') as infile:
                        outfile.write(infile.read())
            
            self.update_status("Finalizing...", 90)
            self.update_status("Merge complete!", 100)
            messagebox.showinfo("Success", f"Files merged successfully!\nSaved as: {output_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.update_status("Error occurred during merge", 0)

if __name__ == "__main__":
    app = AudioMerger()
    app.window.mainloop()

git --version