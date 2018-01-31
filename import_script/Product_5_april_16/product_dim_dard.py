#!/usr/bin/env python
# coding: utf-8
import xmlrpclib
import xlrd

dbname =  'dard_import_new'
username =  'admin'
pwd = 'admin'
#sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')
#sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

sock_common = xmlrpclib.ServerProxy ('https://dardbma071501.officebrain.com/xmlrpc/common')
sock = xmlrpclib.ServerProxy('https://dardbma071501.officebrain.com/xmlrpc/object')

uid = sock_common.login(dbname, username, pwd)

#Product Attribute
product_attribute = [{'name': 'Color'},
{'name': 'Size'},
]

for prod_attribute in product_attribute:
    attribute_id = sock.execute(dbname, uid, pwd, 'product.attribute', 'search', [('name', '=', prod_attribute.get('name',''))])
    if not attribute_id:
        sock.execute(dbname, uid, pwd, 'product.attribute', 'create', prod_attribute)

print "Product Attributes created! :)"

#Color

colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

color_attribute_id = sock.execute(dbname, uid, pwd, 'product.attribute', 'search', [('name', '=', 'Color')])

if color_attribute_id:
    for color in colors:
        color_option_id = sock.execute(dbname, uid, pwd, 'product.attribute.value', 'search', [('name', '=', color.title()), ('attribute_id', '=', color_attribute_id[0])])
        if not color_option_id:
            color_option_id = sock.execute(dbname, uid, pwd, 'product.attribute.value', 'create', {'name': color.title(), 'attribute_id': color_attribute_id[0]})
            


print "Color Attribute Values created! :)"


#size

size = ['W 3 1/8 In X H 1 7/8 In', 'W 2 1/2 In X H 1 13/16 In', 'W 2 3/8 In X H 2 In', 'W 5/8 In X L 5 1/4 In', 'W 2" X H 1 3/8"', 'W 4 1/2" X H 2 1/8"', 'W 5 In X H 5 1/8 In X D 4 1/4 In', 'W 1 3/8 In X H 2 3/4 In', 'W 1 1/4" X L 9 1/2"', 'W 9/16 In X L 5 1/2 In', 'W 3/4" X L 5 3/8"', 'W 7/8 In X L 7 3/4 In', 'W 1/2 In X H 5 1/2 In', 'W 3 3/16 In X H 1 In', '1 1/2 In Dia', 'W 9/16" X H 5 1/2"', 'W 3/8" X L 5 1/2"', 'W 3/4 In X L 5 1/4 In', 'W 1/2 In X L 5 3/4 In', 'W 47 In X H 53 In', 'W 5/8 In X L 5 1/3 In', 'W 5/8 In X L 5 3/8 In', 'W 1/2 In X L 5 1/4 In', 'W 50 In X   L 60 In', 'W 1 1/2 In X H 3 In', 'W 3 1/2 In X H 1 3/4 In X D 1 1/8 In', 'W 5 1/2" X H 5/8"', 'W 3/4 In X L 5 3/4 In', 'W 3 1/4" X H 5"', 'W 1 3/4 In X H 1 In', 'W 1 5/8 In X H 1 1/4 In', 'W 1 1/2 In X H 1 1/2 In', '3 5/8 In X H 6 3/4 In', 'W 5/16" X H 1 1/8"', 'W 5/8 In X L 4 9/16 In', 'W 2 In X H 1 5/8 In', 'W 1 13/16 In X H 2 9/16 In', 'W 7/8 In X H 5 1/4 In', 'W 3 1/2" X H 7 1/2"', 'W 3 1/2 X H 4"', 'W 5/8" X H 3 1/8"', 'W 1/4" Oval', 'W 1 3/16 In X H 1 3/16 In X L 1 3/16 In', 'W 2 7/8 In X H 3 1/8 In', 'W 1 3/8" X H 1 5/8"', 'W 13/16" X H 15/16"', 'W 3 5/8 In X H 1 In', 'W 2 7/8 In X H 8 3/4 In', '1 7/8 In Diameter', 'W 1 1/2 In X H 2 1/4 In X L 5 1/4 In', 'W 5/8" X H 1 1/4"', 'W 3 1/8" X H 4 3/16"', '2 1/2 In Dia', 'W 9/16 In X L 5 9/16 In', 'W 4 3/8 In X H 3 1/2 In', 'Closed: W 2 1/2 In X H 4 3/4 In  Open Depth: 3 1/2 In', 'W 2 3/8 In X H 15/16 In', 'W 3 7/8 In X H 3 7/8 In', 'W 1 3/4 In X H 3 7/8 In', 'W 2 In X H 1 3/8 In', 'W 4 1/4 In X H 5 7/8 In', 'W 2 1/8 In X H 3 1/4 X D 3/8', 'W 3 1/2 In X H 2 3/8 In', 'W 3/8 In X L 5 1/2 In', 'W 5 1/16 In X H 1 3/16 In X L 5 15/16 In', '3 3/8 In Dia X H 3 7/16 In', '1 1/4 In Dia X L 3 1/4 In', 'H 4 In X 13/8 In Diameter', 'W 2 3/4 In X H 2 3/4 In', 'W 2 7/8 In X H 2 1/2 In', 'W 3 1/2 X H 2 1/2', 'L 14 7/8 In X W 1 3/4 In', 'W 9/16 In X L 5 716 In', 'W 2 In X H 1 1/2 In', 'W 2 1/4 In X H 1 3/8 In', 'W 3/4 In X L 3 1/8 In', 'W 2 1/4 In X H 3/4 In', 'W 2 3/8" X H 1 5/8"', 'W 1 5/8 In X H 2 3/8 In', 'W 3 1/4 In X H 6 In', 'Unfolded: W 7 3/4 In X H 4 3/4 In X L 12 In', 'W 1 3/8 In X H 6 In', 'W 1 5/8" X H 2 3/8"', 'W 5 1/2" X H 1/2"', 'W 8 5/8 In X H 5 7/8 In', 'W 5 1/2 In X H 3 1/2 In', 'W 5 3/4" X H 3"', '3 Diameter', 'W 1 9/16" X H 4 3/8"', 'W 2 1/8" X H 3 1/2"', 'W 5/8 In X L 5 9/16 In', 'W 11/16 In X H 5 5/8 In', 'W 3/4 In X H 3 In', 'W 9 In X H 4 1/2 In', 'W 3 In X H 13/16 In', 'W 3 3/8 In X H 2 1/16 In', 'W 5 1/2 In X H 5 1/2 In X D 3 3/4 In', '1 3/8 In Dia', 'W 10 1/4 In X H 12 3/4 In', 'W 2 1/8" X H 6"', 'W 2 5/8 In X H 3 In', 'L 5 3/16 In X W 2 9/32 In', 'W 1/2 In X L 5 1/2 In', 'W 4 5/8 In X H 3 1/4 In', 'W 3/4 In X L 5 9/16 In', 'W 3 1/2 In X H 1 1/8 In', 'W 3 1/8" X H 2 1/2"', 'W 8 1/2 In X H 12 In', 'W 2 9/16 In X H 5 1/8 In', 'W 1 7/16 In X H 3 1/4 In X D 13/16 In', 'W 3 1/4 In X H 1 7/8 In', 'W 3 1/8" X H 4 1/8"', 'W 6 1/4 In X H 1 3/4 In', '2 In Dia', 'W 11/16 In X L 415/16 In', 'W 11/16 In X L 4 15/16 In', 'N/A', 'W 2 15/16 In X H 9 5/8 In', 'W 1 7/8 In X H 1 9/16 In', 'W 2 7/8 In X H 3 3/4 In', 'W 2 1/2 In X H 1 1/2 In', 'W 2 1/8 In X H 2 3/6 In', 'Up To 10" Diameter', 'W 3in X H 1 3/4 In', 'W 2 In X H 2 3/16 In', 'W 2 13/16 X X H 4 3/16 In', 'W 1 3/4 In X H 1 3/4 In', '3 1/2 In Diameter', 'W 3 3/4 In X H 2 1/4 In', 'W 3 1/2 In X H 1 3/4 In', 'W 3 1/4" X H 1 1/2"', 'W 2 9/16 In X H 1 9/16 In', 'W 1 3/16 In X H 2 7/8 In', 'W 8 13/16 In X H 6 1/2 In X D 2 13/16 In', 'W 2 1/4 In X H 1 5/8 In', 'L 3 3/16 In X W 1 In X D 3/8 In', 'W 1 1/4 In X H 1 7/16 In', 'W 5 1/2 In X H 4 1/8 In', '6 5/8 In Diam X H 10 1/2 In', 'W 2 3/8 In X H 1 9/16 In X D 1/2 In', 'W 1 7/8 In X H 1 7/8 In X D 1 In', 'W 3 7/8 In X H 4 5/8 In', 'W 5 7/8 In X H 7 In', 'W 4 1/8 In X H 4 1/8 In', 'W 11/16 In X L 5 7/16 In', 'W 6 In X H 3 7/8 In', 'W 2 In X H 3 1/4 In', 'W 1 1/4 In X 4 1/4 In', 'W 3 1/4 In X H 2 1/8 In', 'W 6 3/4" X H 3 7/8"', 'W 3/4 In X L 5 5/8 In', 'W 4 1/8 In X H 15/16 In', 'W 2 5/16 X H 4 1/4', 'W 3 5/16 In X H 2 1/8 In', 'W 2 1/2 In X H 2 3/4 In', 'W 1 7/8 In X H 4 1/2 In', 'W 3 7/8 In X H 2 1/2 In', 'W 2 9/16 In X H 6 15/16 In', 'W 2 7/8 In X L 2 9/16 In', 'W 2 1/2 In X H 7 3/8 In', 'W 2 1/2 In X H 1 In', 'W 2 3/4 In X H 2 In', 'W 3 1/2 In X H 7 3/4 In', '2" Diam X H 1 1/2"', '2 3/16" Diam', 'W 4 In X H 2 3/4 In', 'W 3 3/8 In Dia X L 3 In', 'W 7 1/4 In X H 5 In', 'W 1/2 In X H 5 5/16 In', 'W 2 In X H 1/2 In', 'W 9/16 In X L 5 1/4 In', 'W 2 1/4 In X H 2 3/4 In', 'W 3 5/8" X H 5 1/4"', 'W 3 In X H 2 5/8 In', 'W 9/16 In X L 5 5/8 In', 'W 3 In X H 2 In', 'W 11/16 In X L 5 1/4 In', 'W 9/16 X L 5 11/16', 'W 3 3/8 In X H 5 3/16 In X D 7/16 In', 'W 2 1/2 In X H 3 In', 'W 3 7/8 In X H 2 1/4 In', 'W 4 7/8" X H 2 1/2"', 'W 2 1/2 X H 3 1/2 In', 'W 2 7/8 In X H 4 In', 'W 3 3/4 In X H 2 1/2 In', 'H 4 7/16 In X 2 In Dia.', 'W 8" X H 4"', 'W 4 In X H 1 3/4 In', 'W3 3/4 In X H 2 1/4 In', 'W 4 3/4 In X H 4 1/2 In X L 6 1/2 In', 'W 2 3/8 In X H 5 5/16 In', 'W 2 1/16 X H 4 1/8 In', 'W 1 3/8" X H 2 3/4"', 'L 5 7/8 In X W 1 11/16 In X H 1 7/32', 'W 4 1/8" X H 9 3/4"', 'W 3 1/2 In X H 7 1/2 In', '2 3/8 In Dia X H 10 9/16 In', 'W 3/8 In X L 3 1/2 In (Length With Rings)', 'W 3/8" X L 3 1/2"', 'W 60 In X H 72 In', 'W 2 7/8 In X H 4 7/16 In', 'W 3/4" X H 1 3/8"', 'W 3 1/2 In X H 5 1/2 In', 'W 13/16" X L 20"', 'W 1" X H 3"', 'L 6 3/5 In X H 1 1/4 In', 'W 47 In X L 53 In', 'W 1" X H 1 3/8"', '5 5/16 X 5/8 W', '5 1/4 H X 5/8 W', '5 1/2 H X 5/8 W', '5 9/16 H X 9/16 W', '5 1/2 H X 9/16 W', '5 3/16 H X 5/8 W', '5 9/16 H  5/8 W', 'W 9/16" X L 5 9/16"', 'W 5/8" X L 5 3/16"', 'W 1/2" X L 5 1/2"', 'W 5/8" X L 5 9/16"', 'W 5/8" X L 5 1/2"', 'W 9/16" X L 5 1/2"', '5 11/16 H X 1/2 W', '5 5/6 Hx 11/16 W', '5 1/8 H X 11/16 W', 'W 5/8 In X L 5 1/2 In', 'W 5 1/2 In X H 8 In', 'W 5 5/8 X H 6 1/4', 'W 3 3/4" X L 3 3/4" X H 3 3/4"', 'L 6 5/8" X H 1 5/8"', '1 7/8 Diameter', 'W 1 3/4 X H 1 3/4', 'W 3/8 X H 3 9/16', 'W 13/16" X H 15/16" X L 1 1/4"', '3  3/4 L 1 1/4 W', '2 3/8 H X 3 W', '7/8 H X 3 1/2 W', '7/8 H X 3 3/4 W', 'L 7/8" X W 7/8" X H 3 3/4"', '3 5/8 H X 7/8 Dia', 'L 4 1/2" X W 2" X H 3/8"', '4 1/4 W X 1 3/4 H', 'L 4 1/2" X W 2 1/2" X H 3/8"', 'L 4 7/8" X W 2 7/8" X H 5/8"', 'L 3 3/4" X W 1 3/4" X H 7/8"', 'L 4 3/4" X W 1 5/8" X H 7/8"', 'L 2 3/4" X W 1 3/8" X H 7/8"', 'L 2 5/8" X W 1 1/8" X H3/4"', 'L 7/8" X W 3/8" X H 7/32"', 'L 1 5/8" X W 1 1/4" X H 1"', 'L 4 1/2" X W 1 3/16" X H 1 1/2"', 'L 2" X W 1" X H 5/8"', 'L 4 7/8" X W 1 3/16" X H 1 3/16"', 'L 6" X W 2 15/16" X H 3/8"', 'W 2 1/8" X H 3 3/4"', 'W 2 1/2" X H 4 5/8"', 'W 2 1/4" X H 3 3/4"', 'L 1 3/16" X W 1" X H 3/16"', 'W 31/32" X H 25/32"', 'L 6 1/2" X W 3 1/2"X H 4"', 'W 3 3/4" X H 8 1/2"', 'W 7" X H 5 1/4"', 'W 3" X H 6 1/2"', 'W 7" X H 6"', 'W 17" X H 7"', 'W 3" X H 2 3/4"', 'W 3 1/2" X H 2 1/16"', 'L 3 3/4" W 1 1/4" X D 1 1/16"', 'W 2" X H 1"', 'W 2" H 1 9/16"', 'W 4" X H 1 1/4"', 'W 6" X H 8 1/2"', 'L 3 3/4" X 1" Diameter', 'W 3" X H 2 1/8"', 'W 3 1/4" Diameter X H 2"', 'W 14 In X H 18 In X D 2 In', 'W 14 In X H 18 In', 'W 15 In X H 16 In', 'W 10 1/2 In X H 14 In X D 5 In', 'W 15 X H 16', 'W 20 In X H 15 In X D 5 In', 'W 18 In X H 14 In X D 4 1/2 In', 'W 14 In X H 12 In X D 5 1/2 In', 'W 17 In X H 13 In X D 5 In', 'W 18 1/2 In X H 12 In X D 5 1/2 In', 'W 22 In X H 16 In X D 6 In', 'W 50" X H 60"', 'H 9 3/8 In X W 3 In Diam', 'H 6 1/2 In X 3 1/8 In', 'W 3" Diameter X H 9 7/16"', '3 1/2" Diameter X H 9 3/8"', 'W 3" Diameter X H 9 3/8"', 'W 2 1/2" Diameter X H 8 1/8"', '3 1/2" Diameter X H 8 7/8"', 'W 4" Diameter X H 8"', 'W 2 1/2" Diameter X H 8 1/4"', 'H 8 7/8 In X 3 1/2 In Diam', 'W 3 3/4" X H 7 13/16"', 'W 3 1/8" X H 8 3/4"', 'W 3 1/4" X H 8 1/4"', 'W 2 3/4" X H 8 5/8"', '7/8" Diameter', 'W 1/8" X L 4 1/16"', '1 1/8" Diameter', 'W 1 1/8" X L 1 3/4"', 'W 3/16" X L 4 1/4"', 'W 3/16" X L 4 1/16"', '1" Diameter', 'W 1/2" Diam X H 1 15/16"', 'W 3/8 " Diam X H 1 3/4"', 'W 1 5/16" X L 2 3/8"', '3/16" Diam X H 9/32"', 'W 3/8" X L 6 1/4"', 'W 1/2" X L 5 1/8"', 'W 1 3/8" X H 6 1/8" Flat', 'W 1/2" X L 7 1/4"', 'W 1/2" X H 1/2"']

size_attribute_id = sock.execute(dbname, uid, pwd, 'product.attribute', 'search', [('name', '=', 'Size')])

if size_attribute_id:
    for s in size:
        size_option_id = sock.execute(dbname, uid, pwd, 'product.attribute.value', 'search', [('name', '=', s), ('attribute_id', '=', size_attribute_id[0])])
        if not size_option_id:
            size_option_id = sock.execute(dbname, uid, pwd, 'product.attribute.value', 'create', {'name': s, 'attribute_id': size_attribute_id[0]})

print "Size Attribute Values created! :)"


#Dimension Types
#Removed sequence, mandatory_dimension and Added dimension_type
dimension_types = [{'name': 'Silk Screen', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'Silk Screen Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   {'name': 'Pad Print', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'Pad Print Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   {'name': 'Embroidery', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'Embroidery Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   {'name': 'Digital Laserjet', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'Digital Laserjet Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   {'name': 'Hot Stamp', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'Hot Stamp Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   {'name': 'Laser Engrave', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'Laser Engrave Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   {'name': 'DigiSplash Doming', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'DigiSplash Doming Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   {'name': 'Four Color Process', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'Four Color Process Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   {'name': 'Heat Transfer', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'Heat Transfer Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   {'name': 'X2 Digital UV Inkjet', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'X2 Digital UV Inkjet Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   {'name': 'Four Color Process DyeSub', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'Four Color Process DyeSub Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   {'name': 'Four Color Process Dome', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'Four Color Process Dome Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   
                   {'name': 'Four Color Process Label', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'Four Color Process Label Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   
                   {'name': 'DO', 'description':'', 'dimension_type': False, 'attribute_field_type': 'none'},
                   {'name': 'DO Imprint Color', 'description':'', 'dimension_type': 'color', 'attribute_field_type': 'multiselection'},
                   
                   {'name': 'Imprint Position', 'description':'', 'dimension_type': 'side', 'attribute_field_type': 'multiselection'},
                  ]

for dimension_type in dimension_types:
    dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', dimension_type.get('name', ''))])
    if not dimension_id:
        dimension_vals = {
            'name': dimension_type.get('name', ''),
            'description': dimension_type.get('description', ''),
            'dimension_type': dimension_type.get('dimension_type', False),
            'attribute_field_type': dimension_type.get('attribute_field_type', False),
        }
        if dimension_type.get('attribute_field_type', False):
            dimension_vals.update({'attribute_field_type': dimension_type.get('attribute_field_type')})
        dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'create', dimension_vals)
print "Dimension types created! :)"


#Dimension Options

#Silk Screen Colors

silk_screen_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

silk_screen_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'Silk Screen Imprint Color')])

if silk_screen_dimension_id:
    for silk_screen_color in silk_screen_colors:
        silk_screen_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', silk_screen_color.title()), ('dimension_id', '=', silk_screen_dimension_id[0])])
        if not silk_screen_color_option_id:
            silk_screen_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': silk_screen_color.title(), 'dimension_id': silk_screen_dimension_id[0]})

print "silk screen Color Dimension Options created! :)"

#Pad Print

pad_print_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

pad_print_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'Pad Print Imprint Color')])

if pad_print_dimension_id:
    for pad_print_color in pad_print_colors:
        pad_print_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', pad_print_color.title()), ('dimension_id', '=', pad_print_dimension_id[0])])
        if not pad_print_color_option_id:
            pad_print_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': pad_print_color.title(), 'dimension_id': pad_print_dimension_id[0]})

print "Pad Print Dimension Options created! :)"

#Embroidery Colors

embroidery_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

embroidery_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'Embroidery Imprint Color')])

if embroidery_dimension_id:
    for embroidery_color in embroidery_colors:
        embroidery_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', embroidery_color.title()), ('dimension_id', '=', embroidery_dimension_id[0])])
        if not embroidery_color_option_id:
            embroidery_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': embroidery_color.title(), 'dimension_id': embroidery_dimension_id[0]})

print "Embroidery Color Dimension Options created! :)"

#Digital Laserjet Colors

digital_laserjet_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

digital_laserjet_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'Digital Laserjet Imprint Color')])

if digital_laserjet_dimension_id:
    for digital_laserjet_color in digital_laserjet_colors:
        digital_laserjet_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', digital_laserjet_color.title()), ('dimension_id', '=', digital_laserjet_dimension_id[0])])
        if not digital_laserjet_color_option_id:
            digital_laserjet_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': digital_laserjet_color.title(), 'dimension_id': digital_laserjet_dimension_id[0]})

print "digital laserjet Color Dimension Options created! :)"

#Hot Stamp

hot_stamp_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

hot_stamp_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'Hot Stamp Imprint Color')])

if hot_stamp_dimension_id:
    for hot_stamp_color in hot_stamp_colors:
        hot_stamp_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', hot_stamp_color.title()), ('dimension_id', '=', hot_stamp_dimension_id[0])])
        if not hot_stamp_color_option_id:
            hot_stamp_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': hot_stamp_color.title(), 'dimension_id': hot_stamp_dimension_id[0]})

print "hot stamp Dimension Options created! :)"

#Laser Engrave

laser_engrave_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

laser_engrave_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'Laser Engrave Imprint Color')])

if laser_engrave_dimension_id:
    for laser_engrave_color in laser_engrave_colors:
        laser_engrave_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', laser_engrave_color.title()), ('dimension_id', '=', laser_engrave_dimension_id[0])])
        if not laser_engrave_color_option_id:
            laser_engrave_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': laser_engrave_color.title(), 'dimension_id': laser_engrave_dimension_id[0]})

print "laser engrave Dimension Options created! :)"

#DigiSplash Doming

digisplash_doming_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

digisplash_doming_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'DigiSplash Doming Imprint Color')])

if digisplash_doming_dimension_id:
    for digisplash_doming_color in digisplash_doming_colors:
        digisplash_doming_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', digisplash_doming_color.title()), ('dimension_id', '=', digisplash_doming_dimension_id[0])])
        if not digisplash_doming_color_option_id:
            digisplash_doming_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': digisplash_doming_color.title(), 'dimension_id': digisplash_doming_dimension_id[0]})

print "digisplash doming Dimension Options created! :)"

#4 Color Process

four_color_process_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

four_color_process_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'Four Color Process Imprint Color')])

if four_color_process_dimension_id:
    for four_color_process_color in four_color_process_colors:
        four_color_process_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', four_color_process_color.title()), ('dimension_id', '=', four_color_process_dimension_id[0])])
        if not four_color_process_color_option_id:
            four_color_process_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': four_color_process_color.title(), 'dimension_id': four_color_process_dimension_id[0]})

print "Four color process Dimension Options created! :)"

#Heat Transfer

heat_transfer_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

heat_transfer_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'Heat Transfer Imprint Color')])

if heat_transfer_dimension_id:
    for heat_transfer_color in heat_transfer_colors:
        heat_transfer_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', heat_transfer_color.title()), ('dimension_id', '=', heat_transfer_dimension_id[0])])
        if not heat_transfer_color_option_id:
            heat_transfer_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': heat_transfer_color.title(), 'dimension_id': heat_transfer_dimension_id[0]})

print "heat transfer Dimension Options created! :)"

#X2 Digital UV Inkjetfour Color Process Dome Imprint Color

x2_digital_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

x2_digital_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'X2 Digital UV Inkjet Imprint Color')])

if x2_digital_dimension_id:
    for x2_digital_color in x2_digital_colors:
        x2_digital_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', x2_digital_color.title()), ('dimension_id', '=', x2_digital_dimension_id[0])])
        if not x2_digital_color_option_id:
            x2_digital_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': x2_digital_color.title(), 'dimension_id': x2_digital_dimension_id[0]})

print "x2 digital Dimension Options created! :)"

#four Color Process DyeSub

four_pro_dyesub_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

four_pro_dyesub_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'Four Color Process DyeSub Imprint Color')])

if four_pro_dyesub_dimension_id:
    for four_pro_dyesub_color in four_pro_dyesub_colors:
        four_pro_dyesub_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', four_pro_dyesub_color.title()), ('dimension_id', '=', four_pro_dyesub_dimension_id[0])])
        if not four_pro_dyesub_color_option_id:
            four_pro_dyesub_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': four_pro_dyesub_color.title(), 'dimension_id': four_pro_dyesub_dimension_id[0]})

print "Four pro dyesub Dimension Options created! :)"

#four Color Process Dome

four_pro_dome_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

four_pro_dome_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'Four Color Process Dome Imprint Color')])

if four_pro_dome_dimension_id:
    for four_pro_dome_color in four_pro_dome_colors:
        four_pro_dome_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', four_pro_dome_color.title()), ('dimension_id', '=', four_pro_dome_dimension_id[0])])
        if not four_pro_dome_color_option_id:
            four_pro_dome_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': four_pro_dome_color.title(), 'dimension_id': four_pro_dome_dimension_id[0]})

print "Four pro dome Dimension Options created! :)"


##############
#Four Color Process Label Colors

four_color_process_label_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

four_color_process_label_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'Four Color Process Label Imprint Color')])

if four_color_process_label_dimension_id:
    for four_color_process_label_color in four_color_process_label_colors:
        four_color_process_label_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', four_color_process_label_color.title()), ('dimension_id', '=', four_color_process_label_dimension_id[0])])
        if not four_color_process_label_color_option_id:
            four_color_process_label_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': four_color_process_label_color.title(), 'dimension_id': four_color_process_label_dimension_id[0]})

print "Four Color Process Label Color Dimension Options created! :)"

#DO Colors

do_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

do_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'DO Imprint Color')])

if do_dimension_id:
    for do_color in do_colors:
        do_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', do_color.title()), ('dimension_id', '=', do_dimension_id[0])])
        if not do_color_option_id:
            do_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': do_color.title(), 'dimension_id': do_dimension_id[0]})

print "DO Color Dimension Options created! :)"

#SS Colors

ss_colors = ['Trans Blue', 'Trans Red', 'White', 'Chrome', 'Trans Amber', 'Silver', 'Clear', 'Blue', 'Light Green', 'Yellow', 'Red', 'Black', 'Trans Green', 'Green', 'Metallic Blue', 'Metallic Green', 'Metallic Red', 'Trans Orange', 'Trans Teal', 'Trans Yellow', 'Burgundy', 'Metallic Silver', 'Glow In Dark', 'Neon Green', 'Neon Orange', 'Neon Pink', 'Neon Yellow', 'Pink', 'Orange', 'Red White Blue', 'Mix Colors', 'Purple', 'Aqua Blue', 'Brown', 'Lime', 'Teal', 'Blue Green', 'Metallic Purple', 'Smoke', 'Trans Pink', 'Dark Green', 'Granite', 'Neon Red', 'Trans Purple', 'Frost Blue', 'Frost Green', 'Frost Purple', 'Frost Red', 'White/Blue', 'Cream', 'Green Yellow', 'Silver Black', 'Silver Blue', 'Gold', 'Camel', 'Light Grey', 'Navy Blue', 'Natural', 'Cocoa', 'Charcoal', 'Forest Green', 'Heather Grey', 'Royal Blue', 'Taxi Yellow', 'Grey', 'Sage', 'Black Watch', 'Red Buffalo', 'Metallic Yellow', 'Gun Metal', 'Trans Magenta', 'Light Blue', 'Trans Clear', 'Maroon', 'Navy', 'Turquoise', 'Forest', 'Gray', 'Trans Smoke', 'Varies']

ss_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'SS Imprint Color')])

if ss_dimension_id:
    for ss_color in ss_colors:
        ss_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', ss_color.title()), ('dimension_id', '=', ss_dimension_id[0])])
        if not ss_color_option_id:
            ss_color_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': ss_color.title(), 'dimension_id': ss_dimension_id[0]})

print "SS Color Dimension Options created! :)"
######################

#Imprint Positions

imprint_positions = ['On Front', 'On Top', 'Barrel', 'Front', 'Long Side', 'On Lid', 'Back Side', 'Below Clip', 'Right Side Below Clip', 'Top', 'Side', 'On Barrel', 'Bottom Front', 'N/A', 'Left Side', 'On Right Side', 'Wrap Around', 'Bottom', 'Top Right Of Clip', 'Front & Back', 'On Shelf', 'Top Ring By Handle', 'Front Handle', 'Right Side Of Clip', 'Right Or Left Side', 'Right Side', 'On Bill', 'On Front Above Grip', 'Base', 'Right Or Left Door', 'On Right On Surface', 'Front On White Board', 'Front Below Pedometer', 'Top Lid', 'Outside Cover', 'On Light', 'On Side', 'Front Bottom', 'Top Flap', 'Below Clock', 'Hood', 'Right Front', 'On Base', 'Back', 'Front Of Cereal Bowl', 'On Clip', 'Embroider Lower Right/Left Corner Or Bottom Center', 'Handle', 'Center Barrel', 'Above Clip', 'Print On All 4 Sides', 'Front Of Bag', 'Top Front', 'On Left Side', 'On Back', 'Front,Back', 'Back Handle', 'Top Of Whistle', 'Left Or Right Side', 'On Cork Board', 'Top Of Light', 'Below Display', 'On Clip 4 Color Process', 'Four Color Process On Clip', 'On Pen', 'Back Of Bag', 'Top Back']

imprint_dimension_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.type', 'search', [('name', '=', 'Imprint Position')])

if imprint_dimension_id:
    for imprint_position in imprint_positions:
        imprint_position_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'search', [('name', '=', imprint_position.title()), ('dimension_id', '=', imprint_dimension_id[0])])
        if not imprint_position_option_id:
            imprint_position_option_id = sock.execute(dbname, uid, pwd, 'product.variant.dimension.option', 'create', {'name': imprint_position.title(), 'dimension_id': imprint_dimension_id[0]})

print "Imprint positions created! :)"

