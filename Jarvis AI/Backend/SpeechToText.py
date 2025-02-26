from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import speech_recognition as sr

# ✅ Load environment variables
env_vars = dotenv_values(".env")

InputLanguage = env_vars.get("InputLanguage")

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# ✅ Correct language setting in HTML
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# ✅ Save voice recognition HTML file
os.makedirs("Data", exist_ok=True)
with open(r"Data/voice.html", "w") as f:
    f.write(HtmlCode)

# ✅ Get current directory path
current_dir = os.getcwd()
Link = f"file:///{current_dir}/Data/voice.html"

# ✅ Chrome Options for Selenium
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")  # ✅ Avoids GUI issues

# ✅ Initialize the Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# ✅ Define the path for temporary files
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

# ✅ Function to set assistant status
def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)

# ✅ Function to modify a query for better punctuation and formatting
def QueryModifier(Query):
    new_query = Query.strip().lower()
    query_words = new_query.split()
    
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can", "what's", "where's", "how's"]

    # ✅ Ensure proper punctuation
    if query_words and query_words[0] in question_words:
        new_query = new_query.rstrip(".?!") + "?"
    else:
        new_query = new_query.rstrip(".?!") + "."

    return new_query.capitalize()

# ✅ Function to translate text to English
def UniversalTranslator(Text):
    return mt.translate(Text, "en", "auto").capitalize()

# ✅ Function to recognize speech using Selenium
def SpeechRecognition():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening for speech...")

        try:
            audio = recognizer.listen(source, timeout=5)  # ✅ Wait for 5 seconds
            print("🛠️ Processing voice input...")

            query = recognizer.recognize_google(audio)
            print(f"🗣️ Captured Speech: {query}")  # ✅ Debugging print
            return query

        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return ""

        except sr.RequestError as e:
            print(f"⚠️ API error: {e}")
            return ""

        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            return ""

# ✅ Main script execution
if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)
