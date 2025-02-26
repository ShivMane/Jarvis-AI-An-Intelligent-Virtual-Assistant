from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# ✅ Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# ✅ Ensure API key is provided
if not GroqAPIKey:
    print("❌ Error: Groq API Key not found. Check your .env file.")
    exit(1)

# ✅ Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# ✅ Load previous chat history
try:
    with open(r"Data\Chatlog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\Chatlog.json", "w") as f:
        dump([], f)
    messages = []

# ✅ System Prompt
System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname}, 
which also has real-time up-to-date information from the internet.

*** Do not tell time until I ask, do not talk too much, just answer the question. ***
*** Reply only in English, even if the question is in Hindi. ***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

# ✅ Function to provide real-time information
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%D")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed:\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds.\n"
    return data

# ✅ Function to clean up AI output
def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

# ✅ Function to handle chatbot responses
def ChatBot(Query):
    """ Sends the user's query to the AI chatbot and returns the response. """

    try:
        # ✅ Load previous messages
        with open(r"Data\Chatlog.json", "r") as f:
            messages = load(f)

        # ✅ Append the user query to the messages
        messages.append({"role": "user", "content": Query})

        # ✅ Make API request
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "user", "content": RealtimeInformation()}] + messages,
            max_tokens=1042,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        # ✅ Clean up the response
        Answer = Answer.replace("</s>", "")

        # ✅ Append AI response to messages
        messages.append({"role": "assistant", "content": Answer})

        # ✅ Save updated chat history
        with open(r"Data\Chatlog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"❌ Error: {e}")
        with open(r"Data\Chatlog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)

# ✅ Main chatbot loop
if __name__ == "__main__":
    while True:
        user_input = input("Enter your question: ")
        print(ChatBot(user_input))
