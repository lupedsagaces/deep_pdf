import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, font, ttk
from tkhtmlview import HTMLLabel
import platform
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import pytesseract
from PyPDF2 import PdfReader, PdfWriter
import tempfile

# Function to search for text in a PDF file.
def search_text_in_pdf(pdf_path, search_text):
    try:
        document = fitz.open(pdf_path)
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text = page.get_text("text")
            if search_text.lower() in text.lower():
                return True
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return False

# Function to search for text in all PDF files in a directory and its subdirectories.
def search_pdfs_in_directory(directory, search_text, progress_callback=None):
    matching_pdfs = []
    pdf_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))

    total_files = len(pdf_files)
    for i, pdf_path in enumerate(pdf_files):
        if search_text_in_pdf(pdf_path, search_text):
            matching_pdfs.append(pdf_path)
        if progress_callback:
            progress_callback(i + 1, total_files)

    return matching_pdfs

def browse_directory():
    directory = filedialog.askdirectory()
    entry_directory.delete(0, tk.END)
    entry_directory.insert(0, directory)

def open_file_location(event):
    widget = event.widget
    href_start = widget.index(f"@{event.x},{event.y}")
    href_end = widget.index(f"@{event.x},{event.y} wordend")
    href = widget.get(href_start, href_end)
    if href.startswith("file://"):
        file_path = href.replace("file://", "")
        file_dir = os.path.dirname(file_path)
        os.startfile(file_dir)

def update_progress(current, total):
    progress_var.set(current)
    progress_bar["maximum"] = total

def search_thread(directory, search_text):
    global html_content
    html_content = "<p>Os seguintes arquivos contêm o conteúdo da busca:</p><ul>"
    matching_pdfs = search_pdfs_in_directory(directory, search_text, update_progress)

    if matching_pdfs:
        for pdf in matching_pdfs:
            html_content += f'<li><a href="{pdf}" style="color: blue; font-weight: bold;">{pdf}</a></li>'
        save_button.config(state=tk.NORMAL)
        clear_button.config(state=tk.NORMAL)
    else:
        html_content = "<p>Nenhum arquivo encontrado</p>"
        save_button.config(state=tk.DISABLED)
        clear_button.config(state=tk.DISABLED)

    html_content += "</ul>"
    results.set_html(html_content)

    # Update the count of found files
    result_count_label.config(text=f"Arquivos encontrados: {len(matching_pdfs)}")

    progress_bar.grid_remove()

    # Re-enable buttons after search
    search_button.config(state=tk.NORMAL)
    browse_button.config(state=tk.NORMAL)
    clear_button.config(state=tk.NORMAL)

def start_search():
    directory = entry_directory.get()
    search_text = entry_search_text.get()

    if not directory or not search_text:
        messagebox.showwarning("Input Error", "Please provide both directory and search text.")
        return

    result_count_label.config(text="")
    progress_var.set(0)
    progress_bar.grid(row=2, column=1, padx=5, pady=5)
    save_button.config(state=tk.DISABLED)
    

    # Disable buttons while search is in progress
    search_button.config(state=tk.DISABLED)
    browse_button.config(state=tk.DISABLED)
    clear_button.config(state=tk.DISABLED)

    search_thread_instance = threading.Thread(target=search_thread, args=(directory, search_text))
    search_thread_instance.start()

def save_files():
    destination_folder = filedialog.askdirectory()
    if not destination_folder:
        messagebox.showwarning("Input Error", "Please select a destination folder.")
        return

    for item in html_content.split("<li>")[1:]:
        file_path = item.split('"')[1]
        file_name = os.path.basename(file_path)
        shutil.copy(file_path, os.path.join(destination_folder, file_name))

    messagebox.showinfo("Success", "Files copied successfully.")

def clear_fields():
    if messagebox.askyesno("Confirmar Limpeza", "Tem certeza de que deseja limpar a pesquisa?"):
        entry_directory.delete(0, tk.END)
        entry_search_text.delete(0, tk.END)
        global html_content
        html_content = "<p>Resultados aparecerão aqui</p>"
        results.set_html(html_content)
        result_count_label.config(text="")
        save_button.config(state=tk.DISABLED)
        clear_button.config(state=tk.DISABLED)

def select_files():

    files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    if files:
        convert_pdfs_to_searchable(files)

def reset_ocr_label():
    ocr_label.config(text="Selecione PDFs não pesquisáveis:")

def convert_pdfs_to_searchable(file_paths):
    output_dir = filedialog.askdirectory(title="Selecione a pasta para salvar os PDFs convertidos")
    if not output_dir:
        return

    ocr_label.config(text="Convertendo... Por favor, aguarde!")
    progress_var.set(0)
    progress_bar.grid(row=7, column=1, padx=5, pady=5)
    ocr_button.config(state=tk.DISABLED)

    def ocr_thread(file_paths, output_dir):
        total_files = len(file_paths)
        for i, file_path in enumerate(file_paths):
            convert_pdf_to_searchable(file_path, output_dir)
            update_progress(i + 1, total_files)

        ocr_label.config(text="Conversão concluída!")
        root.after(3000, reset_ocr_label)

        ocr_button.config(state=tk.NORMAL)
        progress_bar.grid_remove()

    ocr_thread_instance = threading.Thread(target=ocr_thread, args=(file_paths, output_dir))
    ocr_thread_instance.start()

def convert_pdf_to_searchable(file_path, output_dir):
    doc = fitz.open(file_path)
    pdf_writer = PdfWriter()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        zoom = 2  # Increase this value for higher resolution
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Save temporary image
        temp_img_path = "temp_image.png"
        img.save(temp_img_path)

        # Apply OCR to the image
        ocr_pdf_bytes = pytesseract.image_to_pdf_or_hocr(temp_img_path, extension='pdf')

        # Save OCR result to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf_file:
            temp_pdf_file.write(ocr_pdf_bytes)
            temp_pdf_file_path = temp_pdf_file.name

        pdf_reader = PdfReader(temp_pdf_file_path)
        ocr_page = pdf_reader.pages[0]
        pdf_writer.add_page(ocr_page)

        # Remove temporary image and file
        os.remove(temp_img_path)
        os.remove(temp_pdf_file_path)

    output_path = os.path.join(output_dir, os.path.basename(file_path).replace(".pdf", "_pesquisavel.pdf"))
    with open(output_path, "wb") as f:
        pdf_writer.write(f)

# Create the main application window
root = tk.Tk()
root.title("Deep PDF")

# Check if the OS is Windows
if platform.system() == "Windows":
    icon_path = "./icon/ico.ico"
    root.iconbitmap(icon_path)

# Custom font for all widgets
custom_font = font.Font(size=12)

# Directory selection
tk.Label(root, text="Diretório:", font=custom_font).grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_directory = tk.Entry(root, width=50, font=custom_font)
entry_directory.grid(row=0, column=1, padx=10, pady=5)
browse_button = tk.Button(root, text="Abrir", command=browse_directory, font=custom_font)
browse_button.grid(row=0, column=2, padx=10, pady=5)

# Search text entry
tk.Label(root, text="Buscar texto:", font=custom_font).grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_search_text = tk.Entry(root, width=50, font=custom_font)
entry_search_text.grid(row=1, column=1, padx=10, pady=5)

# Search button
search_button = tk.Button(root, text="Buscar", command=start_search, font=custom_font)
search_button.grid(row=1, column=2, padx=10, pady=5)

# Progress bar
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate", variable=progress_var)
progress_bar.grid(row=2, column=2, padx=10, pady=5)
progress_bar.grid_remove()  # Hide the progress bar initially

# Results display
results = HTMLLabel(root, width=80, height=20, background="white", html="<p>Resultados aparecerão aqui</p>")
results.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
results.bind("<Button-1>", open_file_location)  # Bind click event to open file location

# Result count label
result_count_label = tk.Label(root, text="", font=custom_font)
result_count_label.grid(row=4, column=0, columnspan=3)

# Save button
save_button = tk.Button(root, text="Salvar Arquivos", command=save_files, font=custom_font, state=tk.DISABLED)
save_button.grid(row=5, column=0, padx=10, pady=5)

# Clear button
clear_button = tk.Button(root, text="Limpar a pesquisa", command=clear_fields, font=custom_font, state=tk.DISABLED)
clear_button.grid(row=5, column=2, padx=10, pady=5)

# OCR conversion section
ocr_label = tk.Label(root, text="Selecione PDFs não pesquisáveis:", font=custom_font)
ocr_label.grid(row=6, column=0,padx=10, pady=10)

ocr_button = tk.Button(root, text="Converter PDFs para OCR", command=select_files, font=custom_font)
ocr_button.grid(row=6, column=1, padx=10, pady=10)

# Progress bar for OCR conversion
ocr_progress_var = tk.IntVar()
ocr_progress_bar = ttk.Progressbar(root, orient="horizontal", length=50, mode="determinate", variable=ocr_progress_var)
ocr_progress_bar.grid(row=6, column=2, padx=5, pady=5)
ocr_progress_bar.grid_remove()  # Hide the progress bar initially

# Start the application
root.mainloop()
