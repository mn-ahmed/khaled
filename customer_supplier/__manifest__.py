# -*- coding: utf-8 -*-

{
    "name": "Customer supplier for sales and purcahse`",
    "author": "Ali Elgarhi",
    "website": "bbi-consulting.com",
    "license": "OPL-1",
    
    "category": "Sales",
    "summary": """
Customer supplier for sales and purcahse
""",
    "description": """
Customer supplier for sales and purcahse
""",
    "depends": ["sale_management","purchase","contacts"],
    "data": [
       
        "views/customer_supplier.xml",
        "views/customer_sales.xml",
        "views/customer_purchase.xml",
    ],
    "images": ["static/description/background.png", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    	
}
