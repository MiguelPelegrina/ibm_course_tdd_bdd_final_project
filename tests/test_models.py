# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_update_a_product(self):
        """It should Update a product from the database"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)
        product.description = "Updated description"
        product.update()
        updated_product = Product.find(product.id)
        self.assertEqual(updated_product.description, "Updated description")

    def test_delete_a_product(self):
        """It should delete a product from the database"""
        product = ProductFactory()
        product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)
        product.delete()
        deleted_product = Product.find(product.id)
        self.assertIsNone(deleted_product)
    
    def test_serialize_a_product(self):
        """It should Serialize a product into a dictionary"""
        product = ProductFactory()
        product.create()
        serialized_product = product.serialize()
        self.assertIsInstance(serialized_product, dict)
        self.assertEqual(serialized_product["name"], product.name)
        self.assertEqual(serialized_product["description"], product.description)
        self.assertEqual(serialized_product["price"], str(product.price))
        self.assertEqual(serialized_product["available"], product.available)
        self.assertEqual(serialized_product["category"], product.category.name)
    
    def test_deserialize_a_product(self):
        """It should Deserialize a product from a dictionary"""
        product = ProductFactory()
        product_data = {
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "available": product.available,
            "category": product.category
        }
        product.deserialize(product_data)
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.description, "Test Description")
        self.assertEqual(product.price, Decimal("19.99"))
        self.assertEqual(product.available, True)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_get_all_products(self):
        """It should return all products in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)

    def test_find_a_product(self):
        """It should find a product by its ID"""
        product = ProductFactory()
        product.create()
        found_product = Product.find(product.id)
        self.assertIsNotNone(found_product)
        self.assertEqual(found_product.id, product.id)

    def test_find_by_name(self):
        """It should return all products with the given name"""
        product = ProductFactory()
        product.create()
        products = Product.find_by_name(product.name)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, product.name)
    
    def test_find_by_price(self):
        """It should return all products with the given price"""
        product = ProductFactory()
        product.create()
        products = Product.find_by_price(product.price)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].price, product.price)

    def test_find_by_availability(self):
        """It should return all products by their availability"""
        product = ProductFactory()
        product.create()
        products = Product.find_by_availability(product.available)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].available, product.available)

    def test_find_by_category(self):
        """It should return all products by their category"""
        product = ProductFactory()
        product.create()
        products = Product.find_by_category(product.category)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].category, product.category)