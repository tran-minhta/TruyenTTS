import os
import re
import sys
import yaml
import subprocess
import signal
import threading
from parsers import BookParser

# 1. Khai báo Bộ đọc chạy ngầm bằng Thread hệ thống
class CLIPiperEngine:
    def __init__(self, sentences, model_path):
        self.sentences = sentences
        self.model_path = model_path
        self.current_index = 0
        self.is_running = True
        self.process = None
        self.config_path = model_path + ".json"

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while self.current_index < len(self.sentences) and self.is_running:
            sentence = self.sentences[self.current_index].strip()
            if not sentence:
                self.current_index += 1
                continue

            # In câu đang đọc lên màn hình CLI
            print(f"\r[Đang đọc {self.current_index + 1}/{len(self.sentences)}]: {sentence}", end="", flush=True)

            # Thay thế aplay bằng lệnh play (Sox) để xử lý dữ liệu thô (raw) mượt mà hơn
            cmd = f'echo "{sentence}" | python3 -m piper --model {self.model_path} --config {self.config_path} --output-raw | play -t raw -r 22050 -e signed-integer -b 16 -c 1 -'
            
            self.process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.process.wait()
            
            self.current_index += 1
        if self.is_running:
            print("\n[+] Đã đọc xong toàn bộ truyện!")

    def stop(self):
        self.is_running = False
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            except Exception:
                pass

# 2. Điều khiển chính của CLI
def main():
    print("\n" + "="*50)
    print("        TRUYENTTS - PHIÊN BẢN TERMUX CLI")
    print("="*50)

    config_path = "config.yaml"
    if not os.path.exists(config_path):
        print("[-] Chưa có config.yaml, vui lòng kiểm tra lại vị trí file.")
        return
        
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        model_path = config.get("path_models", "").strip()
        books_dir = config.get("books_dir", "./books").strip()

    model_path = os.path.abspath(model_path)
    print(f"[*] Đường dẫn Model: {model_path}")

    # Tự động quét thư mục truyện được chỉ định
    file_path = ""
    supported_extensions = ('.txt', '.epub', '.pdf', '.mobi', '.fb2')
    
    if os.path.exists(books_dir) and os.path.isdir(books_dir):
        scanned_books = [
            os.path.join(books_dir, f) for f in os.listdir(books_dir) 
            if f.lower().endswith(supported_extensions) and os.path.isfile(os.path.join(books_dir, f))
        ]
        
        if scanned_books:
            print(f"\n[+] Tìm thấy {len(scanned_books)} truyện trong thư mục '{books_dir}':")
            for idx, book in enumerate(scanned_books):
                print(f"  [{idx + 1}] {os.path.basename(book)}")
            print("  [0] Nhập đường dẫn thủ công bên ngoài")
            
            try:
                choice = int(input("\n[?] Chọn số thứ tự truyện muốn đọc: ").strip())
                if choice == 0:
                    file_path = input("[?] Nhập đường dẫn file truyện cần đọc: ").strip()
                elif 1 <= choice <= len(scanned_books):
                    file_path = scanned_books[choice - 1]
                else:
                    print("[-] Lựa chọn không hợp lệ!")
                    return
            except ValueError:
                print("[-] Vui lòng chỉ nhập số thứ tự!")
                return
        else:
            print(f"\n[-] Thư mục '{books_dir}' đang trống.")
            file_path = input("[?] Nhập đường dẫn file truyện thủ công: ").strip()
    else:
        print(f"\n[-] Không tìm thấy thư mục '{books_dir}'.")
        file_path = input("[?] Nhập đường dẫn file truyện thủ công: ").strip()

    if not file_path or not os.path.exists(file_path):
        print(f"[-] Lỗi: Không tìm thấy file truyện tại '{file_path}'")
        return

    print(f"\n[*] Đang mở file: {os.path.basename(file_path)}")
    print("[*] Đang bóc tách nội dung văn bản...")
    try:
        full_text = BookParser.get_text(file_path)
        sentences = re.split(r'(?<=[.!?…])\s+', full_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        print(f"[+] Tổng số câu: {len(sentences)}")
        print("[*] Bắt đầu phát âm thanh... (Bấm Ctrl+C để dừng)")
        
        engine = CLIPiperEngine(sentences, model_path)
        engine.start()
        
        engine.thread.join()

    except KeyboardInterrupt:
        print("\n[-] Đã nhận lệnh dừng từ người dùng.")
        engine.stop()
    except Exception as e:
        print(f"\n[-] Lỗi hệ thống: {e}")

if __name__ == "__main__":
    main()
