{
    'name': 'Historial de WhatsApp en Contactos',
    'version': '1.0',
    'depends': ['base', 'contacts'],
    'author': 'Carlos Berrocal',
    'description': 'Guarda y muestra el historial de WhatsApp de cada contacto.',
    'category': 'Tools',
    'data': [
        'security/ir.model.access.csv',
        'views/whatsapp_message_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
}
