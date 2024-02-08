from config import *
import os
from dotenv import load_dotenv, find_dotenv
from langchain_community.llms.ctransformers import CTransformers
from ctransformers import AutoConfig
from ctransformers import AutoModelForCausalLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts.prompt import PromptTemplate
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores.weaviate import Weaviate
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
import weaviate
load_dotenv(find_dotenv())

class LifeGuru:

    def __init__(self):
        self.books_folder = 'books'
        self.db = None
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        auth_config = weaviate.auth.AuthApiKey(api_key=self.weaviate_api_key)
        self.client = weaviate.Client(
            url=os.getenv("WEAVIATE_CLUSTER_URL"),
            auth_client_secret=auth_config
        )
        self.prompt_template = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=INPUT_VARIABLES
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=SEPARATORS,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        # config = AutoConfig.from_pretrained("TheBloke/Mistral-7B-v0.1-GGUF")
        # config.config.max_new_tokens = 2000
        # config.config.context_length = 4000
        # self.llm = AutoModelForCausalLM.from_pretrained(
        #     "TheBloke/Mistral-7B-v0.1-GGUF",
        #     model_file="mistral-7b-v0.1.Q5_K_M.gguf",
        #     model_type="mistral",
        #     gpu_layers=10,
        #     config=config
        # )
        self.llm = CTransformers(
            model=MODEL,
            model_type=MODEL_TYPE,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            gpu_layers=10,
            context_length = 6000
        ) 
        self.hfembeddings = HuggingFaceEmbeddings(
                            model_name=EMBEDDER, 
                            model_kwargs={'device': 'cuda'}
                        )
        # load shastra_gyaan
        self.load_shastra_gyaan()
    
    def research_answerer(self):
    
        research_qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever= self.db.as_retriever(search_kwargs=SEARCH_KWARGS),
            return_source_documents=True,
            verbose=True,
            chain_type_kwargs={"prompt": self.prompt_template}
        )
        return research_qa_chain

    def get_content_from_books(self):
        loader = PyPDFDirectoryLoader(self.books_folder)
        books = loader.load()
        return books
    
    def get_document_embeddings(self, shashtra_gyaan):
        if self.db:
            return self.db
        docs = self.text_splitter.split_documents(shashtra_gyaan)
        self.db = Weaviate.from_documents(docs, self.hfembeddings, client=self.client, by_text=False)
        return self.db

    def load_shastra_gyaan(self):
        shashtra_gyaan = self.get_content_from_books()
        self.get_document_embeddings(shashtra_gyaan)

    def get_jawab(self, vatsa_query):
        bot = self.research_answerer()
        research_out = bot({ "query":  vatsa_query })
        return research_out["result"]

    def research(self, vatsa_query):
        answer = self.get_jawab(vatsa_query)
        return answer

# if __name__ == "__main__":
#     vatsa_query = input("Kya Problem hai Vatsa?")
#     life_guru = LifeGuru()
#     life_guru.research(vatsa_query)