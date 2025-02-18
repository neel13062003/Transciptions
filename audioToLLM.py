# # deepseek_env\Scripts\activate
# # python -m streamlit run audioToLLM.py 
# import os
# import openai
# import pyttsx3
# import speech_recognition as sr
# import streamlit as st
# from datetime import datetime
# import threading
# import asyncio
# from dotenv import load_dotenv

# load_dotenv()

# # OpenAI API key
# openai.api_key = os.getenv('OPENAI_API_KEY')

# # Initialize text-to-speech engine
# engine = pyttsx3.init()
# voices = engine.getProperty('voices')
# if len(voices) > 1:
#     female_voice = voices[1]
#     engine.setProperty('voice', female_voice.id)

# def extract_file_names(query):
#     """Extract file names from a comparison query"""
#     files = st.session_state.audio_files.keys()
#     mentioned_files = []
#     for file in files:
#         base_name = os.path.splitext(file)[0].lower()
#         if base_name in query.lower():
#             mentioned_files.append(file)
#     return mentioned_files

# def generate_summary_points():
#     """Generate summary points for all audio files"""
#     all_transcripts = {
#         file: data["transcript"] 
#         for file, data in st.session_state.audio_files.items()
#     }
    
#     if not all_transcripts:
#         return "No audio files uploaded yet."
    
#     combined_text = "\n\n".join([
#         f"Recording {file}:\n{text}" 
#         for file, text in all_transcripts.items()
#     ])
    
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are an expert in summarizing audio transcriptions."},
#                 {"role": "user", "content": f"""Please provide key points from all these recordings:
#                 {combined_text}
                
#                 Format your response as:
#                 1. Overall themes across all recordings
#                 2. Key points from each recording
#                 3. Notable connections between recordings"""}
#             ],
#         )
#         return response['choices'][0]['message']['content']
#     except Exception as e:
#         return f"Error generating summary: {str(e)}"

# def analyze_similarities(transcripts):
#     """Analyze similarities between multiple transcripts using GPT"""
#     combined_text = "\n\n".join([f"Recording {i+1}:\n{text}" for i, text in enumerate(transcripts)])
    
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are an expert in analyzing and comparing audio transcriptions."},
#                 {"role": "user", "content": f"""Please analyze these transcriptions and provide:
#                 1. Key similarities and differences
#                 2. Main themes or topics discussed
#                 3. Notable variations in content
#                 4. Any inconsistencies or contradictions

#                 Transcriptions:
#                 {combined_text}"""}
#             ],
#         )
#         return response['choices'][0]['message']['content']
#     except Exception as e:
#         return f"Error in analysis: {str(e)}"


# def text_to_speech(text):
#     """Use a separate thread to avoid blocking issues."""
#     local_engine = pyttsx3.init()
#     local_engine.say(text)

#     # Run in a separate thread to avoid 'run loop already started' issue
#     def run_engine():
#         local_engine.runAndWait()

#     thread = threading.Thread(target=run_engine)
#     thread.start()

# def transcribe_audio(file_path):
#     """Transcribe audio using OpenAI Whisper"""
#     try:
#         with open(file_path, "rb") as audio_file:
#             transcript = openai.Audio.transcribe(
#                 model="whisper-1",
#                 file=audio_file
#             )
#         return transcript['text']
#     except Exception as e:
#         st.error(f"Error transcribing audio: {str(e)}")
#         return None

# def call_gpt(query, context, chat_history):
#     """Call GPT with the given query and context"""
#     final_query = f"""
#     Based on the following audio transcription and chat history, please answer the question.
    
#     Available Transcriptions:
#     {context}
    
#     Previous Chat History:
#     {chat_history}
    
#     Question: {query}
#     """
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant analyzing audio transcriptions."},
#                 {"role": "user", "content": final_query}
#             ],
#         )
#         return response['choices'][0]['message']['content']
#     except Exception as e:
#         return f"Error: {str(e)}"

# def handle_comparison_query(query):
#     """Handle natural language comparison queries"""
#     files = extract_file_names(query)
#     if len(files) < 2:
#         return "I couldn't identify which recordings you want to compare. Please mention the file names clearly in your question."
    
#     transcripts = [st.session_state.audio_files[file]["transcript"] for file in files]
#     comparison = analyze_similarities(transcripts)
    
#     return comparison

# def initialize_session_state():
#     """Initialize session state variables"""
#     if "audio_files" not in st.session_state:
#         st.session_state.audio_files = {}
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []
#     if "transcription_status" not in st.session_state:
#         st.session_state.transcription_status = {}

# def save_uploaded_file(uploaded_file):
#     """Save uploaded file temporarily and return the path"""
#     temp_dir = "temp_audio_files"
#     if not os.path.exists(temp_dir):
#         os.makedirs(temp_dir)
    
#     file_path = os.path.join(temp_dir, uploaded_file.name)
#     with open(file_path, "wb") as f:
#         f.write(uploaded_file.read())
#     return file_path

# def process_chat_input(user_input):
#     """Process chat input and return response"""
#     # Add user message to history
#     st.session_state.chat_history.append({
#         "role": "user",
#         "content": user_input
#     })

#     # Get context from all transcripts
#     all_transcripts = "\n\n".join([
#         f"File: {file}\nTranscript: {data['transcript']}"
#         for file, data in st.session_state.audio_files.items()
#     ])

#     chat_history = "\n".join([
#         f"{msg['role']}: {msg['content']}"
#         for msg in st.session_state.chat_history[:-1]
#     ])

#     # Check if it's a comparison query
#     if "compare" in user_input.lower() or "difference" in user_input.lower():
#         response = handle_comparison_query(user_input)
#     else:
#         # Regular chat query
#         response = call_gpt(user_input, all_transcripts, chat_history)

#     # Add AI response to history
#     st.session_state.chat_history.append({
#         "role": "assistant",
#         "content": response
#     })

#     return response

# def main():
#     st.set_page_config(page_title="Audio Analysis System", layout="wide")
#     initialize_session_state()

#     # Sidebar
#     with st.sidebar:
#         st.title("🎙️ Audio Analysis System")
        
#         # File Upload Section
#         st.markdown("### 📤 Upload Files")
#         uploaded_files = st.file_uploader(
#             "Upload MP3 Files",
#             type=["mp3"],
#             accept_multiple_files=True,
#             key="file_uploader"
#         )

#         # Process uploaded files
#         if uploaded_files:
#             for file in uploaded_files:
#                 if file.name not in st.session_state.audio_files:
#                     st.session_state.transcription_status[file.name] = "Processing..."
#                     temp_path = save_uploaded_file(file)
                    
#                     transcript = transcribe_audio(temp_path)
#                     if transcript:
#                         st.session_state.audio_files[file.name] = {
#                             "transcript": transcript,
#                             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                         }
#                         st.session_state.transcription_status[file.name] = "Complete"
#                     else:
#                         st.session_state.transcription_status[file.name] = "Failed"
                    
#                     if os.path.exists(temp_path):
#                         os.remove(temp_path)

#         # Show available files and their status
#         st.markdown("### 📁 Available Recordings")
#         for file_name in st.session_state.audio_files:
#             status_color = {
#                 "Complete": "🟢",
#                 "Processing...": "🟡",
#                 "Failed": "🔴"
#             }
#             st.write(f"{status_color[st.session_state.transcription_status[file_name]]} {file_name}")

#     # Main interface
#     if st.session_state.audio_files:
#         st.title("💬 Audio Analysis Dashboard")

#         # Summary section
#         with st.expander("📊 Summary of All Recordings", expanded=True):
#             summary = generate_summary_points()
#             st.markdown(summary)

#         # Show all transcriptions
#         with st.expander("📝 All Transcriptions"):
#             for file_name, data in st.session_state.audio_files.items():
#                 st.subheader(f"📄 {file_name}")
#                 st.write(data["transcript"])

#         # Chat interface
#         st.markdown("### 💭 Master Chat")
#         for message in st.session_state.chat_history:
#             if message["role"] == "user":
#                 st.markdown(f"""
#                 <div style='background-color: #d6f5d6;padding: 10px; border-radius: 10px; margin: 5px 0;'>
#                     🗣️ <b>You:</b> {message['content']}
#                 </div>
#                 """, unsafe_allow_html=True)
#             else:
#                 st.markdown(f"""
#                 <div style='background-color: #d6f5d6; padding: 10px; border-radius: 10px; color: black;'>
#                     🤖 <b>Assistant:</b> {response}
#                 </div>
#                 """, unsafe_allow_html=True)

#         # Input section
#         st.markdown("### ⌨️ Your Input")
#         input_col1, input_col2 = st.columns([3, 1])
#         with input_col1:
#             user_input = st.text_input(
#                 "Type your message (you can ask about any recording or compare them):",
#                 key="text_input"
#             )
#         with input_col2:
#             is_voice = st.button("🎤 Voice Input")

#         if is_voice:
#             recognizer = sr.Recognizer()
#             try:
#                 with sr.Microphone() as source:
#                     st.info("🎤 Listening... Speak now")
#                     audio = recognizer.listen(source, timeout=5)
#                     user_input = recognizer.recognize_google(audio)
#                     st.success(f"You said: {user_input}")
#             except Exception as e:
#                 st.error(f"Error recording audio: {str(e)}")
#                 user_input = ""

#         if user_input:
#             response = process_chat_input(user_input)
#             st.write(f"🤖 Assistant: {response}")
#             text_to_speech(response)

#     else:
#         st.title("🎤 Audio Analysis System")
#         st.markdown("""
#         ### Welcome! 👋
        
#         This system allows you to:
#         - 📤 Upload multiple audio recordings
#         - 📊 View summaries of all recordings
#         - 💬 Chat about any or all recordings
#         - 🔄 Compare recordings through chat
#         - 🎙️ Use voice or text input
        
#         Get started by uploading your audio files in the sidebar! 👈
#         """)

# if __name__ == "__main__":
#     main()

# # deepseek_env\Scripts\activate
# # python -m streamlit run audioToLLM.py 
import os
import openai
import speech_recognition as sr
import streamlit as st
from datetime import datetime
import threading
import asyncio
from dotenv import load_dotenv

load_dotenv()

# OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def extract_file_names(query):
    """Extract file names from a comparison query"""
    files = st.session_state.audio_files.keys()
    mentioned_files = []
    for file in files:
        base_name = os.path.splitext(file)[0].lower()
        if base_name in query.lower():
            mentioned_files.append(file)
    return mentioned_files

def generate_summary_points():
    """Generate summary points for all audio files"""
    all_transcripts = {
        file: data["transcript"] 
        for file, data in st.session_state.audio_files.items()
    }
    
    if not all_transcripts:
        return "No audio files uploaded yet."
    
    combined_text = "\n\n".join([
        f"Recording {file}:\n{text}" 
        for file, text in all_transcripts.items()
    ])
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in summarizing audio transcriptions."},
                {"role": "user", "content": f"""Please provide key points from all these recordings:
                {combined_text}
                
                Format your response as:
                1. Overall themes across all recordings
                2. Key points from each recording
                3. Notable connections between recordings"""}
            ],
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def analyze_similarities(transcripts):
    """Analyze similarities between multiple transcripts using GPT"""
    combined_text = "\n\n".join([f"Recording {i+1}:\n{text}" for i, text in enumerate(transcripts)])
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in analyzing and comparing audio transcriptions."},
                {"role": "user", "content": f"""Please analyze these transcriptions and provide:
                1. Key similarities and differences
                2. Main themes or topics discussed
                3. Notable variations in content
                4. Any inconsistencies or contradictions

                Transcriptions:
                {combined_text}"""}
            ],
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error in analysis: {str(e)}"

def transcribe_audio(file_path):
    """Transcribe audio using OpenAI Whisper"""
    try:
        with open(file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
        return transcript['text']
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def call_gpt(query, context, chat_history):
    """Call GPT with the given query and context"""
    final_query = f"""
    Based on the following audio transcription and chat history, please answer the question.
    
    Available Transcriptions:
    {context}
    
    Previous Chat History:
    {chat_history}
    
    Question: {query}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant analyzing audio transcriptions."},
                {"role": "user", "content": final_query}
            ],
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

def handle_comparison_query(query):
    """Handle natural language comparison queries"""
    files = extract_file_names(query)
    if len(files) < 2:
        return "I couldn't identify which recordings you want to compare. Please mention the file names clearly in your question."
    
    transcripts = [st.session_state.audio_files[file]["transcript"] for file in files]
    comparison = analyze_similarities(transcripts)
    
    return comparison

def initialize_session_state():
    """Initialize session state variables"""
    if "audio_files" not in st.session_state:
        st.session_state.audio_files = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "transcription_status" not in st.session_state:
        st.session_state.transcription_status = {}

def save_uploaded_file(uploaded_file):
    """Save uploaded file temporarily and return the path"""
    temp_dir = "temp_audio_files"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    return file_path

def process_chat_input(user_input):
    """Process chat input and return response"""
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    # Get context from all transcripts
    all_transcripts = "\n\n".join([
        f"File: {file}\nTranscript: {data['transcript']}"
        for file, data in st.session_state.audio_files.items()
    ])

    chat_history = "\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in st.session_state.chat_history[:-1]
    ])

    # Check if it's a comparison query
    if "compare" in user_input.lower() or "difference" in user_input.lower():
        response = handle_comparison_query(user_input)
    else:
        # Regular chat query
        response = call_gpt(user_input, all_transcripts, chat_history)

    # Add AI response to history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response
    })

    return response

def main():
    st.set_page_config(page_title="Audio Analysis System", layout="wide")
    initialize_session_state()

    # Sidebar
    with st.sidebar:
        st.title("🎙️ Audio Analysis System")
        
        # File Upload Section
        st.markdown("### 📤 Upload Files")
        uploaded_files = st.file_uploader(
            "Upload MP3 Files",
            type=["mp3"],
            accept_multiple_files=True,
            key="file_uploader"
        )

        # Process uploaded files
        if uploaded_files:
            for file in uploaded_files:
                if file.name not in st.session_state.audio_files:
                    st.session_state.transcription_status[file.name] = "Processing..."
                    temp_path = save_uploaded_file(file)
                    
                    transcript = transcribe_audio(temp_path)
                    if transcript:
                        st.session_state.audio_files[file.name] = {
                            "transcript": transcript,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        st.session_state.transcription_status[file.name] = "Complete"
                    else:
                        st.session_state.transcription_status[file.name] = "Failed"
                    
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

        # Show available files and their status
        st.markdown("### 📁 Available Recordings")
        for file_name in st.session_state.audio_files:
            status_color = {
                "Complete": "🟢",
                "Processing...": "🟡",
                "Failed": "🔴"
            }
            st.write(f"{status_color[st.session_state.transcription_status[file_name]]} {file_name}")

    # Main interface
    st.title("💬 Audio Analysis Dashboard")
    
    # Show Transcriptions in UI
    st.markdown("### 🎧 Transcriptions")
    if st.session_state.audio_files:
        for file_name, data in st.session_state.audio_files.items():
            st.subheader(f"📂 {file_name}")
            st.text_area(f"Transcript of {file_name}", data["transcript"], height=150)

    # Chat Interface for Querying Transcripts
    st.markdown("### 💬 Ask Questions About the Audio")
    user_input = st.text_input("Ask a question about the uploaded audio...")

    if st.button("Submit Query"):
        if not user_input:
            st.warning("Please enter a question before submitting.")
        else:
            response = process_chat_input(user_input)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.success("Response generated!")

    # Display Chat History
    if st.session_state.chat_history:
        st.markdown("### 📝 Chat History")
        for chat in st.session_state.chat_history:
            role_icon = "🧑‍💻" if chat["role"] == "user" else "🤖"
            st.markdown(f"**{role_icon} {chat['role'].capitalize()}**: {chat['content']}")


if __name__ == "__main__":
    main()
