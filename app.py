from flask import Flask, render_template,  request, Markup
import numpy as np
import pandas as pd
from utils.disease import disease_dic
import pickle
import io
import torch
from torchvision import transforms
from PIL import Image
from utils.model import ResNet9

app = Flask(__name__)


disease_classes = ['Apple___Apple_scab',
                   'Apple___Black_rot',
                   'Apple___Cedar_apple_rust',
                   'Apple___healthy',
                   'Blueberry___healthy',
                   'Cherry_(including_sour)___Powdery_mildew',
                   'Cherry_(including_sour)___healthy',
                   'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
                   'Corn_(maize)___Common_rust_',
                   'Corn_(maize)___Northern_Leaf_Blight',
                   'Corn_(maize)___healthy',
                   'Grape___Black_rot',
                   'Grape___Esca_(Black_Measles)',
                   'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
                   'Grape___healthy',
                   'Orange___Haunglongbing_(Citrus_greening)',
                   'Peach___Bacterial_spot',
                   'Peach___healthy',
                   'Pepper,_bell___Bacterial_spot',
                   'Pepper,_bell___healthy',
                   'Potato___Early_blight',
                   'Potato___Late_blight',
                   'Potato___healthy',
                   'Raspberry___healthy',
                   'Soybean___healthy',
                   'Squash___Powdery_mildew',
                   'Strawberry___Leaf_scorch',
                   'Strawberry___healthy',
                   'Tomato___Bacterial_spot',
                   'Tomato___Early_blight',
                   'Tomato___Late_blight',
                   'Tomato___Leaf_Mold',
                   'Tomato___Septoria_leaf_spot',
                   'Tomato___Spider_mites Two-spotted_spider_mite',
                   'Tomato___Target_Spot',
                   'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
                   'Tomato___Tomato_mosaic_virus',
                   'Tomato___healthy']

disease_model_path = 'models/plant_disease_model.pth'
disease_model = ResNet9(3, len(disease_classes))
disease_model.load_state_dict(torch.load(
    disease_model_path, map_location=torch.device('cpu')))
disease_model.eval()


# Loading crop recommendation model

# crop_recommendation_model_path = 'models/RandomForest.pkl'
# crop_recommendation_model = pickle.load(
#     open(crop_recommendation_model_path, 'rb'))


# =========================================================================================

# Custom functions for calculations

def predict_image(img, model=disease_model):
    """
    Transforms image to tensor and predicts disease label
    :params: image
    :return: prediction (string)
    """
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.ToTensor(),
    ])
    image = Image.open(io.BytesIO(img))
    img_t = transform(image)
    img_u = torch.unsqueeze(img_t, 0)

    # Get predictions from model
    yb = model(img_u)
    # Pick index with highest probability
    _, preds = torch.max(yb, dim=1)
    prediction = disease_classes[preds[0].item()]
    # Retrieve the class label
    return prediction
# _________________________________________________________________________________________





@app.route('/', methods=['POST','GET'])
def disease_prediction():
    title = 'PDD - Disease Detection'

    # if request.method == 'POST':
    if 'file' not in request.files:
        return render_template('index.html', title=title)
    file = request.files.get('file')
        # if not file:
    #     return render_template('index.html', title=title)
    try:
        if file:
            img = file.read()
            prediction = predict_image(img)
            prediction = Markup(str(disease_dic[prediction]))
            return render_template('temp.html', prediction=prediction, img = file, title=title)
    except:
        pass
    return render_template('index.html', title=title)

@app.route('/result')
def result():
    title= 'Disease Result'
    file = request.files.get('file')
    print(file)
    if file:
        img = file.read()
        prediction = predict_image(img)
        prediction = Markup(str(disease_dic[prediction]))
        print(prediction)
        return render_template('temp.html', prediction = prediction, title=title)
    return render_template('temp.html', prediction = "prediction", title=title)

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
