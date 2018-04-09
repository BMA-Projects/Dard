{
    'name' : 'OB Live Support',
    'author': 'OpenERP SA',
    'version': '1.0',
    'summary': 'Chat with the Beacon collaborators',
    'category': 'Tools',
    'complexity': 'medium',
    'website': 'https://www.officebrain.com/',
    'description':
        """
Office Beacon Live Support
=================

Ask your functionnal question directly to the Beacon Operators with the livechat support.

        """,
    'data': [
        "views/im_beacon_support.xml",
        'access_live_support.xml'
    ],

    'depends' : ["web", "im_chat"],
    'qweb': [
        'static/src/xml/im_beacon_support.xml'
    ],    
    'installable': True,
    'auto_install': True,
    'application': True,
}
