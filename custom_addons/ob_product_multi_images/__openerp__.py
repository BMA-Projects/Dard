{
    'name' : 'Product Multi Images Office Brain',
    'version' : '1.0',
    'author' : 'OfficeBrain',
    'category' : 'Product',
    'description' : """
Product Multiple Images Management
====================================
It will manages multiple images for the particular product.
    """,
    'depends' : ['product','sale'],
    'data': [
        'views/ob_product_multi_images.xml',
        'product_view.xml',
    ],
    'qweb': [
        'static/src/xml/image_multi.xml',
    ],
    'images' : ['static/src/img/download.png','static/src/img/closelabel.gif','static/src/img/pdf_icon.png'],
    'installable': True,
    'auto_install': False,
}