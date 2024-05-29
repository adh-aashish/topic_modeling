from fastapi import FastAPI
from fastapi.responses import JSONResponse
# from flask import Flask 
# from flask import request
from pydantic import BaseModel
from gensim import models
import pandas as pd
import os
from os import path
from utils import *
import json
import matplotlib.pyplot as plt
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

SECRET_KEY = "05c87e355fbc3044701ba8819829cfdef454bad982b1e10f85eae909e2f6ed37"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Document(BaseModel):
    content : str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "सन् २०२० को डिसेम्बर २९ मा हमासका सबै समूहका नेता इस्माइल हानियाले गाजाका विभिन्न सशस्त्र गुटहरूबीच बलियो सन्देश र एकताको सङ्केत को रूपमा पिलर छद्म नाम दिइएको चारमध्ये पहिलो सैन्य अभ्यास गर्ने घोषणा गरे। हमास गाजाको सबैभन्दा शक्तिशाली सशस्त्र समूह थियो। अन्य १० प्यालेस्टिनी समूह पनि सम्मिलित गठबन्धन हमास प्रमुख घटक थियो। ती लडाकु समूहहरू युद्धको खेलजस्तो अभ्यासमा सहभागी भए। त्यसलाई संयुक्त अपरेशन कक्षले निगरानी गरेको थियो। गाजाका सशस्त्र गुटहरूसँग एउटा केन्द्रीय कमान्डअन्तर्गत समन्वय गर्न सन् २०१८ मा उक्त संरचना बनाइएको थियो। सन् २०१८ अघि हमासले प्यालेस्टिनी इस्लामिक जिहाद (पीआईजे) सँग समन्वय गरेको थियो। पीआईजे गाजाको दोस्रो ठूलो सशस्त्र गुट हो। ब्रिटेन र अन्य देशमा उक्त सङ्गठनलाई हमासलाई जसरी नै प्रतिबन्धित आतङ्कवादी सङ्गठनका रूपमा हेरिन्छ। पहिलाका द्वन्द्वमा पनि हमासले अरू समूहहरूसँग मिलेर लडाइँ गरेको थियो। तर २०२० को अभ्यासलाई धेरै समूह एकजुट भएको प्रमाणको रूपमा प्रचारबाजी गरियो। हमास नेताले पहिलो अभ्यासले सशस्त्र समूहहरूको स्थायी तत्परता प्रतिबिम्बित गरेको बताएका थिए। तीन वर्षमा गरिएका चारवटा संयुक्त अभ्यासमध्ये सन् २०२० को अभ्यास पहिलो थियो। विभिन्न सामाजिक सञ्जालहरूमा ती सबैसँग सम्बन्धित भिडिओहरू छन्। सन्देश आदानप्रदान गर्ने एप टेलिग्राममा प्रेषित फुटेजका अनुसार स्ट्रङ पिलर अभ्यासमा सहभागी भएका पीआईजेसहित १० वटा लडाकु समूहलाई टाउकोमा बाँध्ने पट्टी र चिह्नका आधारमा बीबीसीले स्पष्टसँग पहिचान गरेको छ।"
                }
            ]
        }
    }

# app = Flask(__name__)

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    print("Here");
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

@app.get('/')
def get_all_topics():
    # topics = lda_model.print_topics(-1)
    # logging.critical(lda_model.num_topics)
    """
    - Input: GET request in '/'
    - Output: A Json in following format

    - {
       - "success": True
       - "word_clouds": [ [Topic Number, Topic Word Cloud],... for all topics ]
    - }
    """
    
    # set following to False if new model trained or folder images deleted
    word_cloud_generated = True
    if not word_cloud_generated:
        success = clear_folder(folder_path='./generated_info/word_clouds_training_data')
        logging.critical(f'success: {success}')
        if success:
            for i in range(lda_model.num_topics):
                topic_in_dict_form = dict(lda_model.show_topic(i, 20))
                plt.axis('off')
                plt.imshow(
                    WordCloud(font_path="../resources/Mangal.ttf").fit_words(topic_in_dict_form))
                img_path = f'./generated_info/word_clouds_training_data/Topic-{i+1}.png'
                # map_img_path_idx[img_path] = i+1
                plt.savefig(img_path, bbox_inches='tight')
        else:
            return {"success":False,"word_clouds":[]}
        
    img_info = images_to_base64_list(
        folder_path='./generated_info/word_clouds_training_data/')
    
    word_clouds = [(idx,val) for _,val,idx in img_info]
    
    word_clouds = sorted(word_clouds, key=lambda x: x[0])
    return {"success":True,"word_clouds":word_clouds}

@app.get('/top_five_news',deprecated=True)
def get_top_five_news_in_each_topic():
    file_path = "./generated_info/top_five_doc.txt"
    success = True
    if not os.path.exists(file_path):
        success = store_top_five_news()
    if success:   
        df = pd.read_csv('./generated_info/top_five_doc.txt')
        results = {}
        for index, row in df.iterrows():
            results[row['topic_id']]= [row['news1'],row['news2'],row['news3'],row['news4'],row['news5']]
        return {"message":results,"success":True}
    else:
        return {"message":"Error to store top 5 documents","success":False}

@app.post('/info')
def document_info(doc:Document, sort: str|None = None):
    """
    - Input: A News Document
    - Output: A Json in following format

    - {
       - "similar_news": [ [ 'title1','data1','link1','source1' ] , [ 'title2','data2','link2','source2' ] ]
       - "topic_word_clouds": [ [ score1, image1_in_base64_encoded, index1 ], [ score2, image2_in_base64_encoded, index2 ] ], 
       - "topics_by_percentage":one_image_in_base64_encoded, 
       - "success": True
    - }

    """   
    # preoperations
    success = clear_folder()
    if success:
        doc = doc.content
        df = pd.DataFrame(columns=['body'])
        df.loc[0] = [doc]
        processed_data = get_processed_data(df)
        bow_vector = id2word.doc2bow(processed_data)
        top_topics_in_a_doc = sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1])
        top_topics_in_a_doc = [(i, j) for i, j in top_topics_in_a_doc if j > 0.08]
        #  list_of_images for a document is [ [highest_score, topic1], [ next_highest_score, topic2]]

        list_of_images = get_imgs_of_topics_word_cloud(top_topics_in_a_doc)

        topic_dis_img = get_topics_bar_chart_by_percentage(top_topics_in_a_doc)
        if sort == "date":
            similar_news = get_similar_news(bow_vector,sort)
        else:
            similar_news = get_similar_news(bow_vector, 'relevance')

        return {"success": True,"similar_news":similar_news,"topic_word_clouds": tuple(list_of_images), "topics_by_percentage":topic_dis_img} 

    else:
        return {"success":False}

@app.get('/topics/{id}')
def top_news_of_topic(id: int, sort: str|None = None):
    file_path = './generated_info/top_news_per_topic_26_topics_setopati_1.csv'
    if not path.exists(file_path):
        # create that file
        success = store_top_news_per_topic()
        if not success:
            return {"success":False}
    
    news_df = pd.read_csv('./generated_info/top_news_per_topic_26_topics_setopati_1.csv')
    curr_topic_df = news_df[news_df['topic_no'] == id]
    if sort == "date" :
        curr_topic_df = curr_topic_df.sort_values(by='Year', ascending=False)
        result = curr_topic_df.to_dict(orient='records')
    else:
        # this is sort = "relevance" or garbage if entered by user
        result = curr_topic_df.to_dict(orient='records')

    topic_trend_img = get_topic_trend_image(id)
    return {"success": True, "topic_id":id, "top_news": result, "topic_trend":topic_trend_img}
    
@app.get('/topic_dis_of_all_news')
def topic_distribution_of_all_news():
    # till now this is gotten by running on setopati_preprocessed_1 i.e first dataset 
    img = images_to_base64_list(f'../core/results/visualization/topic_distribution_of_40k_data.png')[0]
    return {"success":True, "img":img}

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
