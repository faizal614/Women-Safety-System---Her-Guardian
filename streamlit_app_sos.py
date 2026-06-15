import streamlit as st
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
import pywhatkit
import requests
import datetime

def send_sos_whatsapp_message(phone_number):
    try:
        response = requests.get('http://ip-api.com/json/')
        location_info = response.json()
        latitude = location_info['lat']
        longitude = location_info['lon']
        location = f"{location_info['city']}, {location_info['country']}"  
        sos_message = f"SOS Alert! Harassment detected. Latitude: {latitude} Longitude: {longitude}. Current location: {location}. Please check on me immediately."
        pywhatkit.sendwhatmsg(phone_number, sos_message, datetime.datetime.now().hour, (datetime.datetime.now().minute + 1) % 60)
        #time.sleep(55) 
    except Exception as e:
        print(f"Error sending SOS WhatsApp message: {e}")

def predict_and_display_camera(model, base_model, phone_number):
    cap = cv2.VideoCapture(0)
    

    st.write("Live Stream:")
    stream = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        resized_frame = cv2.resize(frame, (224, 224))
        preprocessed_frame = img_to_array(resized_frame)
        preprocessed_frame = np.expand_dims(preprocessed_frame, axis=0)
        preprocessed_frame = preprocess_input(preprocessed_frame)

        features = base_model.predict(preprocessed_frame)
        features_flatten = features.reshape(1, -1)

        prediction = model.predict(features_flatten)[0]
        class_label = np.argmax(prediction)
        class_prob = prediction[class_label]

        label = "Harassment" if class_label == 1 else "Non-Harassment"
        prob_text = f"{label} ({class_prob:.2f})"

        if class_label == 1:# Harassment detected
            send_sos_whatsapp_message(phone_number)
            
                

        cv2.putText(frame, prob_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        stream.image(frame, channels="BGR", caption="Live Prediction")

    cap.release()

def main():
    st.title("Live Harassment Detection")

    model_path = "./my_model2.h5"
    model = load_model(model_path)
    base_model = VGG16(weights='imagenet', include_top=False)

    st.write("Press the button to start prediction:")
    phone_number = st.text_input("Enter SOS WhatsApp number (with country code):", "+1234567890")
    if st.button("Start Prediction"):
        predict_and_display_camera(model, base_model, phone_number)

if __name__ == "__main__":
    main()
