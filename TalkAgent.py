### GUIも組み込めそうなので，実際にGPTを取り入れて会話してみる
from openai import OpenAI
import speech_recognition as sr
import os
import PySimpleGUI as sg
from gtts import gTTS 
from pydub import AudioSegment
import time
import flet as ft
import time
import datetime
import schedule
import shutil
import glob
import random
import config

from threading import Thread

#MeCabで分割
import MeCab
import ipadic
import shutil
import glob
from collections import Counter

import re


client=OpenAI(api_key=config.openai_api_key)

directory = config.directory+'/wav'

isGet=False


answer=""


def typeSpeech():
    isGet=False
    user_text=input('エージェントへのメッセージ：')
    
    return(user_text)
        

def askChatGPT(question, pattern,history_summary,start_story):
    global answer
    
    system_prompt = config.main_prompt + f"""###直前の会話を参照して，自然な会話をしてください
    ###前日の物語
    {start_story}
    
    ###直前の会話
    {history_summary}
    """

            
    try:
        res = client.chat.completions.create(
              model = "gpt-4-1106-preview",
              messages = [
                  {
                      'role':'system',
                      'content': system_prompt
                  },
                  {
                      'role':'user',
                      'content':question
                  },
                  ],
              max_tokens = 1024,
              stream=True
              )
        #return res#.choices[0].message.content
        collected_messages=[]
        total_messages=""

        for chunk in res:
            #chunk_message = chunk['choices'][0]['delta']
            chunk_message=chunk.choices[0].delta.content or ""
            collected_messages.append(chunk_message)
            if '、' in chunk_message or \
                '。' in chunk_message or \
                '！' in chunk_message or \
                '？' in chunk_message:
                message = ''.join(collected_messages)
                print('クロ: ' + message)
                total_messages+=message

                collected_messages=[]
        return total_messages
    except Exception as e:
        print(e)
        return ""

# TTS用の便利関数
def make_wav(text:str, output_file_path='temp.wav', slow=False) -> int:
    gTTS(text=text, lang='ja', slow=slow).save('temp.mp3')
    sound = AudioSegment.from_mp3('temp.mp3')
    sound.export(output_file_path, format='wav')
    return sound.duration_seconds


def make_pattern():
    # GUI設定
    sg.theme('Black')
    layoutBefore=[]

    # Buttons
    text='条件１'
    label=sg.Text(text,size=(25,1))
    btn=sg.Button('雑談',key='pattern1')
    layoutBefore.append([label,btn])

    return sg.Window('会話パターン選択',layoutBefore)


def make_conv(pattern):
    global response
    # GUI設定
    sg.theme('Black')
    # Window layout
    layout = []

    # Speech buttons
    btn=sg.Button('＜前に戻る',key='back')
    btn2=sg.Button('対話履歴保存',key='save')
    layout.append([btn,btn2])

    
    # # Text fieldをいったんはさんで境界をつくろう！
    # text_field = sg.Text('------------------------------------------------------------',key='border', size=(50, 1))
    # layout.append([text_field])
    
    text = 'エージェントとの対話'
    #response='ニャンランドは無事平和を迎えることができたよ！君とお話したおかげかも！ありがとう！'
    btn = sg.Button('対話開始', key='zenhan')
    text='ここを押して対話スタート'
    label = sg.Text(text, size=(50, 1))
    layout.append([label, btn])

    '''
    text = '後半の対話(人間のこと聞く)'
    #response='ニャンランドは無事平和を迎えることができたよ！君とお話したおかげかも！ありがとう！'
    btn = sg.Button('後半', key='kouhan')
    text='ここを押して後半スタート'
    label = sg.Text(text, size=(50, 1))
    layout.append([label, btn])

    '''

    return sg.Window('フェーズ管理', layout)

def delete_wav_files(directory_path):
    # ディレクトリ内のファイル一覧を取得
    files = os.listdir(directory_path)

    # ディレクトリ内のすべてのwavファイルを削除
    for file in files:
        if file.endswith('.wav'):
            file_path = os.path.join(directory_path, file)
            os.remove(file_path)
            print(f"{file} を削除しました。")

'''def datesend(data):
    # exitを切断用コマンドとしておく
    if data == "exit":
        break
    else:
        try:
            sock.send(data.encode("utf-8"))
        except ConnectionResetError:
            break'''

# 会話パターン初期化
pattern=0

# 最初に表示するウィンドウ
window=make_pattern()

'''#不要でーたの削除
for file in os.listdir('./'):
    if file.endswith('signal.txt'):
        os.remove('signal.txt')
    if file.endswith('signal2.txt'):
        os.remove('signal2.txt')'''

# ディレクトリのパスを指定
target_directory = config.directory+'/wav'

# WAV ファイルを削除
delete_wav_files(target_directory)

histories=[]
history_summary=""
story_list=["","","",""]

target_string='<ストーリー>' #探したい文字列

start=time.time() #実行開始時の時間取得


# Event loop
while True:
    question="error"
    found=False
    event, values = window.read(timeout=1)
    if event is None:
        print('Window event is None. exit')
        break 
    elif event==('pattern1'):
        print("雑談 is pushed!")
        pattern=1
        # startstory.txtの内容を変数に保存しておく
        with open(config.directory+f'/startstory.txt','r',encoding='utf-8') as file:
            for line in file:
                    if found:
                        story_list[0]+=line
                    if target_string in line:
                        found=True
    
        window.close()
        window=make_conv(1)
    
    elif event==('zenhan'):
        count=1
        print("Start zenhan talk!")
        print(story_list[0])
        while event==('zenhan'):
            print(str(count) + "回目の会話")
            # ここに最初の質問の音声を流す処理
            
            question=""
            if count>10:
                history_summary += "クロ:話し疲れたから僕は寝るね、おやすみなさい！" + "\n"
                break
            else:
                question=typeSpeech()
                if question=="end":
                    print("「end」を入力したためプログラムを終了")
                    break
                #print(question)
            
            count=count+1
            if pattern!=0:
                answer=askChatGPT(question,pattern,history_summary,story_list[0])
            else:
                answer=askChatGPT(question,"",history_summary,story_list[0])
            histories.append({'role': 'user', 'content': question})
            histories.append({'role': 'assistant', 'content': answer})
            text_message = ""
            for history in histories:
                if history['role'] == 'user':
                    text_message += "人間: " + history['content'] + "\n"
                elif history['role'] == 'assistant':
                    text_message += "クロ: " + history['content'] + "\n"
            history_summary+=text_message

            histories=[]
    
    elif event=='save':
        # 1日の対話履歴を保存
        # 会話履歴をテキストファイルに
        dt=datetime.datetime.today()
        filepath=f"history_1.txt"
        f = open(filepath, 'w')
        f.write(history_summary)
        f.close()
        print("会話履歴を保存しました")
        # 今の回のcreatedフォルダの名前を取得
        foldername=glob.glob(config.directory+"/created*", recursive=False)
        print(foldername[0])
        # day1～day3までの対話履歴テキストファイルをcreatedフォルダに移動
        shutil.move(filepath, foldername[0])
        print(f"読み取った対話履歴のテキストファイルを{foldername}に移動しました．")
        history_summary=""

    elif event=='back':
        

        pattern=0
        history_summary=""

        window.close()
        window=make_pattern()
    else:
        pass




# # データを受け取った時の処理にこれを入れる
# sock.send(data.encode("utf-8"))
# まだ対話履歴を保存していなかったら
filepath=f"history_1.txt"
if os.path.isfile(filepath)==False and pattern!=0:
    # 1日の対話履歴を保存
    # 会話履歴をテキストファイルに
    f = open(filepath, 'w')
    f.write(history_summary)
    f.close()
    print("会話履歴を保存しました")
    # 今の回のcreatedフォルダの名前を取得
    foldername=glob.glob(config.directory+"/created*", recursive=False)
    print(foldername[0])
    # 対話履歴テキストファイルをcreatedフォルダに移動
    shutil.move(filepath, foldername[0])
    print(f"読み取った対話履歴のテキストファイルを{foldername[0]}に移動しました．")

else:
    print("そのファイルはすでに保存されています")


window.close()