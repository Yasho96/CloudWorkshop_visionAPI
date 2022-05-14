from pkgutil import iter_modules
import sys
import os

from flask import Flask, request, render_template


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


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
