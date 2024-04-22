# Lời nói đầu
Bạn có một bộ manga khá cuốn nhưng lại không biết tiếng Nhật, không biết tiếng Trung? Vậy thì đây có thể là một chương trình bạn đang tìm. Chương trình sẽ tự động tìm văn bản trên ảnh bạn đã cung cấp và trả về ảnh với bản dịch của văn bản đó.

## Hướng dẫn cài đặt
Bạn có thể tải file [.zip](https://drive.google.com/file/d/10mykEfRaxcCkYpoYCmZu0JLSu2n2mIPs/view?usp=drive_link) về và giải nén rồi sử dụng   
Hoặc   
Thực hiện theo các bước sau (ngôn ngữ lập trình python):   
**Bước 1**: Cài đặt miniconda [Nhấn vào đây và làm theo hướng dẫn](https://docs.conda.io/projects/conda/en/4.6.1/user-guide/install/windows.html)   
**Bước 2**: Tải chương trình về bằng cách Download.zip hoặc
```sh
git clone https://github.com/Tranhoangkhanhlinh/Auto_translate.git
```
**Bước 3**: Tạo một thư mục mới, đặt tên manga-ocr-base   
**Bước 4**:    
  **Bước 4.1**: Truy cập [Huggingface](https://huggingface.co/kha-white/manga-ocr-base/tree/main) , tải tất cả file và đưa vào thư mục manga-ocr-base   
  **Bước 4.2**: Nhấp vào đây để tải [Pytesseract](https://github.com/UB-Mannheim/tesseract/wiki), sau đó cài đặt các loại ngôn ngữ chi_sim, chi_tra, jpn, kor, rồi đưa vào thư mục pytesseract   
**Bước 5**: Chạy Miniconda   
**Bước 6**: Tạo môi trường ảo bằng lệnh 
```sh
conda create --name <my-env> 
```
(thay <my-env> bằng tên bạn muốn đặt)   
**Bước 7**: Chạy môi trường ảo bằng lệnh
```sh 
conda activate <my-env> 
```
(thay <my-env> bằng tên bạn muốn đặt)   
**Bước 8**: Chuyển đến thư mục trong Miniconda chứa các file như translate_GUI.py trong conda bằng lệnh 
```sh
cd <path_to_folder> 
```
(Thay <path_to_folder> bằng đường dẫn trên máy của bạn)   
**Bước 9**: Chạy lệnh 
```sh
pip install -r requirements.txt
```
**Bước 10**: Sau khi cài đặt thư viện hoàn tất, sử dụng lệnh 
```sh
python translate_GUI.py để chạy chương trình
```
   
      
## Hướng dẫn chạy chương trình ở những lần tiếp theo (Sau khi đã cài đặt lần đầu và chạy thành công)   
**Bước 1**: Chạy Miniconda   
**Bước 2**: Khởi chạy môi trường ảo bằng lệnh
```sh
conda activate <my-env> 
```
(thay <my-env> bằng tên bạn đã đặt cho môi trường lúc khởi tạo)   
**Bước 3**: Chuyển đến thư mục trong Miniconda chứa các file như translate_GUI.py trong conda bằng lệnh 
```sh
cd <path_to_folder> 
```
(Thay <path_to_folder> bằng đường dẫn trên máy của bạn)   
**Bước 4**: sử dụng lệnh 
```sh
python translate_GUI.py 
```
để chạy chương trình
