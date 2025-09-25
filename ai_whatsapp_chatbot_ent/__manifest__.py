{
    "name": "AI WhatsApp Chatbot Enterprise Odoo | Open AI | RAG AI | Official WhatsApp Cloud API by Meta | Odoo V17 Enterprise Edition",
    'version': '17.0',
    "author": "TechUltra Solutions Private Limited",
    "category": "Discuss",
    "company": "TechUltra Solutions Private Limited",
    'live_test_url': 'https://www.youtube.com/watch?v=BbxNJGIe9go',
    'website': 'www.techultrasolutions.com',
    'price': 99,
    'currency': 'USD',
    'summary': """Meta Whatsapp chat all in one integrated with the sale purchase accounting discuss modules. all in one whatsapp can help you to take the advantage of the whatsapp communication in current market
        Odoo WhatsApp Integration
        Odoo Meta WhatsApp Graph API
        Odoo V17 Enterprise Edition
        Enterprise WhatsApp
        Enterprise
        WhatsApp Enterprise
        Odoo WhatsApp Enterprise
        Odoo WhatsApp Cloud API
        WhatsApp Cloud API
        WhatsApp Enterprise Edition,
        AI WhatsApp Chatbot, OpenAI, RAG AI, Official WhatsApp Cloud API, Meta, Odoo V17, Odoo Enterprise Edition, AI Integration, 
        Document Processing, Automated Responses, Customer Support, WhatsApp Business API, NLP, GPT-4, GPT-3.5, GPT-3.5 Turbo,
        Custom Odoo Module, Intelligent Communication, Retrieval-Augmented Generation, Efficiency, Advanced AI, 
        Seamless Integration, Multi-language Support

    """,
    'description': """
        The WhatsApp Business Platform Cloud API is based on Meta/Facebook's Graph API Which allows medium and large businesses to communicate with their customers at scale. Send and receive whatsapp messages quickly & easily directly from Odoo to WhatsApp and WhatsApp to Odoo.
        Also, this module which allows the user to Create/Edit/Remove/Delete WhatsApp Templates, 
        Showing WhatsApp Chat History, Configure WhatsApp Templates in Particular User via Odoo.
        Odoo WhatsApp Integration
        Odoo Meta WhatsApp Graph API
        Odoo V17 Enterprise Edition
        Odoo V17 Enterprise Edition
        Odoo V17 Enterprise WhatsApp Integration
        V17 Enterprise WhatsApp
        Enterprise WhatsApp
        Enterprise
        WhatsApp Enterprise
        Odoo WhatsApp Enterprise
        Odoo WhatsApp Cloud API
        WhatsApp Cloud API
        WhatsApp Enterprise Edition,
	    AI WhatsApp Chatbot, OpenAI, RAG AI, Official WhatsApp Cloud API, Meta, Odoo V17, Odoo Enterprise Edition, AI Integration, 
        Document Processing, Automated Responses, Customer Support, WhatsApp Business API, NLP, GPT-4, GPT-3.5, GPT-3.5 Turbo,
        Custom Odoo Module, Intelligent Communication, Retrieval-Augmented Generation, Efficiency, Advanced AI, 
        Seamless Integration, Multi-language Support
    """,
    'depends': ["odoo_whatsapp_ent_chatbot"],
    'external_dependencies': {
        'python': ['langchain-community',
                   'langchain-openai ',
                   'openai',
                   'pypdf',
                   'langchain-chroma',
                   'chromadb'
                   ]
    },
    'data': [
        'views/res_config_settings_views.xml',
        'views/whatsapp_chatbot_script_inherit.xml',
    ],
    "images": ["static/description/Banner.gif"],
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "OPL-1",
}
