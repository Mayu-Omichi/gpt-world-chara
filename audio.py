import os
import time
import scipy.io.wavfile as wav  # 今回はwaveモジュールではなくこれを用いる（ファイル読み込み）
import sounddevice as sd  # pythonで音声データを扱うライブラリ
import wave  # waveファイルを扱うライブラリ

i = 1
print('実行開始')
while True:
    for file in os.listdir('./wav/'):
        if file.endswith('.wav'):
            try:
                print(i)
                filepath = 'C://Users//kinak//Documents//物語自動生成//沖縄に向けて//TRPG_papet//wav//audio' + str(i) + '.wav' # wavファイルのパス
                print(filepath)
                while True:
                    while True:
                        try:  # wavファイルの長さが取得できるまで繰り返し
                            with wave.open(filepath, mode='rb') as wf:  # wavファイルの長さを取得
                                wavtime = float(wf.getnframes() / wf.getframerate())
                                # print('time(second): ', wavtime)  # サンプリング周波数(fs)とデータを取得
                            if wavtime != 0:
                                fs, data = wav.read(filepath)  # サンプリング周波数(fs)とデータを取得
                                sd.play(data, fs)  # 再生
                                time.sleep(wavtime)  # 再生中待機
                                break
                            # else:
                            #     print("wav=0s")
                        except Exception as e:
                            # print("再生エラー")
                            pass

                    print("再生しました。")
                    os.remove(filepath)  # 再生したファイルを削除
                    i += 1
                    break

            except Exception as e:
                i += 1
                pass