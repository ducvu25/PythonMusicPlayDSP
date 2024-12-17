import pygame
import random
import math
from pydub import AudioSegment
from pydub.playback import play
import wave
import numpy as np
import simpleaudio as sa
from scipy.io.wavfile import write
from scipy.signal import butter, lfilter


path = "C:/Learn/PythonMusicPlayDSP/BTL/"

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
instruments = ["piano", "drum", "guitar"]
    
# Tạo và xuất từng file âm thanh cho mỗi nhạc cụ
def create_individual_files(duration=1, sampling_rate=44100):
    for instrument in instruments:
        instrument_wave = []
        for note, freq in frequencies.items():
            print(f"Generating {note} for {instrument}")

            if instrument == "guitar":
                wave2 = karplus_strong(freq, duration, sampling_rate)
            elif instrument == "piano":
                wave2 = generate_piano_sound(freq, duration, sampling_rate)
            elif instrument == "drum":
                wave2 = generate_drum_sound(freq, duration, sampling_rate)

            wave2 = adsr_envelope(wave2, instrument, sampling_rate)
            wave2 = np.int16(wave2 / np.max(np.abs(wave2)) * 32767) # Áp dụng ADSR


            filename = f"{path}Audio/{instrument}_{note}.wav"
            write(filename, sampling_rate, wave2)

def export_audio(notes, instrument, output_file="output_notes.wav", sampling_rate=44100):
    combined_wave = np.array([], dtype=np.float32)
    print(notes)
    # Tạo sóng âm cho từng nốt và nối vào mảng tổng hợp
    combined_audio = AudioSegment.empty()  # Tạo một AudioSegment rỗng
    
    for note in notes:
        file = f"{path}Audio/{instrument}_{note}.wav"
        print(file)
        audio = AudioSegment.from_wav(file)  # Đọc file WAV
        combined_audio += audio  # Ghép file hiện tại vào đoạn âm thanh tổng hợp

    combined_audio.export(output_file, format="wav")  # Xuất file âm thanh
    print(f"File âm thanh '{output_file}' đã được ghép thành công!")


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
    instrument = instruments[loaiNhacCu]  # Lấy tên nhạc cụ
    filename = f"{path}Audio/{instrument}_{tenNot}.wav"  # Tạo tên file âm thanh

    try:
        # Phát âm thanh từ file
        wave_obj = sa.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()
        #play_obj.wait_done()  # Đợi âm thanh phát xong
    except FileNotFoundError:
        print(f"File {filename} không tồn tại.")
    except Exception as e:
        print(f"Lỗi xảy ra khi phát âm thanh: {e}")
create_individual_files()

# kichs thuowsc man hinh
width = 1200
height = 800
YELLOW = (255, 255, 0)
fpsclock = pygame.time.Clock() # thoi gian game
FPS = 30  # frame
pygame.init()

pygame.mixer.init()
audio_click = pygame.mixer.Sound(path + "Audio/audioClick.mp3")
audio_sai = pygame.mixer.Sound(path + "Audio/audioSai.mp3")

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Music Player")
font = pygame.font.Font(None, 36)


class Button:
    def __init__(self, link, scale, index):
        self.surface =  pygame.image.load(link).convert_alpha()
        self.w, self.h = self.surface.get_size()# lấy kích thước ảnh
        self.scale = scale
        self.x, self.y = index   
    
    def draw(self):
        surface_tempt = pygame.transform.scale(self.surface, (self.w *self.scale[0], self.h*self.scale[1]))
        screen.blit(surface_tempt, (self.x - self.w *self.scale[0]/2, self.y - self.h*self.scale[1]/2))
        
    def click(self, x, y):
        if(x > self.x - self.w*self.scale[0]/2 and x < self.x + self.w*self.scale[0]/2 
           and y > self.y - self.h*self.scale[1]/6 and y < self.y + self.h*self.scale[1]/6):
                audio_click.play()
                return True
        return False

class IconShow:
    def __init__(self, link, scale, index):
        self.surface1 =  pygame.image.load(link + "b.png").convert_alpha()
        self.surface2 =  pygame.image.load(link + "a.png").convert_alpha()
        self.isShow = False
        self.w, self.h = self.surface1.get_size()# lấy kích thước ảnh
        self.scale = scale
        self.x, self.y = index  
    def draw(self):
        surface_tempt = pygame.transform.scale(self.surface2 if self.isShow else self.surface1, (self.w *self.scale[0], self.h*self.scale[1]))
        screen.blit(surface_tempt, (self.x - self.w *self.scale[0]/2, self.y - self.h*self.scale[1]/2))
class IconValue:
    def __init__(self, scale, index, typeIcon):
        self.typeIcon = typeIcon
        self.surface =  pygame.image.load(path + "Image/"+ str(19 if typeIcon == 0 else 18) + ".png").convert_alpha()
        self.isActive = True
        self.w, self.h = self.surface.get_size()# lấy kích thước ảnh
        self.scale = scale
        self.x, self.y = index 
    
    def draw(self, speedY):
        self.y += speedY
        if(self.y < 100):
            return True
        if(self.y >= height):
            self.isActive = False
            return False
        surface_tempt = pygame.transform.scale(self.surface, (self.w *self.scale[0], self.h*self.scale[1]))
        screen.blit(surface_tempt, (self.x - self.w *self.scale[0]/2, self.y - self.h*self.scale[1]/2))
        return True
    def check_Button(self, typeBtn, indexBtn):
        xValue = self.x - indexBtn[0]
        yValue = self.y - indexBtn[1]
        d = math.sqrt(xValue*xValue + yValue*yValue)
        if(d < 20):
            if(typeBtn == self.typeIcon):
                return 1
            else:
                return -1
        return 0
        
class Game:
    def __init__(self):
        self.typeMusicalInstrument = 2

    def loadScene(self, indexScene):
        bg_surface = pygame.image.load(path + "Image/BG.png").convert()
        bg_surface = pygame.transform.scale(bg_surface, (width, height))
        n = 0
        index = (520, 700)
        while n < 100:
            screen.blit(bg_surface, (0, 0))
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
            x = random.randint(0, 100)
            if x < 30:
                n += random.randint(0, 15)
                if n > 100:
                    n = 100
            text_surface = font.render("Loading: " + str(n) + "%", True, YELLOW)
            screen.blit(text_surface, index)
            pygame.display.update()
            fpsclock.tick(FPS)
        if(indexScene == 0):
            self.menu()
        elif(indexScene == 1):
            self.playGame()
        elif(indexScene == 2):
            self.setting()
        elif(indexScene == 3):
            self.endGame()
            
    def menu(self):
        bg_surface = pygame.image.load(path + "Image/BG2.png").convert()
        bg_surface = pygame.transform.scale(bg_surface, (width, height))
        btnStart = Button(path + "Image/btnStart.png", (1, 1), (570, 400))
        btnSetting = Button(path + "Image/btnSetting.png", (1, 1), (570, 500))
        btnExit = Button(path + "Image/btnExit.png", (1, 1), (570, 600))
        while True:
            screen.blit(bg_surface, (0, 0))
            events = pygame.event.get()
            btnStart.draw()
            btnSetting.draw()
            btnExit.draw()
            for event in events:
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN: # nếu click chuột
                    mouse_x, mouse_y = event.pos # lấy tọa độ chuột và vẽ hình tròn
                    pygame.draw.circle(screen, (255, 220, 220), (mouse_x, mouse_y), 15)
                    if btnStart.click(mouse_x, mouse_y) == True:
                        self.loadScene(1)
                        return
                    if btnSetting.click(mouse_x, mouse_y) == True:
                        self.loadScene(2)
                        return
                    if btnExit.click(mouse_x, mouse_y) == True:
                        return
            pygame.display.update()
            fpsclock.tick(FPS)

    def setting(self):
        bg_surface = pygame.image.load(path + "Image/BG3.png").convert()
        bg_surface = pygame.transform.scale(bg_surface, (width, height))
        btn1 = Button(path + "Image/piano.png", (1, 1), (270, 400))
        btn2 = Button(path + "Image/drum.png", (1, 1), (570, 380))
        btn3 = Button(path + "Image/gitar.png", (1, 1), (970, 360))

        btnSelect1 = Button(path + "Image/btnSelect.png", (0.6, 0.6), (250, 540))
        btnSelect2 = Button(path + "Image/btnSelect.png", (0.6, 0.6), (570, 540))
        btnSelect3 = Button(path + "Image/btnSelect.png", (0.6, 0.6), (900, 540))
        btnExit = Button(path + "Image/btnExit.png", (1, 1), (570, 700))
        while True:
            screen.blit(bg_surface, (0, 0))
            events = pygame.event.get()
            btn1.draw()
            btn2.draw()
            btn3.draw()
            if self.typeMusicalInstrument != 0:
                btnSelect1.draw()
            if self.typeMusicalInstrument != 1:
                btnSelect2.draw()
            if self.typeMusicalInstrument != 2:
                btnSelect3.draw()
            btnExit.draw()
            for event in events:
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN: # nếu click chuột
                    mouse_x, mouse_y = event.pos # lấy tọa độ chuột và vẽ hình tròn
                    pygame.draw.circle(screen, (255, 220, 220), (mouse_x, mouse_y), 15)
                    if btnSelect1.click(mouse_x, mouse_y) == True:
                        self.typeMusicalInstrument = 0
                        playAudio('C4', self.typeMusicalInstrument)
                        print("Phát âm piano")
                    if btnSelect2.click(mouse_x, mouse_y) == True:
                        self.typeMusicalInstrument = 1
                        print("Phát âm trống")
                        playAudio('C4', self.typeMusicalInstrument)
                    if btnSelect3.click(mouse_x, mouse_y) == True:
                        self.typeMusicalInstrument = 2
                        print("Phát âm gitar")
                        playAudio('C4', self.typeMusicalInstrument)
                    if btnExit.click(mouse_x, mouse_y) == True:
                        self.loadScene(0)
                        return
            pygame.display.update()
            fpsclock.tick(FPS)

    def playGame(self):
        colorLine = (0, 238, 236)
        x1, y1 = 500, 100
        x2, y2 = 500, 700
        distanceX = 150
        bg_surface = pygame.image.load(path + "Image/BG3.png").convert()
        bg_surface = pygame.transform.scale(bg_surface, (width, height))

        btnExit = Button(path + "Image/btnExit.png", (0.6, 0.6), (1100, 50))
        icons = [IconShow(path + "Image/1", (0.4, 0.4), (x1 + 0*distanceX, 700)),
                    IconShow(path + "Image/2", (0.4, 0.4), (x1 + 1*distanceX, 700))]
        itemsPre = [IconValue((0.2, 0.2), (x1, y1), 0), IconValue((0.2, 0.2), (x1 + distanceX, y1), 1)]

        items = []
        inputValue = extract_notes_from_file(path + "/Data/" + str(random.randint(1, 5)) +".txt")
        n = len(inputValue)
        export_audio(inputValue, instruments[self.typeMusicalInstrument], path + "output_piano.wav")
        # xuat file am thanh toan bo ra export_audio(note):
        self.countTrue = 0
        self.countFalse = 0
        delaySpawnMin, delaySpawnMax = 1, 7
        delaySpawn = random.uniform(delaySpawnMin, delaySpawnMin)
        while n > 1:
            if delaySpawn > 0:
                delaySpawn -= 1 / FPS
                if delaySpawn <= 0:
                    delaySpawn = random.uniform(delaySpawnMin, delaySpawnMin)
                    #print(delaySpawn)
                    num = random.randint(1, 3)
                    for i in range(num):
                        k = 0 if random.randint(0, 1) < 0.5 else 1
                        t = IconValue((0.2, 0.2), (x1 + k*distanceX, y1), 0 if random.uniform(0, 1) < (0.7 if k == 0 else 0.3) else 1)
                        items.append(t)

            screen.blit(bg_surface, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos # lấy tọa độ chuột và vẽ hình tròn
                    pygame.draw.circle(screen, (255, 220, 220), (mouse_x, mouse_y), 15)
                    if btnExit.click(mouse_x, mouse_y) == True:
                        self.loadScene(0)
                        return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        icons[0].isShow = True
                    elif event.key == pygame.K_RIGHT:
                        icons[1].isShow = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        icons[0].isShow = False
                    elif event.key == pygame.K_RIGHT:
                        icons[1].isShow = False

            # Vẽ đường thẳng
            for i in range(0, 2):
                pygame.draw.line(screen, colorLine, (x1 + i*distanceX, y1), (x2 + i*distanceX, y2), 5)  # 5 là độ dày của đường thẳng
                icons[i].draw()
           # print(len(items))
            i = 0
            while i < len(items):
                if (not items[i].draw(5)):
                    print("MAt")
                    #audio_sai.play()
                else:
                    for j in range(2):
                        if icons[j].isShow:
                            #typeIcon
                            result = items[i].check_Button(j, (icons[j].x, icons[j].y))
                            if result == 1:
                                playAudio(inputValue[self.countTrue], self.typeMusicalInstrument)
                                print("Dung")
                                self.countTrue += 1
                                n -= 1
                                items[i].isActive = False
                            elif result == -1:
                                self.countFalse += 1
                                print("Sai")
                                #audio_sai.play()
                                items[i].isActive = False

                if not items[i].isActive:
                    items.pop(i)  
                else:
                    i += 1 
            btnExit.draw()
            
            pygame.display.update()
            fpsclock.tick(FPS)
        self.loadScene(3)
    def endGame(self):
        bg_surface = pygame.image.load(path + "Image/BG3.png").convert()
        bg_surface = pygame.transform.scale(bg_surface, (width, height))
        btnResult = Button(path + "Image/" + str(21 if self.countTrue > self.countFalse else 20)  +".png", (0.6, 0.6), (600, 450))
        btnExit = Button(path + "Image/btnExit.png", (1, 1), (600, 750))
        while True:
            screen.blit(bg_surface, (0, 0))
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN: # nếu click chuột
                    mouse_x, mouse_y = event.pos # lấy tọa độ chuột và vẽ hình tròn
                    pygame.draw.circle(screen, (255, 220, 220), (mouse_x, mouse_y), 15)
                    if btnExit.click(mouse_x, mouse_y) == True:
                        self.loadScene(0)
                        return
            text_surface = font.render(f"Score: {self.countTrue} / {self.countTrue + self.countFalse}", True, YELLOW)
            screen.blit(text_surface, (530, 650))
            btnExit.draw()
            btnResult.draw()
            pygame.display.update()
            fpsclock.tick(FPS)

    def play(self):
        #self.endGame()
        #self.playGame()
        #self.menu()
        self.loadScene(0)

game = Game()
game.play()
pygame.quit()