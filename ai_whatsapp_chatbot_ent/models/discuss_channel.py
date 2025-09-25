# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import json
from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough


class AIDiscussChannel(models.Model):
    _inherit = "discuss.channel"

    def process_rag_chain(self, input_data, persist_directory):
        # Initialize the Chroma vector store
        if self.env.company.open_ai_api_key:
            os.environ["OPENAI_API_KEY"] = self.env.company.open_ai_api_key
        else:
            raise UserError("No OpenAI API key found.")

        db3 = Chroma(persist_directory=persist_directory, embedding_function=OpenAIEmbeddings())
        docs = db3.similarity_search(input_data)
        # Define the prompt template
        template = """
           Use the following pieces of context to provide a detailed answer to the question at the end.
           Act as a traveler agent. Your role is to give guidance on it.
           If user input is a greeting, you should greet.
           {context}
           Question: {question}
           Helpful Answer:
           """
        # Initialize the ChatOpenAI model

        if self.env.company.open_ai_model and self.env.company.open_ai_max_tokens:
            llm = ChatOpenAI(model=self.env.company.open_ai_model, max_tokens=self.env.company.open_ai_max_tokens)
        else:
            raise UserError("No OpenAI model found.")

        # Create a retriever from the Chroma vector store
        retriever = db3.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        # Create the custom prompt template
        custom_rag_prompt = PromptTemplate.from_template(template)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # Create the RAG chain
        rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | custom_rag_prompt
                | llm
                | StrOutputParser()
        )
        # Invoke the chain with the user input
        result = rag_chain.invoke(input_data)
        return result

    def get_response(self, input_data):
        persist_directory = 'chroma'
        return self.process_rag_chain(input_data, persist_directory)

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        res = super(AIDiscussChannel, self)._notify_thread(
            message, msg_vals=msg_vals, **kwargs
        )
        if self.env.context.get('stop_recur'):
            return res
        if message:
            wa_account_id = self.wa_account_id
            user_partner = (
                wa_account_id.notify_user_ids and wa_account_id.notify_user_ids[0] or []
            )
            mail_message_id = message
            partner_id = mail_message_id.author_id
            if wa_account_id and user_partner and wa_account_id.wa_chatbot_id and self:
                message.update({"wa_chatbot_id": wa_account_id.wa_chatbot_id.id})
                if not self.is_chatbot_ended:
                    message_script = (
                        self.env["whatsapp.chatbot"]
                        .search([("id", "=", wa_account_id.wa_chatbot_id.id)])
                        .mapped("step_type_ids")
                        .filtered(
                            lambda l: l.message
                            == tools.html2plaintext(mail_message_id.body)
                            and l.step_call_type == 'pdf'
                        )
                    )

                    current__chat_seq_script = (
                        self.env["whatsapp.chatbot"]
                        .search([("id", "=", wa_account_id.wa_chatbot_id.id)])
                        .mapped("step_type_ids")
                        .filtered(lambda l: l.sequence == self.script_sequence)
                    )
                    if message_script:
                        chatbot_script_lines = message_script
                    elif current__chat_seq_script and current__chat_seq_script.step_call_type != 'action':
                        chatbot_script_lines = current__chat_seq_script
                    else:
                        chatbot_script_lines = wa_account_id.wa_chatbot_id.step_type_ids[0]

                    for chat in chatbot_script_lines:
                        if chat.sequence >= self.script_sequence:
                            self.write(
                                {
                                    "wa_chatbot_id": chat.whatsapp_chatbot_id.id
                                    if wa_account_id.wa_chatbot_id
                                    == chat.whatsapp_chatbot_id
                                    else False,
                                    "script_sequence": chat.sequence,
                                }
                            )
                        elif (
                            current__chat_seq_script
                            and current__chat_seq_script.parent_id
                            and current__chat_seq_script.parent_id == chat.parent_id
                        ):
                            self.write(
                                {
                                    "wa_chatbot_id": chat.whatsapp_chatbot_id.id,
                                    "script_sequence": chat.sequence,
                                }
                            )
                        else:
                            first_script = (
                                self.env["whatsapp.chatbot"]
                                .search([("id", "=", self.wa_chatbot_id.id)])
                                .mapped("step_type_ids")
                                .filtered(lambda l: l.sequence == 1)
                            )
                            if first_script:
                                self.write(
                                    {
                                        "wa_chatbot_id": chat.whatsapp_chatbot_id.id,
                                        "script_sequence": first_script.sequence,
                                    }
                                )
                            else:
                                self.write(
                                    {
                                        "wa_chatbot_id": chat.whatsapp_chatbot_id.id if wa_account_id and wa_account_id.wa_chatbot_id == chat.whatsapp_chatbot_id
                                        else False,
                                        "script_sequence": chat.sequence,
                                    })
                        if chat.step_call_type == "pdf":
                            if chat.chatbot_document_ids:
                                chat_answer = self.get_response(tools.html2plaintext(mail_message_id.body))
                                self.with_context({'stop_recur': True}).with_user(user_partner.id).message_post(
                                    body=chat_answer,
                                    message_type="whatsapp_message",
                                )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self._context.get("wa_chatbot_id"):
                whatsapp_chatbot = self.env["whatsapp.chatbot"].search(
                    [("id", "=", self._context.get("wa_chatbot_id"))]
                )
                if whatsapp_chatbot:
                    vals.update(
                        {
                            "wa_chatbot_id": whatsapp_chatbot.id,
                        }
                    )
        return super(AIDiscussChannel, self).create(vals_list)



