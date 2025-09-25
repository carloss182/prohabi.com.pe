# VERSION IA DEL CODIGO
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import base64
import os
import tempfile
from odoo.exceptions import ValidationError

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import TokenTextSplitter
from odoo import api, fields, models


class WhatsappChatbotScript(models.Model):
    _inherit = "whatsapp.chatbot.script"

    step_call_type = fields.Selection(selection_add=[("pdf", "Open AI Document")])

    chatbot_document_ids = fields.Many2many('ir.attachment', string="Attach Document")

    @api.onchange('chatbot_document_ids')
    def onchange_chatbot_document(self):
        if self.chatbot_document_ids:
            temp_dir = tempfile.gettempdir()
            
            for document in self.chatbot_document_ids:
                # Crea un archivo temporal único para cada documento
                temp_file_path = os.path.join(temp_dir, document.name)
                
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                
                # Guarda el contenido decodificado del documento
                with open(temp_file_path, 'wb') as temp_file:
                    temp_file.write(base64.b64decode(document.datas))
                
                # Procesa el documento
                self.process_documents(temp_file_path, self.env.company.open_ai_api_key)

    def process_documents(self, file_path, open_ai_api_key):
        if open_ai_api_key:
            os.environ["OPENAI_API_KEY"] = open_ai_api_key
        else:
            raise ValidationError("Please provide OpenAI API key")
        
        embedding_function = OpenAIEmbeddings()
        persist_directory = "chroma"
        
        # Cargar y dividir el documento
        if file_path.split(".")[-1].lower() == "pdf":
            pdf_loader = PyPDFLoader(file_path)
            pages = pdf_loader.load_and_split()
        elif file_path.split(".")[-1].lower() == "txt":
            txt_loader = TextLoader(file_path)
            pages = txt_loader.load()
        else:
            raise ValidationError("Unsupported file type")
        
        # Dividir en fragmentos
        text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=250)
        docs = text_splitter.split_documents(pages)
        
        if os.path.exists(persist_directory):
            db3 = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
            for i in range(0, len(docs), 165):
                batch = docs[i:i + 165]
                db3.add_documents(batch)
        else:
            db3 = Chroma.from_documents(docs, embedding_function, persist_directory=persist_directory)
        
        # Retornar el directorio persistente
        return persist_directory

#VERSION ORIGINAL DEL CODIGO
# # Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# import base64
# import os
# import tempfile
# from odoo.exceptions import ValidationError

# from langchain_chroma import Chroma
# from langchain_community.document_loaders import PyPDFLoader, TextLoader
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_text_splitters import TokenTextSplitter
# from odoo import api, fields, models
# from odoo.exceptions import UserError


# class WhatsappChatbotScript(models.Model):
#     _inherit = "whatsapp.chatbot.script"

#     step_call_type = fields.Selection(selection_add=[("pdf", "Open AI Document"),])

#     chatbot_document_ids = fields.Many2many('ir.attachment', string="Attach Document")

#     @api.onchange('chatbot_document_ids')
#     def onchange_chatbot_document(self):
#         if self.chatbot_document_ids:
#             temp_dir = tempfile.gettempdir()
#             temp_file_path = os.path.join(temp_dir, self.chatbot_document_ids.name)
#             if os.path.exists(temp_file_path):
#                 os.remove(temp_file_path)
#             with open(temp_file_path, 'wb') as temp_file:
#                 temp_file.write(base64.b64decode(self.chatbot_document_ids.datas))
#             result = self.process_documents(temp_file_path,self.env.company.open_ai_api_key)

#     def process_documents(self, file_path,open_ai_api_key):
#         if open_ai_api_key:
#             os.environ["OPENAI_API_KEY"] = open_ai_api_key
#         else:
#             raise ValidationError("Please provide OpenAI API key")
#         embedding_function = OpenAIEmbeddings()
#         persist_directory = "chroma"
#         if file_path.split(".")[-1].lower() == "pdf":
#             pdf_loader = PyPDFLoader(file_path)
#             pages = pdf_loader.load_and_split()
#         elif file_path.split(".")[-1].lower() == "txt":
#             txt_loader = TextLoader(file_path)
#             pages = txt_loader.load()
#         else:
#             raise ValueError("Unsupported file type")
#         # Split documents into chunks
#         text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=250)
#         docs = text_splitter.split_documents(pages)
#         if os.path.exists(persist_directory):
#             db3 = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
#             b = []
#             for i in range(0, len(docs), 165):
#                 c = []
#                 for j in range(i, i + 165):
#                     if j < len(docs):
#                         c.append(docs[j])
#                     else:
#                         break
#                 b.append(c)
#             for batch in b:
#                 db3.add_documents(batch)
#         else:
#             db3 = Chroma.from_documents(docs, embedding_function, persist_directory=persist_directory)
#         # Perform similarity search
#         return persist_directory