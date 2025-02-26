from Frontend.GUI import(
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
) 
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
import subprocess

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am Doing Well. How may i help you ?'''
subprocess = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    File = open (r'Data\Chatlog.json', 'r', encoding="utf-8" )
    if len(File.read())<5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")

        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\Chatlog.json', 'r', encoding='utf-8')as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry ["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry ["role"] == "assistant":
            formatted_chatlog += f"Assistent: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User",Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding = 'utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    File = open(TempDirectoryPath('Database.data'), "r", encoding='utf-8')
    Data = File.read()
    if len(str(Data))>0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(TempDirectoryPath('Response.data'), "w", encoding='utf-8')
        File.write(result)
        File.close()

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecutin():


    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()  
    print(f"🗣️ Heard: {Query}")  

    if not Query.strip():  # ✅ If no input, return
        print("❌ No speech detected!")
        return

    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)
    print(f"🤖 Decision: {Decision}")   

    if not Decision:
        print("❌ No decision was made.")
        return

    # ✅ Process General Queries (AI ChatBot)
    for command in Decision:
        if command.startswith("general"):
            QueryFinal = command.replace("general", "").strip()
            print(f"💡 Sending query to AI: {QueryFinal}")
            Answer = ChatBot(QueryFinal)  # ✅ Get AI response
            print(f"📝 AI Response: {Answer}")
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return

    # ✅ Process Other Functionalities (Automation, Realtime, etc.)
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True


    processes = []
    if ImageExecution == True:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")

        try:
            p1 = subprocess.Popen(['python', r'Backend\ImageGenaration.py'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE, shell=False)
            processes.append(p1)  # ✅ Store processes correctly
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    if G and R or R: 
        SetAssistantStatus("Searching... ")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname}: {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True

    for Queries in Decision:
        if "realtime" in Queries:
            SetAssistantStatus("Searching...")
            QueryFinal = Queries.replace("realtime", "").strip()
            Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True

        elif "exit" in Queries:
            QueryFinal = "Okay, Bye!"
            Answer = ChatBot(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            os._exit(1)


    print("🎤 Jarvis is Listening for speech...")

    SetAssistantStatus("Listening...")
    
    Query = SpeechRecognition()  # ✅ Capture voice input
    print(f"🗣️ Heard: {Query}")  # ✅ Debugging print

    if not Query.strip():  # ✅ If no input, return
        print("❌ No speech detected!")
        return

    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)
    print(f"🤖 Decision: {Decision}")  # ✅ See what Jarvis is deciding

    if not Decision:
        print("❌ No decision was made.")
        return

    for command in Decision:
        if command.startswith("general"):
            QueryFinal = command.replace("general", "").strip()
            print(f"💡 Sending query to AI: {QueryFinal}")
            Answer = ChatBot(QueryFinal)  # ✅ Get AI response
            print(f"📝 AI Response: {Answer}")
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return

    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening... ")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking... ")
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"Decision : {Decision}")
    print("")

    G = any ([i for i in Decision if i.startswith("general")])
    R = any ([i for i in Decision if i.startswith("realtime")])

    Mearged_query = " and " .join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True

    if ImageExecution == True:

        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")

        try:
            p1 = subprocess.Popen(['python', r'Backend\ImageGenaration.py'],
                                  stdout = subprocess.PIPE, stderr = subprocess.PIPE,
                                  stdin = subprocess.PIPE, shell=False)
            subprocess.append(p1)

        except Exception as e:
            print(f"Error stsrting ImageGeneration.py: {e}")

    if G and R or R:

        SetAssistantStatus("Searching... ")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:

            if"general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering... ")
                TextToSpeech(Answer)
                return True
            
            elif "realtime" in Queries:
                SetAssistantStatus("Searching... ")
                QueryFinal = Queries.replace("realtime ","")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering... ")
                TextToSpeech(Answer)
                return True
            
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen (f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering... ")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering... ")
                os._exit(1)

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        print(f"🔍 Checking Mic Status: {CurrentStatus}")  # ✅ Debugging print

        if CurrentStatus == "True":
            print("🎤 Jarvis is Listening...")
            MainExecutin()  # ✅ Run the main execution function

        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")



def SecondThread():

    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon = True)
    thread2.start()
    SecondThread()
