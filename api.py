from flask import Flask, jsonify, request
import pyodbc
import pandas as pd
import json
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from sqlalchemy import create_engine

app = Flask(__name__)
global engine, host, admin, password, database
# DB SETTING
engine = '{SQL Server}'
host = ""
admin = ""
password = ""
database = ""

global ENDPOINT, API_KEY, MODEL_NAME
# Azure_Open_API SETTING
ENDPOINT = ""
API_KEY = ""
API_VERSION = "2024-02-01"
MODEL_NAME = "model-gpt4o-20240513"

global text_analytics_endpoint, text_analytics_key
# Azure_analytics_API SETTING
text_analytics_endpoint = ""
text_analytics_key = ""

@app.route("/location", methods=['GET'])
def Location():
    # DB 연결
    try:
        mssql_engine = create_engine(
                                "mssql+pyodbc://"+admin+":"+password+"@"+host+"/"+database+""
                                "?driver=SQL+Server"
                            )
        
        sql = "SELECT * FROM Locations"
        df = pd.read_sql_query(sql, mssql_engine)

        records = df.to_dict(orient='records')
        json_data = json.loads(json.dumps(records, indent=4))
        
        response = {
            "code" : 200,
            "msg" : 'success',
            'result' : json_data
        }
    except Exception as e:
        print(f"{e}")
        code = "999"
        msg = "정의되지 않은 error입니다."
        response = {
            "code" : code,
            "msg" : msg
        }
    return response

@app.route("/Review_Solution", methods=['POST'])
def Solution():
    print(request.json)
    try:
        data = request.json
        print(data)
        ###################
        ##DB_Reviews_Data##
        ###################    
        mssql_engine = create_engine(
                            "mssql+pyodbc://"+admin+":"+password+"@"+host+"/"+database+""
                            "?driver=SQL+Server"
                        )

        SC_NAME = data['SC_NAME']
        ADDRESS = data['ADDRESS']

        sql = "SELECT TOP 10 * FROM Reviews WHERE SC_NAME = N'%s' AND ADDRESS = N'%s' ORDER BY Review_Date DESC" %(SC_NAME, ADDRESS)

        df = pd.read_sql_query(sql, mssql_engine)
        print(df)

        combined_string = ''.join(df['Review'].apply(lambda x: str([x])))
        print(combined_string)
        ###################
        ##azure - Open AI##
        ###################
        client = AzureOpenAI(
            azure_endpoint=ENDPOINT,
            api_key=API_KEY,
            api_version=API_VERSION
        )

        ###### request message ######
        Content = combined_string + '해당 리뷰 10개에 대해 종합하여 좋은점과 불편한점을 한줄로 해주고 나쁜점에 대한 솔루션을 한줄로 정리해서 다른말 붙이지 말고 JSON 데이터(좋은점 : "한줄", 나쁜점 : "한줄", solution : "한줄") 해당 형식으로 제공해줘 근데 문자열로 제공해줘'
        print(Content)

        message = [
            {
                "role": "system",
                "content": "우리는 지금 대한민국 경상북도 경로당에 대한 리뷰를 보고 문제를 파악한 후 솔루션을 제공할 거야",
            },
            {
                "role": "user",
                "content": Content
            }
        ]

        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=message
        )

        # response 결과 json 화    
        json_string = completion.choices[0].message.content
        json_string_clean = json_string.replace('```json', '').replace('```', '').strip()
        print('json_string_clean:', json_string_clean)
        result_dict = json.loads(json_string_clean)
        print(result_dict)
        result = {}
        # Extract values from the dictionary
        result['good_points'] = result_dict.get('좋은점')
        result['bad_points'] = result_dict.get('나쁜점')
        result['solution'] = result_dict.get('solution')
        print(result)
        response = {
            "code" : 200,
            "msg" : 'success',
            "result" : result
        }

    except Exception as e:
        print(f"{e}")
        code = "999"
        msg = "정의되지 않은 error입니다."
        response = {
            "code" : code,
            "msg" : msg
        }

    return response

@app.route("/Review_Rating", methods=['POST'])
def Rating():
    print(request.json)
    try:
        data = request.json

        ###################
        ##DB_Reviews_Data##
        ###################    
        mssql_engine = create_engine(
                            "mssql+pyodbc://"+admin+":"+password+"@"+host+"/"+database+""
                            "?driver=SQL+Server"
                        )

        SC_NAME = data['SC_NAME']
        ADDRESS = data['ADDRESS']
        print(SC_NAME)
        print(ADDRESS)
        
        sql = "SELECT TOP 10 * FROM Reviews WHERE SC_NAME = N'%s' AND ADDRESS = N'%s' ORDER BY Review_Date DESC" %(SC_NAME, ADDRESS)

        df = pd.read_sql_query(sql, mssql_engine)

        review_list = df['Review'].tolist()

        ###################
        ##Text__Analytics##
        ###################  
        text_analytics_client = TextAnalyticsClient(text_analytics_endpoint, AzureKeyCredential(text_analytics_key))
        
        response = text_analytics_client.analyze_sentiment(review_list)
        successful_responses = [doc for doc in response if not doc.is_error]
        successful_responses

        rating = 0

        for i in successful_responses:
            rating += i['confidence_scores']['positive']

        mean = (rating/len(successful_responses))/2

        rating = mean*10

        response = {
            "code" : 200,
            "msg" : 'success',
            'result' : rating
        }
    except Exception as e:
        print(f"{e}")
        code = "999"
        msg = "정의되지 않은 error입니다."
        response = {
            "code" : code,
            "msg" : msg
        }
    return response
