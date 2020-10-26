import os
import json
import jwt
import logging
import pymysql
from flask import abort, Flask, jsonify, render_template, request, redirect, url_for
from flask import Response

# from flask_cors import CORS
from db import db


# project_folder = os.path.expanduser('~/Project1')  # adjust as appropriate
# load_dotenv(os.path.join(".", '.env'))

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

app = Flask(__name__, template_folder='static')
db = db.Database()
username = None

@app.route('/homepage')
def homepage():
    global username
    username = request.args.get("user")
    # accToken = jwt.decode(token, algorithms=['RS256'])
    print(username)

    resp, status = db.read(id=None, username=username)
    # if status != 200:
    #     return jsonify({"status": "get all failed", "error": resp}), status
    print(resp, status)
    file_list = []

    for r in resp:
        filename = r[9]
        filename = filename[filename.rindex("/")+1:]
        file_list.append({
            "id": r[0],
            "username": r[1],
            "filename": filename,
            "firstname": r[2],
            "lastname": r[3],
            "uploadTime": r[4],
            "createdAt": r[5],
            "description": r[7],
            "filekey": r[9]
        })    
    return render_template('./sample/home.html', file_list=file_list)
    # return render_template('login-form.html')

@app.route('/')
def index():
    return render_template('./sample/index.html')

@app.route('/downloadFile', methods=['POST'])
def downloadFile():
    global username
    key = request.args.get("key")
    n = key.rindex("/")
    filename = key[n+1:]
    print(username)
    file = s3_api.download_file(key, filename)
    return Response(
        file,
        mimetype='text/plain',
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )    
    # return jsonify({"status": "sucess", "msg": "Hello"}), 200

    # s3_api.download_file()

@app.route('/uploader', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    username = request.form["username"]
    description = request.form["description"]
    n = username.rindex("=")
    username = username[n+1:]
    print(username)

    
    if uploaded_file.filename != '':
        filename = uploaded_file.filename
        resp, err = s3_api.save_to_s3(uploaded_file, username, filename, description)
        if not err:
            print("Error", err)
            return jsonify({"status": "insert failed", "error": resp}), 500
        print(resp)

    print("us", username)
    return jsonify({"status": "sucess", "msg": resp}), 200



@app.route('/upload', methods=['POST', 'GET'])
def data():
    
    # POST a data to database
    if request.method == 'POST':
        body = request.json
        print(body)
        if body:
            if "username" not in body:
                return jsonify({"status": "failed", "msg": "username required"}), 400
            elif "firstname" not in body:
                return jsonify({"status": "failed", "msg": "firstname required"}), 400
            elif "lastname" not in body:
                return jsonify({"status": "failed", "msg": "lastname required"}), 400
            elif "uploadTime" not in body:
                return jsonify({"status": "failed", "msg": "uploadTime required"}), 400
            elif "description" not in body:
                return jsonify({"status": "failed", "msg": "description required"}), 400

            # username = body['username']
            # firstname = body["firstname"]
            # lastname = body["lastname"]
            # uploadTime = body["uploadTime"]
            # description = body["description"]
            body["filekey"] = "pbox-storage/"
            resp, status = db.insert(body)
            if status != 200:
                return jsonify({"status": "insert failed", "error": resp}), status
                # return Response({"status": "insert failed", "error": err}, 500, mimetype='application/json')
            
            return jsonify({"status": "insert success", "data": resp}), status
            # return Response({"status": "insert success", "data": resp}, 200, mimetype='application/json')

        else:
            return Response({"status": "failed, ", "msg": "invalid request body"}, 400, mimetype='application/json')


        # resp, err, status = db.insert(body)
        # if not err:
        #     return jsonify({"status": "post failed", "error": err}), 500
        #     # return Response({"status": "post failed", "error": resp}, 500, mimetype='application/json')

        # return jsonify({"status": "post success", "data": resp}), 200
        # return Response({"status": "post success", "data": resp}, 200, mimetype='application/json')
    
    # GET all data from database
    if request.method == 'GET':
        resp, status = db.read(None)
        if status != 200:
            return jsonify({"status": "get all failed", "error": resp}), status
            # return Response({"status": "get all failed", "error": err}, 404, mimetype='application/json')

        result = []

        for r in resp:
            result.append({
                "id": r[0],
                "username": r[1],
                "firstname": r[2],
                "lastname": r[3],
                "uploadTime": r[4],
                "createdAt": r[5],
                "updatedAt": r[6],
                "description": r[7],
                "isDeleted": r[8]
            })
        print(resp, result)
        return jsonify({"status": "get all success", "data": result}), status
        # return Response({"status": "get all success", "data": result}, 200, mimetype='application/json')


@app.route('/upload/<string:id>', methods=['GET', 'DELETE', 'PUT'])
def onedata(id):

    # GET a specific data by id
    if request.method == 'GET':
        r, status = db.read(id)
        if status != 200:
            return jsonify({"status": "get failed", "error": r}), status
            # return Response({"status": "get failed", "error": err}, 500, mimetype='application/json')

        print(r)
        if len(r) > 0:
            r = r[0]
            result = {
                "id": r[0],
                "username": r[1],
                "firstname": r[2],
                "lastname": r[3],
                "uploadTime": r[4],
                "createdAt": r[5],
                "updatedAt": r[6],
                "description": r[7],
                "isDeleted": r[8]
            }

            return jsonify({"status": "get success", "data": result}), status
        else:
            return jsonify({"status": "not found", "data": f"No record found for id: {id}"}), 404
        # return Response({"status": "get success", "data": result}, 200, mimetype='application/json')

        
    # DELETE a data
    if request.method == 'DELETE':
        resp, status = db.delete(id)
        if status != 204:
            return jsonify({"status": "delete failed", "error": resp}), status
            # return Response({"status": "delete failed", "error": err}, 500, mimetype='application/json')
        if resp > 0:
            return jsonify({"status": "delete success", "data": resp}), 200
        else:
            return jsonify({"status": "not found", "data": f"No record found to delete for id: {id}"}), 404

        # return Response({"status": "delete success", "data": resp}, 200, mimetype='application/json')


    # UPDATE a data by id
    if request.method == 'PUT':
        if id is None:
            return jsonify({"status": "failed",  "msg": "invalid id to update data"}), 400

        body = request.json
        if body:
            if "username" not in body:
                return jsonify({"status": "failed", "msg": "username required"}), 400
            elif "firstname" not in body:
                return jsonify({"status": "failed", "msg": "firstname required"}), 400
            elif "lastname" not in body:
                return jsonify({"status": "failed", "msg": "lastname required"}), 400
            elif "uploadTime" not in body:
                return jsonify({"status": "failed", "msg": "uploadTime required"}), 400
            elif "updatedAt" not in body:
                return jsonify({"status": "failed", "msg": "updatedAt required"}), 400
            elif "description" not in body:
                return jsonify({"status": "failed", "msg": "description required"}), 400

            # username = body['username']
            # firstname = body["firstname"]
            # lastname = body["lastname"]
            # uploadTime = body["uploadTime"]
            # description = body["description"]

            resp, status = db.update(id, body)
            if status != 201:
                return jsonify({"status": "update failed", "error": resp}), status
                # return Response({"status": "update failed", "error": err}, 500, mimetype='application/json')
            
            return jsonify({"status": "update success", "data": resp}), status
            # return Response({"status": "update success", "data": resp}, 200, mimetype='application/json')

        else:
            return jsonify({"status": "failed",  "msg": "invalid request body"}), 400
            # return Response({"status": "failed, ", "msg": "invalid request body"}, 400, mimetype='application/json')



def setEnv():
    aws_config = open("config.json").read()
    config = json.loads(aws_config)
    print(json.dumps(config, indent=2))

    os.environ["PBOX_REGION"] = config["PBOX_REGION"]
    os.environ["PBOX_BUCKET"] = config["PBOX_BUCKET"]
    os.environ["PBOX_AWS_KEY"] = config["PBOX_AWS_KEY"]
    os.environ["PBOX_AWS_SECRET"] = config["PBOX_AWS_SECRET"]
    os.environ["PBOX_S3_URL"] = config["PBOX_S3_URL"]
    os.environ["PBOX_DBHOST"] = config["PBOX_DBHOST"]
    os.environ["PBOX_DBNAME"] = config["PBOX_DBNAME"]
    os.environ["PBOX_DB_USERNAME"] = config["PBOX_DB_USERNAME"]
    os.environ["PBOX_DB_PASSWORD"] = config["PBOX_DB_PASSWORD"]

    

if __name__ == "__main__":
    logger.info("Starting Pbox-App !!!")
    logger.info("Connecting to DB !!!")

    if not db.validate_db_init():
        logger.error("Connection to DB failed !!!")
        logger.info("Shutting down Pbox-App !!!")
        os._exit(0)
    
    testdata = open("app.py").read()
    from s3 import s3_api
    # s3_api.list_all_data()
    # resp, err = s3_api.save_to_s3(testdata, "mmgehlot", "app.py", "sdfsadfsadf")
    # if not err:
    #     print(err)
    
    # print(resp)

    app.run(port=9000, ssl_context="adhoc")
    

