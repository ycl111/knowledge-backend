from flask_restful import Resource
from dotenv import load_dotenv, find_dotenv
import os
from flask import request
from werkzeug.utils import secure_filename
from knowledge.knowledgeUtils import add_knowledge_db
from knowledge.knowledgeUtils import load_knowledge_file_init

load_dotenv(find_dotenv())


class DeleteFile(Resource):  # pylint: disable=abstract-method
    # 删除文件
    def delete(self, filename):
        if os.path.exists(os.path.join(os.getenv("knowledge_file_path"), filename)):
            os.remove(os.path.join(os.getenv("knowledge_file_path"), filename))
            load_knowledge_file_init()
            return {"status": "success", "message": "File deleted successfully"}
        else:
            return {"status": "error", "message": "File not found"}


class FileManage(Resource):  # pylint: disable=abstract-method
    # 获取文件列表
    def get(self):
        file_path = os.getenv("knowledge_file_path")
        if not os.path.exists(file_path):
            return {"status": "error", "message": "File path not found"}
        else:
            files = os.listdir(file_path)
            return {"status": "success", "message": "File list retrieved successfully", "data": files}

    # 上传文件
    def post(self):  # pylint: disable=no-self-use
        files = request.files.getlist('file')
        error_message = []
        file_path = os.getenv("knowledge_file_path")
        if files:
            for file in files:
                try:
                    filename = secure_filename(file.filename)
                    if not (filename.endswith('.txt') or filename.endswith('.doc') or filename.endswith(
                            '.docx') or filename.endswith('.pdf')):
                        error_message.append(
                            "{file} type is wrong,Only txt, doc, docx and pdf files are allowed".format(file=filename))
                    file.save(os.path.join(file_path, filename))
                    if os.path.exists(os.path.join(file_path, filename)):
                        # 文件上传成功后，知识库增加一条记录
                        result = add_knowledge_db(filename)
                        if result["status"] != "success":
                            error_message.append(
                                "{file} uploaded successfully but failed to add knowledge record".format(file=filename))
                    else:
                        error_message.append("{file} uploaded error".format(file=filename))

                except Exception as e:
                    error_message.append("{file} error is".format(file=file.filename) + str(e))
        else:
            error_message.append("No file uploaded")
        if len(error_message) == 0:
            return {"status": "success", "message": "File uploaded successfully"}
