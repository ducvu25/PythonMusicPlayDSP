import numpy as np
from scipy.io.wavfile import write
from scipy.signal import butter, lfilter

# Hàm tạo bộ lọc thông thấp
def lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, data)

# Hàm Karplus-Strong cho Guitar
def karplus_strong(freq, duration, sampling_rate, decay_factor=0.995):
    num_samples = int(sampling_rate * duration)
    buffer_len = int(sampling_rate / freq)
    buffer = np.random.uniform(-1, 1, buffer_len)  # Dữ liệu ngẫu nhiên ban đầu
    output = np.zeros(num_samples)

    for i in range(num_samples):
        output[i] = buffer[0]
        avg = decay_factor * 0.5 * (buffer[0] + buffer[1])  # Giảm dần biên độ
        buffer = np.append(buffer[1:], avg)  # Cập nhật bộ đệm

    output = lowpass_filter(output, cutoff=5000, fs=sampling_rate, order=5)
    return output

# Hàm tạo âm thanh trống
def generate_drum_sound(note_freq, duration, sampling_rate):
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    sine_wave = np.sin(2 * np.pi * note_freq * t) * np.exp(-4 * t)  # Sóng sin giảm dần
    #noise = np.random.normal(0, 0.03, len(t)) * np.exp(-5 * t)  # Noise giảm dần
    noise = np.random.normal(0, 0.03, sine_wave.shape)
    drum_sound = sine_wave + noise
    drum_sound = lowpass_filter(drum_sound, cutoff=300, fs=sampling_rate, order=5)
    drum_sound *= 2
    return drum_sound

# Hàm tạo âm thanh piano
def generate_piano_sound(freq, duration, sampling_rate):
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    wave = np.sin(2 * np.pi * freq * t)
    return wave


# Tạo bao ADSR
def adsr_envelope(wave, instrument, sampling_rate):
    if instrument == "piano":
        attack, decay, sustain, release = 0.01, 0.1, 0.3, 0.2
    elif instrument == "guitar":
        attack, decay, sustain, release = 0.02, 0.3, 0.6, 0.4
    elif instrument == "drum":
        attack, decay, sustain, release = 0.01, 0.1, 0.3, 0.2

    total_samples = len(wave)
    attack_samples = int(attack * sampling_rate)
    decay_samples = int(decay * sampling_rate)
    release_samples = int(release * sampling_rate)
    sustain_samples = total_samples - (attack_samples + decay_samples + release_samples)

    attack_env = np.linspace(0, 1, attack_samples)
    decay_env = np.linspace(1, sustain, decay_samples)
    sustain_env = np.ones(sustain_samples) * sustain
    release_env = np.linspace(sustain, 0, release_samples)

    envelope = np.concatenate((attack_env, decay_env, sustain_env, release_env))
    return wave[:len(envelope)] * envelope

# Dữ liệu tần số (C4 đến B4)
frequencies = {
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "B4": 493.88,
}
# Tạo và xuất từng file âm thanh cho mỗi nhạc cụ
def create_individual_files(duration=1, sampling_rate=44100):
    instruments = ["piano", "guitar", "drum"]
    for instrument in instruments:
        instrument_wave = []
        for note, freq in frequencies.items():
            print(f"Generating {note} for {instrument}")

            if instrument == "guitar":
                wave = karplus_strong(freq, duration, sampling_rate)
            elif instrument == "piano":
                wave = generate_piano_sound(freq, duration, sampling_rate)
            elif instrument == "drum":
                wave = generate_drum_sound(freq, duration, sampling_rate)

            wave = adsr_envelope(wave, instrument, sampling_rate)
            wave = np.int16(wave / np.max(np.abs(wave)) * 32767) # Áp dụng ADSR


            filename = f"{instrument}_{note}.wav"
            write(filename, sampling_rate, wave)

import simpleaudio as sa

def extract_notes_from_file(filename):
    notes_array = []
    try:
        with open(filename, "r") as file:
            for line in file:
                # Tách các nốt trong dòng, loại bỏ dấu cách hoặc ký tự xuống dòng
                notes = line.strip().split(", ")
                notes_array.extend(notes)  # Thêm các nốt vào mảng
    except FileNotFoundError:
        print(f"Không tìm thấy file: {filename}")
    except Exception as e:
        print(f"Lỗi xảy ra: {e}")

    return notes_array

def playAudio(tenNot, loaiNhacCu):
    instruments = ["piano", "guitar", "drum"]
    instrument = instruments[loaiNhacCu]  # Lấy tên nhạc cụ
    filename = f"{instrument}_{tenNot}.wav"  # Tạo tên file âm thanh

    try:
        # Phát âm thanh từ file
        wave_obj = sa.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Đợi âm thanh phát xong
    except FileNotFoundError:
        print(f"File {filename} không tồn tại.")
    except Exception as e:
        print(f"Lỗi xảy ra khi phát âm thanh: {e}")
create_individual_files()
# Dữ liệu ban nhạc
banNhac = "C4, D4, E4, G4, A4, B4, C4, B4, A4, G4, E4, D4, C4, E4, G4, A4, F4, E4, D4, C4, B4, A4, G4, F4, E4, D4, C4, B4, A4, G4"

#print("Notes generated:", notes_list)
playAudio('C4', 0)
playAudio('C4', 1)