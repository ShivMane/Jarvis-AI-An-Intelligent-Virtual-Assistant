from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# ✅ Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# ✅ Ensure API key is available
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
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

def Googlesearch(query):
    """ Searches Google and returns top 5 results. """
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    """ Removes unnecessary new lines from the answer. """
    lines = Answer.split("\n")
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    """ Provides real-time date and time information. """
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%D")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    return (
        f"Please use this real-time information if needed:\n"
        f"Day: {day}\n"
        f"Date: {date}\n"
        f"Month: {month}\n"
        f"Year: {year}\n"
        f"Time: {hour} hours : {minute} minutes : {second} seconds.\n"
    )

def RealtimeSearchEngine(prompt):
    """ Sends user query to Groq AI with real-time Google search results. """
    global SystemChatBot, messages

    # ✅ Load previous chat history
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)

    messages.append({"role": "user", "content": prompt})

    # ✅ Append Google search results as system message
    SystemChatBot.append({"role": "system", "content": Googlesearch(prompt)})

    try:
        # ✅ API Request
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "user", "content": Information()}] + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        # ✅ Fix indentation issue for streaming response
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
        return RealtimeSearchEngine(prompt)

# ✅ Main chatbot loop
if __name__ == "__main__":
    while True:
        user_input = input("Enter your question: ")
        print(RealtimeSearchEngine(user_input))
