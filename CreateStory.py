
### openaiのバージョンがもとは0.28?だったのが<=1になったのでその変更をすべし

from venv import create
from openai import OpenAI
import openai
import json
import time
#from text2voicePeakv6 import playVoicePeak
#from text2voiceBox import playVoiceBox
#from text2voiceBox import play_auido_by_filename
#import speech_recognition as sr
#from GUIOmichi import StartGUI
#import tkinter as tk
#from CreateImageOmichiv6 import createImage
#from text2Emoji import createEmoji
#from playsound import playsound
import datetime
import os
import PySimpleGUI as sg
import glob
import shutil
import pygame

import config

client=OpenAI(api_key=config.openai_api_key)

### 世界観や登場人物の情報
story_Info=config.story_Info


# 続きの物語を生成する
def CreateCon(story_Info,story_history,history_summary):
    # 相手との対話履歴のアドバイスを反映させた物語
    prompt=f'''
    ###新たな人間との対話履歴 を参照して、「クロ」の###これまでの物語　の続きを作成してください。
    
    ### 新たな人間との対話履歴
    {history_summary}

    ### これまでの物語
    {story_history}
    '''

    try:
        res= client.chat.completions.create(
        model="gpt-4-1106-preview",
            messages=[
                {"role": "system", 
                 "content": prompt
                 }
            ],
        )
        return res.choices[0].message.content
        
    except Exception as e:
        print(e)
        return ""



def CreateStory(state,story_Info,plot):
    system_prompt="物語の設定："+story_Info  + f"""
        物語の設定からより詳細な物語を作ってください．
        豊かな発想力で書いてください。
        絶対に箇条書きをしないでください．文章で書いてください．
        ですます口調で，３段落程度で
        """
    try:
        res=client.chat.completions.create(
        model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
        )
        return res.choices[0].message.content
        
    except Exception as e:
        print(e)
        return ""
    
def make_pattern():
    # GUI設定
    sg.theme('LightBlue')
    layoutBefore=[]

    # # Buttons
    # text='1日目作成'
    # label=sg.Text(text,size=(50,1))
    # btn=sg.Button('day1',key='day1')
    # layoutBefore.append([label,btn])

    # text='2日目作成'
    # label=sg.Text(text,size=(50,1))
    # btn=sg.Button('day2',key='day2')
    # layoutBefore.append([label,btn])

    # text='3日目作成'
    # label=sg.Text(text,size=(50,1))
    # btn=sg.Button('day3',key='day3')
    # layoutBefore.append([label,btn])

    # text='4日目作成'
    # label=sg.Text(text,size=(50,1))
    # btn=sg.Button('day4',key='day4')
    # layoutBefore.append([label,btn])

    text='始まり作成'
    label=sg.Text(text,size=(50,1))
    btn=sg.Button('start',key='start')
    layoutBefore.append([label,btn])

    text='続き作成'
    label=sg.Text(text,size=(50,1))
    btn=sg.Button('continue',key='continue')
    layoutBefore.append([label,btn])
    return sg.Window('ストーリ作成',layoutBefore)

def select_chara():
    # GUI設定
    sg.theme('LightBlue')
    layoutChara=[]

    text='エージェントとの対話後'
    label=sg.Text(text,size=(50,1))
    btn=sg.Button('taiwago',key='taiwago')
    layoutChara.append([label,btn])

    text='エージェントとの対話なし'
    label=sg.Text(text,size=(50,1))
    btn=sg.Button('notaiwa',key='notaiwa')
    layoutChara.append([label,btn])

    return sg.Window('エージェントとの対話有無確認',layoutChara)
    

### main開始 ###################################
start=time.time() #実行開始時の時間取得
state=""
story=""
story_history=""
history_summary=""

### GUI設定を追加
window=make_pattern()

### すでにcreatedフォルダがある場合，それを「過去の物語」フォルダに移動する
# 前のcreatedフォルダの名前を取得
foldername=glob.glob(config.directory+"/created*", recursive=False)
print(foldername)
for folder in foldername:
    # 使用した物語4つと対話履歴4つが入ったファイルを「過去の物語」フォルダに移動する
    new_path = shutil.move(folder, config.directory+"/過去の物語")
    print("過去の物語フォルダに移動しました：")
    print(new_path)

dt=datetime.datetime.today()
folder_path=f"./created{dt.month}{dt.day}_{dt.hour}{dt.minute}"
print("フォルダ名："+folder_path)
os.mkdir(folder_path) # その時々のフォルダを作成する

while True:
    event, values = window.read(timeout=1)
    if event is None:
        print('Window event is None. exit')
        break
   
    elif event==('start'):
        print("creating startstory...")
        state="start"

        while state=="start":
            print("始まりのストーリー生成")
            story=CreateStory(state,story_Info,"")
            if story!="":
                state="終了"
        with open(config.directory+'/startstory.txt', 'w', encoding='utf-8') as f:
        #f = open(config.directory+'/startstory.txt', 'w')#シグナル生成
            f.write('\n<ストーリー>\n'+str(story))
            f.close()

        #story_history=story_history+"起:"+story
        pygame.mixer.init()
        pygame.mixer.music.load(config.directory+"/pre_wav/通知音.mp3")
        pygame.mixer.music.play()
        print("生成完了")
    elif event==('continue'):
        print("creating continuestory...")
        state="con"
        window.close()
        window=select_chara()  
    elif event==('taiwago'):
        ## created*フォルダ内にkuro_1フォルダがあるはずなのでそこに行き、対話履歴ファイルをゲットする。
        ## その際、保存先はcreated+フォルダであるが、directoryはconfig.directory+であることを忘れずに
        print("続きのストーリー生成(対話あり)")
        #chara=''
        if os.path.exists(f"{folder_path}/history_1.txt"):
            f = open(f"{folder_path}/history_1.txt")
            history_summary=f.read() # ファイル終端まで全て読んだデータを返す
            f.close()
            print(history_summary)
            # kuro_1.txtの内容を変数に保存しておく
            with open(config.directory+'/startstory.txt','r',encoding='utf-8') as file:
                for line in file:
                    story_history+=line
            state="con"
            while state=="con":
                story=CreateCon(story_Info,story_history,history_summary)
                if story!="":
                    state="終了"

        else:
            print("対話履歴が読み取れませんでした")
            history_summary=""
        with open(f"{folder_path}/ContinueStory.txt", 'w', encoding='utf-8') as f:
        #f = open(f"{folder_path}/ContinueStory.txt", 'w')#シグナル生成
            f.write('\n<ストーリー>\n'+str(story))
            f.close()

        filepath=f"startstory.txt"
        # 今の回のcreatedフォルダの名前を取得
        foldername=glob.glob(config.directory+"/created*", recursive=False)
        print(foldername[0])
        # day1～day3までの対話履歴テキストファイルをcreatedフォルダに移動
        shutil.move(filepath, foldername[0])
        print(f"初めの物語のテキストファイルを{foldername}に移動しました．")
        pygame.mixer.init()
        pygame.mixer.music.load(config.directory+"/pre_wav/通知音.mp3")
        pygame.mixer.music.play()
        print("生成完了")
    elif event==('notaiwa'):
        #単純に続きを生成
        print("続きのストーリー生成(対話なし)")
        #chara=''
        with open(config.directory+'/startstory.txt','r') as file:
            for line in file:
                story_history+=line
        state="con"
        while state=="con":
            story=CreateCon(story_Info,story_history,history_summary)
            if story!="":
                state="終了"
        with open(f"{folder_path}/ContinueStory.txt", 'w', encoding='utf-8') as f:
        #f = open(f"{folder_path}/ContinueStory.txt", 'w')#シグナル生成
            f.write('\n<ストーリー>\n'+str(story))
            f.close()
        
        filepath=f"startstory.txt"
        # 今の回のcreatedフォルダの名前を取得
        foldername=glob.glob(config.directory+"/created*", recursive=False)
        print(foldername[0])
        # day1～day3までの対話履歴テキストファイルをcreatedフォルダに移動
        shutil.move(filepath, foldername[0])
        print(f"初めの物語のテキストファイルを{foldername}に移動しました．")
        pygame.mixer.init()
        pygame.mixer.music.load(config.directory+"/pre_wav/通知音.mp3")
        pygame.mixer.music.play()  
        print("生成完了")
    
    else:
        pass

'''story_history=story_history+"結:"+story
print(story_history)
'''
end=time.time() #実行終了時の時間を取得

time_diff=end-start

print("実行終了")
print("処理時間：")
print(time_diff)
window.close()