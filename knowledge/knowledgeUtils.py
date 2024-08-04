from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())  # load .env file

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS  # , Pinecone, Weaviate
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader, UnstructuredWordDocumentLoader, UnstructuredPDFLoader
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
import os
from langchain_core.prompts import PromptTemplate


# load all markdown files in the knowledge directory
def load_knowledge_file_init():
    if not os.path.exists(os.getenv('vectorstores_path')):
        os.makedirs(os.getenv('vectorstores_path'))
    files = os.listdir(os.getenv('knowledge_file_path'))
    raw_documents = []
    for file in files:
        if file.endswith('.txt'):
            loader = TextLoader(os.path.join(os.getenv('knowledge_file_path'), file), encoding='utf-8')
        elif file.endswith('.docx') or file.endswith('.doc'):
            loader = UnstructuredWordDocumentLoader(os.path.join(os.getenv('knowledge_file_path'), file),
                                                    encoding='utf-8')
        elif file.endswith('.pdf'):
            loader = UnstructuredPDFLoader(os.path.join(os.getenv('knowledge_file_path'), file), encoding='utf-8')
        else:
            print("wrong type {file}".format(file=file))
            continue
        raw_documents += loader.load()
    textsplitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    documents = textsplitter.split_documents(raw_documents)
    db = FAISS.from_documents(documents, OpenAIEmbeddings(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        openai_api_base=os.getenv('OPENAI_BASE_URL')
    ))
    db.save_local(os.path.join(os.getenv('vectorstores_path'), 'faiss_index'))

def load_localpath_db():
    db = FAISS.load_local(os.path.join(os.getenv('vectorstores_path'), 'faiss_index'), OpenAIEmbeddings(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        openai_api_base=os.getenv('OPENAI_BASE_URL')
    ), allow_dangerous_deserialization=True)
    return db

# 增加新文件到知识库
def add_knowledge_db(filename):
    global loader
    if not os.path.exists(os.path.join(os.getenv('knowledge_file_path'),filename)):
        return {"status": "error", "message": "file not exist"}

    if filename.endswith('.txt'):
        loader = TextLoader(os.path.join(os.getenv('knowledge_file_path'), filename), encoding='utf-8')
    elif filename.endswith('.docx') or filename.endswith('.doc'):
        loader = UnstructuredWordDocumentLoader(os.path.join(os.getenv('knowledge_file_path'), filename),                                          encoding='utf-8')
    elif filename.endswith('.pdf'):
        loader = UnstructuredPDFLoader(os.path.join(os.getenv('knowledge_file_path'), filename), encoding='utf-8')
    else:
        print("wrong type {file}".format(file=filename))
    raw_documents = loader.load()
    textsplitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    documents = textsplitter.split_documents(raw_documents)
    db_all = load_localpath_db()
    db = FAISS.from_documents(documents, OpenAIEmbeddings(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        openai_api_base=os.getenv('OPENAI_BASE_URL')
    ))
    db_all.merge_from(db)
    db_all.save_local(os.path.join(os.getenv('vectorstores_path'), 'faiss_index'))
    return {"status": "success", "message": "add file to knowledge db success"}

def search_knowledge(query):
    if not os.path.exists(os.path.join(os.getenv('vectorstores_path'), 'faiss_index')):
        load_knowledge_file_init()
    else:
        db = load_localpath_db()
        llm = OpenAI(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            openai_api_base=os.getenv('OPENAI_BASE_URL')
        )
        prompt_template = """
        Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer in chinese:
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain_type_kwargs = {"prompt": prompt}
        chain = RetrievalQA.from_chain_type(llm, chain_type="stuff",
                                            retriever=db.as_retriever(search_type="similarity", search_kwargs={"k": 1}),
                                            chain_type_kwargs=chain_type_kwargs)
        return chain.invoke({"query": query})


if __name__ == "__main__":
    print(search_knowledge("如何检查master组件是否运行正常?"))
