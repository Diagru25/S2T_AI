- cài đặt lib:
#sudo apt install libsndfile1

- Tải 2 thư mục "cache", "model_best" xuống từ link sau:

- chay lenh vao moi truong ao
step 3: chạy môi trường ảo (nếu lỗi -> step 4)
(cmd) -> venv\Scripts\activate.bat
(power shell) -> .\venv\Scripts\activate

step 4: cho phép chạy môi trường ảo (step 3 không lỗi -> bỏ qua bước này)
-> Set-ExecutionPolicy Unrestricted -Scope Process

- sau khi vào môi trường ảo:
#pip install https://github.com/kpu/kenlm/archive/master.zip
#pip install wheel
#pip install -r requirement