from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

from flask_restful import Resource
from flask import request
from knowledge.knowledgeUtils import search_knowledge
import json

class KnowledgeManage(Resource):
    def post(self):
        # Get the query from the request
        responsedata = request.data
        query = json.loads(responsedata)['query']
        # Call the knowledge search function with the query
        result =  search_knowledge(query)
        return result
