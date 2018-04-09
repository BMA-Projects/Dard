# -*- coding: utf-8 -*-

{
    'name': 'Ob Sale Artwork Extend',
    'category': '',
    'summary': '',
    'version': '1.0',
    'description': """
Provides ability to forecast the quantity for the products and based upon the calculation of action quantity, Purchase Order or Manufacture order can be created.

    """,
    'author': 'OfficeBrain',
    'depends': ['ob_sale_artwork'],
    'data': [
        'ob_artwork_extend_view.xml',
        "demo/artwork_type_demo.xml",
        "demo/artwork_shape_demo.xml",
        "demo/artwork_platting_demo.xml",
        "demo/artwork_onloop_demo.xml",
        "demo/artwork_attachment_demo.xml",
        "demo/artwork_2d_3d_demo.xml",
        "security/ir.model.access.csv",

    ],
    'installable': True,
    'auto_install': False,
}
