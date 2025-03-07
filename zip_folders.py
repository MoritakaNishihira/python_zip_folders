import os
import zipfile
import shutil
from concurrent.futures import ThreadPoolExecutor
from tkinter import Tk
from tkinter.filedialog import askdirectory
import traceback
from tqdm import tqdm  # 進捗バーを表示するためのライブラリ

def log_message(message, level="INFO"):
    with open("process_log.txt", "a") as log_file:
        log_file.write(f"{level}: {message}\n")
    print(message)

def zip_folder(folder_path, zip_file_path):
    try:
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=folder_path)
                    zipf.write(file_path, arcname)
        log_message(f"'{os.path.basename(folder_path)}'フォルダを圧縮しました: {zip_file_path}")
        return True
    except Exception as e:
        error_message = f"圧縮中にエラーが発生しました: {e}\n{traceback.format_exc()}"
        log_message(error_message, level="ERROR")
        return False

def delete_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        log_message(f"'{os.path.basename(folder_path)}'フォルダを削除しました。")
        return True
    except Exception as e:
        error_message = f"フォルダ '{os.path.basename(folder_path)}' の削除中にエラーが発生しました: {e}\n{traceback.format_exc()}"
        log_message(error_message, level="ERROR")
        return False

def process_folder(directory_path, folder_name, progress_bar):
    folder_path = os.path.join(directory_path, folder_name)
    zip_file_path = generate_unique_zip_path(directory_path, folder_name)
    
    if zip_folder(folder_path, zip_file_path):
        if not delete_folder(folder_path):
            log_message(f"'{folder_name}'フォルダの削除に失敗しました。", level="WARNING")
    else:
        log_message(f"'{folder_name}'フォルダの圧縮に失敗しました。", level="WARNING")
    
    progress_bar.update(1)

def generate_unique_zip_path(directory_path, folder_name):
    base_zip_file_path = os.path.join(directory_path, f"{folder_name}.zip")
    count = 1
    while os.path.exists(base_zip_file_path):
        base_zip_file_path = os.path.join(directory_path, f"{folder_name}_{count}.zip")
        count += 1
    return base_zip_file_path

def zip_folders_in_directory(directory_path):
    folder_names = [folder_name for folder_name in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, folder_name))]
    
    with ThreadPoolExecutor() as executor, tqdm(total=len(folder_names), desc="フォルダの処理進捗") as progress_bar:
        for folder_name in folder_names:
            executor.submit(process_folder, directory_path, folder_name, progress_bar)

def select_directory():
    root = Tk()
    root.withdraw()
    directory_path = askdirectory(title="フォルダを選択")
    
    if directory_path:
        zip_folders_in_directory(directory_path)
    else:
        log_message("ディレクトリが選択されませんでした。", level="INFO")

select_directory()
