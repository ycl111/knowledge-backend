import flask_restful
from knowledge.fileManage import FileManage,DeleteFile
from knowledge.knowledgeManage import KnowledgeManage

api = flask_restful.Api(catch_all_404s=True)


api.add_resource(DeleteFile, '/api/deletefile/<string:filename>')
api.add_resource(FileManage, '/api/filemanage')
api.add_resource(KnowledgeManage, '/api/knowledge')