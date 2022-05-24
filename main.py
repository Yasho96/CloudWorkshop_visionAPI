from fileinput import filename
from pkgutil import iter_modules
from queue import Empty
import sys
import os
import io
from os import access
from sys import prefix

from flask import Flask, flash, redirect, request, render_template
from google.cloud import storage
from google.cloud import vision


app = Flask(__name__, template_folder='template')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_key.json"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("Data Received")
    return render_template('index.html')


@app.route('/callCategorize', methods=['GET', 'POST'])
def callCategorize():

    from google.cloud import storage
    from google.cloud import vision

    catImg = []
    dogImg = []

    bucket_name = "piyumi_test_bucket"

    storage_client = storage.Client()

    blobs = storage_client.list_blobs(bucket_name) #Reading the images in the bucket

    for blob in blobs:
        imageUri = ("gs://piyumi_test_bucket/"+blob.name) #Take the name of the image in the bucket

        client = vision.ImageAnnotatorClient()
        image = vision.Image()

        image.source.image_uri = imageUri
        objects = client.object_localization(
            image=image).localized_object_annotations

        len(objects)

        for object_ in objects:

            if object_.name == "Cat" or object_.name == "CAT" or object_.name == "cat" and object_.score > 0.80:
                catImg.append('Img Name: {} , Confidence: {}'.format(
                    blob.name, '%.2f%%' % (object_.score*100.)))

            if object_.name == "Dog" or object_.name == "DOG" or object_.name == "dog" and object_.score > 0.80:
                dogImg.append('Img Name: {} , Confidence: {}'.format(
                    blob.name, '%.2f%%' % (object_.score*100.)))

    return render_template('categorize.html', catImg=catImg, dogImg=dogImg)


@app.route('/callImgGallery', methods=['GET', 'POST'])
def callImgGallery():

    from google.cloud import storage
    from google.cloud import vision

    catImgUri = []
    dogImgUri = []

    bucket_name = "piyumi_test_bucket"
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name) #Reading the images in the bucket

    for blob in blobs:
        imageUri = ("gs://piyumi_test_bucket/"+blob.name) #Take the name of the image in the bucket
        publicImgUri = (
            'https://storage.googleapis.com/piyumi_test_bucket/'+blob.name) #Setting the above taken name to the end of the common link

        client = vision.ImageAnnotatorClient()
        image = vision.Image()

        image.source.image_uri = imageUri
        objects = client.object_localization(
            image=image).localized_object_annotations

        len(objects)

        for object_ in objects:

            if object_.name == "Cat" and object_.score > 0.80:
                catImgUri.append(publicImgUri)

            if object_.name == "Dog" and object_.score > 0.80:
                dogImgUri.append(publicImgUri)

    return render_template('img_display.html', catImgUri=catImgUri, dogImgUri=dogImgUri)

@app.route('/detect-Web-entities', methods=['GET', 'POST'])
def detectWebEntities():

    return render_template('detect-web-entities.html')


@app.route('/upload-image', methods=['GET', 'POST'])
def uploadImage():

    if request.method == 'POST':

        objectName = []
        isEmpty = False
        publicImgUri = ''

        if 'file' not in request.files:
            return redirect(request.url) #if the file is not in there redirect back to the url

        file = request.files['file']

        if file == '':
            return redirect(request.url) #if the file is empty, redirect

        if file:

            print(file)

            storage_client = storage.Client()
            bucket = storage_client.bucket("piyumi_bucket_2")
            filename = '%s/%s' % ('images', file.filename) #creates a images directory inside the bucket and assign the image with the filename

            blob = bucket.blob(filename, chunk_size=262144 * 5)
            blob.upload_from_file(file, file.content_type) # Does the file upload

            image_uri = ('gs://piyumi_bucket_2/images/'+file.filename)
            publicImgUri = ("https://storage.googleapis.com/piyumi_bucket_2/images/"+file.filename)

            client = vision.ImageAnnotatorClient()
            image = vision.Image()
            image.source.image_uri = image_uri

            response = client.web_detection(image=image)
            annotations = response.web_detection

            if annotations.pages_with_matching_images:

                for page in annotations.pages_with_matching_images:
                    objectName.append(format(page.url))

            else:
                isEmpty = True

        return render_template('detect-web-entities.html', objectName=objectName, isEmpty=isEmpty, publicImgUri=publicImgUri)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
