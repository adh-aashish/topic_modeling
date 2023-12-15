# from fastapi import FastAPI
# from fastapi.responses import JSONResponse
from flask import Flask 
from flask import request
from pydantic import BaseModel
from gensim import models,corpora
import pandas as pd
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import shortuuid
from utils import *
import json

# app = FastAPI()
app = Flask(__name__)

@app.get('/')
def get_all_topics():
    topics = lda_model.print_topics(-1)
    print(topics)
    return json.dumps({"message":topics})

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
        return json.dumps({"message":results,"success":True})
    else:
        return json.dumps({"message":"Error to store top 5 documents","success":False})

@app.route('/info',methods=['POST'])
def document_info():
    print(json.loads(request.data))
    return json.dumps({})
    # preoperations
    # clear_folder()
    # # doc = doc.content
    # df = pd.DataFrame(columns=['body'])
    # df.loc[0] = [doc]
    # df['body'] = df['body'].apply(str)
    # processed_data = string_manipulation(df)
    # processed_data = processed_data['body'].to_list()[0]
    # processed_data = tokenize.tokenizer(processed_data)
    # processed_data = get_stem(processed_data,stemmer)
    # processed_data = clean_data(processed_data,stopwords)
    # # 
    # id2word = corpora.Dictionary.load('../saved_model/dictionary_1')
    # bow_vector = id2word.doc2bow(processed_data)
    # top_topics_in_a_doc = sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1])
    # list_of_images = []
    # for i in top_topics_in_a_doc:
    #     topic_in_dict_form = dict(lda_model.show_topic(i[0],20))
    #     plt.axis('off')
    #     plt.imshow(WordCloud(font_path="../resources/Mangal.ttf").fit_words(topic_in_dict_form))
    #     random_img_name = shortuuid.uuid()+'.png'
    #     random_img_path = f'./generated_info/{random_img_name}'
    #     # plt.savefig(random_img_path, bbox_inches='tight')
    # # list_of_images =  images_to_base64_list()
    
    # return json.dumps({"message": list_of_images, "top_topics": top_topics_in_a_doc, "success": True})

# test api routes
@app.get("/getimages")
def get_image():
    encoded_imgs = images_to_base64_list('./generated_info') 
    return json.dumps({'result': encoded_imgs})

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
    
@app.get('/clean_folder')
def clean_folder(folder_path:str='./generated_info'):
# print(folder_path+'*')
    files = glob.glob(folder_path+'/*')
    for f in files:
        os.remove(f)
    return json.dumps({"success":True,"files":files})


# if __name__=="__main__":
#     app.run(host="0.0.0.0",port="5000",debug=True)