from fastapi import FastAPI
from fastapi.responses import JSONResponse
# from flask import Flask 
# from flask import request
from pydantic import BaseModel
from gensim import models
import pandas as pd
import os

from utils import *
import json
import matplotlib.pyplot as plt
import numpy as np
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Document(BaseModel):
    content : str

# app = Flask(__name__)

@app.get('/')
def get_all_topics():
    topics = lda_model.print_topics(-1)
    print(topics)
    return {"message":topics}

@app.get('/top_five_news')
def get_top_five_news_in_each_topic():
    file_path = "../saved_model/top_five_doc.txt"
    success = True
    if not os.path.exists(file_path):
        success = store_top_five_news()
    if success:   
        df = pd.read_csv('../saved_model/top_five_doc.txt')
        results = {}
        for index, row in df.iterrows():
            results[row['topic_id']]= [row['news1'],row['news2'],row['news3'],row['news4'],row['news5']]
        return {"message":results,"success":True}
    else:
        return {"message":"Error to store top 5 documents","success":False}

@app.post('/info')
def document_info(doc:Document):
    """
    - Input: A News Document
    - Output: A Json in following format

    - {
       - "topic_word_clouds": list_of_images_in_base64_encoded, 
       - "topics_by_percentage":one_image_in_base64_encoded, 
       - "success": True
    - }

    """
    # preoperations
    clear_folder()
    doc = doc.content
    
    df = pd.DataFrame(columns=['body'])
    df.loc[0] = [doc]
    processed_data = get_processed_data(df)
    bow_vector = id2word.doc2bow(processed_data)
    top_topics_in_a_doc = sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1])
    
    list_of_images = get_imgs_of_topics_word_cloud(top_topics_in_a_doc)
    
    topic_dis_img = get_topics_bar_chart_by_percentage(top_topics_in_a_doc)
    # return {"message": doc}
    # with open('test.txt','w') as f:
    #     f.write(topic_dis_img)
    return {"topic_word_clouds": list_of_images, "topics_by_percentage":topic_dis_img, "success": True}




# test api routes [ not called by client but just for testing purposes in backend ]
@app.get("/getimages",deprecated=True)
def get_image():
    encoded_imgs = images_to_base64_list('./generated_info') 
    return JSONResponse({'result': encoded_imgs})

    # the below works------------ 
    # zip_buffer = io.BytesIO()
    # with zipfile.ZipFile(zip_buffer, "w") as zip_file:
    #     for img_path in img_paths:
    #         img_name = os.path.basename(img_path)
    #         zip_file.write(img_path, img_name)

    # # Move the buffer's position to the beginning
    # zip_buffer.seek(0)

    # # Return the zip file as a StreamingResponse
    # return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": "attachment;filename=images.zip"})
    # the above works------------ 
    
    # return []


@app.get('/clean_folder',deprecated=True)
def clean_folder(folder_path: str = './generated_info/word_clouds'):
    # print(folder_path+'*')
    files = glob.glob(folder_path+'/*')
    for f in files:
        os.remove(f)
    return {"success": True, "files": files}
