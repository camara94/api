import os
import cv2
import requests
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, send_file, render_template

from tensorflow import keras
from keras.preprocessing import image as IMG
import numpy as np

from io import BytesIO
import io
from PIL import Image

from skimage import io, transform
import requests

import urllib


UPLOAD_FOLDER = "static"

base_dir = './../data_2'
liste_dossier = os.listdir(base_dir + "/train")

classes = []

for c in liste_dossier:
    classes.append(' '.join(c.title().split('_')))


f = open("classes.txt", "a+")

for i, t in enumerate(classes):
    f.write(f'{i+1}-{t}\n')
f.close()


def url_to_img(url, save_as=''):
    img = Image.open(BytesIO(requests.get(url).content))
    if save_as:
        img.save(save_as)
    return np.array(img)


def model(lien_model):
    return keras.models.load_model(lien_model)


def predict(image_url, model=model("../model/model_88_91.h5")):
    # predicting images

    img = IMG.load_img(image_url, target_size=(150, 150))
    x = IMG.img_to_array(img)
    x = x/255
    x = np.expand_dims(x, axis=0)

    images = np.vstack([x])
    resulat = model.predict(images, batch_size=10)
    percent = resulat.max()

    label = classes[np.argmax(resulat)]

    return (label, percent)


# app = Flask(__name__)
app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Upload API


@app.route('/uploadfile', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("saved file successfully")
      # send file name as parameter to downlad
            return redirect('/return-files/' + filename)

    return render_template('form.html')

# Download API


@app.route("/downloadfile/<filename>", methods=['GET', 'POST'])
def download_file(filename):
    return render_template('download.html', value=filename)


@app.route('/return-files/<filename>', methods=['GET', 'POST'])
def return_files_tut(filename):
    if request.method == 'POST':
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_path = UPLOAD_FOLDER + '/' + filename
            label, pourcentage = predict(image_url=file_path)

            file = "http://localhost:5000/static/" + filename
            lab = f"{label} : {pourcentage*100:.2f}%"
            return render_template('index.html', value={"image": file, "label": lab})

    file_path = UPLOAD_FOLDER + '/' + filename
    label, pourcentage = predict(image_url=file_path)

    file = "http://localhost:5000/static/" + filename
    lab = f"{label} : {pourcentage*100:.2f}%"
    return render_template('index.html', value={"image": file, "label": lab})


if __name__ == "__main__":
    app.run(host='0.0.0.0')
