# Game Chơi Nhạc 🎵🎮

Dự án này là một trò chơi tương tác dựa trên âm nhạc, được phát triển bằng Python và Pygame. Trò chơi kết hợp các kỹ thuật tạo âm thanh, gameplay tương tác và giao diện hấp dẫn để mang lại trải nghiệm thú vị cho người chơi.

## Tính Năng

- **Gameplay Tương Tác**: 
  - Chọn một nhạc cụ (Piano, Trống, Guitar) và chơi theo các nốt nhạc rơi xuống.
  
- **Tạo Âm Thanh Tùy Chỉnh**: 
  - Sử dụng các kỹ thuật tổng hợp âm thanh như thuật toán Karplus-Strong để tạo âm thanh guitar, bao bọc ADSR và lọc thông thấp.
  
- **Tích Hợp Đa Phương Tiện**: 
  - Hỗ trợ phát âm thanh bằng thư viện `simpleaudio` và tự động tạo file âm thanh làm tài nguyên cho trò chơi.
  
- **Giao Diện Hấp Dẫn**: 
  - Thiết kế giao diện trực quan, dễ sử dụng, phù hợp với mọi lứa tuổi.

## Hướng Dẫn Cài Đặt

### Yêu Cầu

- Python 3.8 trở lên.
- Các thư viện Python:
  - `pygame`
  - `numpy`
  - `scipy`
  - `pydub`
  - `simpleaudio`

### Cài Đặt Thư Viện
pip install pygame numpy scipy pydub simpleaudio

### Chạy Trò Chơi

1. **Cấu hình đường dẫn**:  
   Trong mã nguồn, đảm bảo thay đổi biến `path` trong file chính sang đường dẫn của dự án trên máy:  
   path = "E:/Hoc_tap/UET/Nam4/Ki1/DSP/BTL/"

1. **Chạy file chính**:  
  python main.py

### Cách Chơi
- Bắt đầu
Khởi động trò chơi, chọn "Start" từ menu chính.
- Cài đặt nhạc cụ
Trong mục "Settings", chọn nhạc cụ mà bạn muốn sử dụng: Piano, Trống hoặc Guitar.
- Chơi
Sử dụng các phím mũi tên Trái và Phải để tương tác với các nốt nhạc rơi xuống.
Nhấn đúng phím để ghi điểm.
- Kết thúc
Kết quả sẽ được hiển thị ở cuối trò chơi. Hãy xem bạn đã ghi được bao nhiêu điểm!


### Thư Mục Chính
- Audio/: Chứa các file âm thanh của các nốt nhạc đã được tạo tự động.
- Image/: Lưu trữ các tài nguyên hình ảnh như nút bấm, biểu tượng, hình nền.
- Data/: Các file văn bản chứa thông tin về chuỗi nốt nhạc.
- main.py: Mã nguồn chính của trò chơi.

### Thư Viện Sử Dụng
- Pygame: Thư viện cho phát triển game.
- NumPy: Hỗ trợ tính toán số học và xử lý dữ liệu.
- SciPy: Cung cấp các thuật toán và kỹ thuật xử lý tín hiệu.
- Pydub: Quản lý file âm thanh dễ dàng.
- Simpleaudio: Phát âm thanh đơn giản từ file WAV.


### Các Hàm Chính
- Hàm lowpass_filter(data, cutoff, fs, order=5): Tạo bộ lọc thông thấp để làm mượt âm thanh.
- Hàm karplus_strong(freq, duration, sampling_rate, decay_factor=0.995):
- Tạo âm thanh guitar dựa trên thuật toán Karplus-Strong.
- Sử dụng ngẫu nhiên để tạo âm thanh ban đầu và áp dụng bộ lọc thông thấp.
- Hàm generate_drum_sound(note_freq, duration, sampling_rate):
- Tạo âm thanh trống bằng cách kết hợp sóng sin và noise.
- Hàm generate_piano_sound(freq, duration, sampling_rate):
- Tạo âm thanh piano bằng cách sử dụng sóng sin.
- Hàm adsr_envelope(wave, instrument, sampling_rate):
- Tạo bao ADSR (Attack, Decay, Sustain, Release) cho các nhạc cụ.
- Dữ Liệu Tần Số
  Frequencies: Định nghĩa tần số cho các nốt nhạc từ C4 đến B4.
- Tạo và Xuất File Âm Thanh
- Hàm create_individual_files(duration=1, sampling_rate=44100):
- Tạo và xuất file âm thanh cho từng nhạc cụ.
Phát Âm Thanh
- Hàm playAudio(tenNot, loaiNhacCu):
- Phát âm thanh từ file tương ứng với nốt nhạc và nhạc cụ đã chọn.

### Đóng Góp
Mọi ý kiến đóng góp hoặc bản cập nhật đều được hoan nghênh. Hãy gửi mail: vuduc25022003@gmail.com để đóng góp cho dự án.
