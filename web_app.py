import streamlit as st
import numpy as np
import librosa
import requests
import time
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
from sklearn.preprocessing import LabelEncoder  # Import LabelEncoder from sklearn

# Cache the models to ensure they are loaded only once
@st.cache_resource
def load_audio_model(path):
    return load_model(path)

@st.cache_resource
def load_text_model(path):
    return load_model(path)

# Load the emotion recognition models
audio_model_path = 'my_model.keras'  # Ensure this file is in the same directory as this script
text_model_path = 'Emotion_Recognition_Text_new.keras'  # Ensure this file is in the same directory as this script

audio_model = load_audio_model(audio_model_path)
text_model = load_text_model(text_model_path)

# Load tokenizer and label encoder
@st.cache_resource
def load_tokenizer(path):
    with open(path, 'rb') as handle:
        return pickle.load(handle)

@st.cache_resource
def load_label_encoder(path):
    with open(path, 'rb') as handle:
        label_encoder = pickle.load(handle)
        label_encoder.fit(['angry', 'disgust', 'fear', 'happy', 'neutral', 'pleasant_surprise', 'sad'])  # Ensure label encoder is fitted
        return label_encoder

tokenizer_path = 'tokenizer.pkl'
label_encoder_path = 'label_encoder.pkl'

tokenizer = load_tokenizer(tokenizer_path)
label_encoder = load_label_encoder(label_encoder_path)


# Function to predict emotion from audio
def predict_audio_emotion(audio_file):
    try:
        y, sr = librosa.load(audio_file, sr=None)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        mfccs_scaled = np.mean(mfccs.T, axis=0)
        mfccs_scaled = mfccs_scaled.reshape(1, 40, 1)  # Adjust the shape as per the model input
        prediction = audio_model.predict(mfccs_scaled)
        emotion_index = np.argmax(prediction, axis=1)[0]
        return emotion_index  # Return the index of the highest probability
    except Exception as e:
        st.error(f"Error in predicting emotion: {e}")

# Function to preprocess input sentence
def normalized_sentence(sentence):
    # Implement your sentence normalization here
    return sentence.lower()

def preprocess_sentence(sentence, tokenizer):
    sentence = normalized_sentence(sentence)
    sentence = tokenizer.texts_to_sequences([sentence])
    sentence = pad_sequences(sentence, maxlen=229, truncating='pre')
    return sentence

# Function to predict emotion from text

# Function to predict emotion from text
def predict_text_emotion(sentence, model, label_encoder, tokenizer):
    preprocessed_sentence = preprocess_sentence(sentence, tokenizer)
    prediction = model.predict(preprocessed_sentence)
    predicted_label_index = np.argmax(prediction, axis=-1)[0]
    # Mapping label index to emotion
    emotions_mapping = {
        0: 'fear',
        1: 'joy',
        2: 'anger',
        3: 'love',
        4: 'sadness',
        5: 'surprise'
    }
    predicted_label = emotions_mapping.get(predicted_label_index, 'neutral')  # Default to 'neutral' if label not found
    return predicted_label

# Function to get text-to-speech with emotion
def text_to_speech(text, emotion):
    #typecast_api_key = '__pltj5baABN9G47V2JRrbKpCSgqGgqwWhKUiCffjBKY5'  # Replace with your actual Typecast API key
    typecast_api_key = '__pltGxD2tMfVJ8TbkFoce5JfhE5MYJChzVSC8QroSMiY'
    headers = {'Authorization': f'Bearer {typecast_api_key}'}

    # Function to get the first actor
    def get_first_actor():
        r = requests.get('https://typecast.ai/api/actor', headers=headers)
        my_actors = r.json()['result']
        return my_actors[0]['actor_id']

    # Function to request speech synthesis
    def request_speech_synthesis(text, actor_id, emotion_prompt):
        r = requests.post('https://typecast.ai/api/speak', headers=headers, json={
            'text': text,
            'lang': 'auto',
            'actor_id': actor_id,
            'xapi_hd': True,
            'model_version': 'latest',
            "emotion_tone_preset": "emotion-prompt",
            "emotion_prompt": emotion_prompt
        })
        return r.json()['result']['speak_v2_url']

    # Function to download audio file
    def download_audio_file(speak_url):
        for _ in range(120):
            r = requests.get(speak_url, headers=headers)
            ret = r.json()['result']
            if ret['status'] == 'done':
                r = requests.get(ret['audio_download_url'])
                output_path = 'output.wav'
                with open(output_path, 'wb') as f:
                    f.write(r.content)
                return output_path
            else:
                time.sleep(1)
        return None

    # Emotion mapping
    emotions = {
       
    
        "anger": "angry",
        "sadness": "sad",
        "disgust": "disgust",
        "joy": "happy",
        "neutral": "neutral",
        "excitement": "excited",
        "politeness": "polite",
        "surprise": "surprised",
        "love": "love",
        "fear":"fear",
        "gratitude":"gratitude"
    }

    actor_id = get_first_actor()
    emotion_prompt = emotions.get(emotion, "neutral")  # Default to "neutral" if emotion not found
    speak_url = request_speech_synthesis(text, actor_id, emotion_prompt)
    return download_audio_file(speak_url)

# Custom CSS for styling
light_mode_css = """
    <style>
    .main {
        background-color: #f5f5f5;
        color: #333;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
        border: none;
    }
    .stTextInput>div>input, .stFileUploader>div>div {
        background-color: #fff;
        color: #333;
        border: 2px solid #ccc;
        border-radius: 12px;
        padding: 10px;
    }
    .stAudio>div>audio {
        border: 2px solid #ccc;
        border-radius: 12px;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #333;
    }
    </style>
    """

dark_mode_css = """
    <style>
    .main {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
        border: none;
    }
    .stTextInput>div>div>input, .stFileUploader>div>div {
        background-color: #333;
        color: #fff;
        border: 2px solid #555;
        border-radius: 12px;
        padding: 10px;
    }
    .stAudio>div>audio {
        border: 2px solid #555;
        border-radius: 12px;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
    }
    .stMarkdown {
        color: #ffffff;
    }
    </style>
    """

# Initialize theme state
if "theme" not in st.session_state:
    st.session_state.theme = "Light Mode"

# Function to toggle between dark mode and light mode
def toggle_theme():
    if st.session_state.theme == "Dark Mode":
        st.session_state.theme = "Light Mode"
    else:
        st.session_state.theme = "Dark Mode"
    st.experimental_rerun()

# Streamlit app layout
st.title('Emotion Recognition and Text-to-Speech App')
st.write('This app can predict emotions from audio files and convert text to speech with specified emotions.')

# Apply the selected theme
if st.session_state.theme == "Dark Mode":
    st.markdown(dark_mode_css, unsafe_allow_html=True)
else:
    st.markdown(light_mode_css, unsafe_allow_html=True)

# Add theme toggle button
if st.button("🌞 Light Mode" if st.session_state.theme == "Light Mode" else "🌜 Dark Mode"):
    toggle_theme()

# Emotion prediction section
st.header('Predict Emotion from Audio')
audio_file = st.file_uploader('Upload an audio file', type=['wav'])
if audio_file is not None:
    emotion = predict_audio_emotion(audio_file)
    target_names = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'pleasant_surprise', 'sad']
    st.write(f'Predicted Emotion: {target_names[emotion]}')

# Text-to-speech section
st.header('Text-to-Speech with Emotion')
text = st.text_area('Enter text')
detect_emotion_automatically = st.checkbox('Detect emotion automatically from text')
if detect_emotion_automatically:
    if st.button('Generate Speech'):
        if 'tokenizer' in locals() and 'label_encoder' in locals():
            predicted_emotion = predict_text_emotion(text, text_model, label_encoder, tokenizer)
            st.write(f'Predicted Emotion from Text: {predicted_emotion}')
            output_audio_file = text_to_speech(text, predicted_emotion)  # Pass predicted emotion here
            if output_audio_file:
                audio_file = open(output_audio_file, 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/wav')
        else:
            st.error('Tokenizer and label encoder are required for emotion detection.')
else:
    emotion = st.selectbox('Select emotion', ['neutral', 'fear', 'joy', 'anger', 'love', 'sadness','surprise','gratitude','politeness','excited'])
    if st.button('Generate Speech'):
        output_audio_file = text_to_speech(text, emotion)  # Pass selected emotion here
        if output_audio_file:
            audio_file = open(output_audio_file, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/wav')

# Footer
st.markdown('---')
st.write('Developed by CodeWrapper')
