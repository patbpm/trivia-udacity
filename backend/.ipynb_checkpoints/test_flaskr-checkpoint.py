import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from settings import  DB_USER, DB_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'trivia_test'
        self.database_path ="postgres://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Test Get Categories
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        
        
    # Test Get Questions Endpoint
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
    
    # Test Get Categories With Wrong Endpoint
    def test_404_get_categories(self):
        res = self.client().get('/categoriess')

        self.assertEqual(res.status_code, 404)
        
    # Test Get Questions With Wrong Endpoint
    def test_404_get_questions(self):
        res = self.client().get('/questionss')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not found")

    # Test Pagination Beyond valid Page
    def test_404_sent_request_beyond_valid_page(self):
        res = self.client().get('/questions?page=500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    # Test Delete Question Endpoint
    def test_delete_question(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)
      
        question = Question.query.filter(Question.id == 1).one_or_none()
        self.assertEqual(question, None)
        self.assertEqual(data['success'], True)

    # Test Delete Question With Wrong ID
    def test_422_delete_question(self):
        res = self.client().delete('/questions/0')
        data = json.loads(res.data)
      
        question = Question.query.filter(Question.id == 0).one_or_none()
        self.assertEqual(question, None)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    # Test Post Question Endpoint
    def test_insert_question(self):
        res = self.client().post(
            '/questions', 
            json={
                'question': 'What program is this?', 
                'answer': 'ALX-T',
                'difficulty': 1,
                'category': 1
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
     # Test get paginated book    
    def test_get_paginated_books(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
     
    # Test 404 requesting beyond available page
    def test_404_requesting_beyond_available_page(self):
        response = self.client().get("/questions?page=100000")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')
        
     # Test select categories
    
    def test_select_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        
     # Test select categories Errors
    def test_select_category_error(self):
        response = self.client().get('/categories/category/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')


    def test_search_question(self):
        find = {'searchTerm': 'a'}
        response = self.client().post('/questions/search', json=find)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
    
     # Test search termas empty

    def test_400_search_question_searchterm_empty(self):
        find = {'searchTerm': ''}
        response = self.client().post('/questions/search', json=find)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')
        
     # Test search terms without result
    
    def test_book_search_without_results(self):
        find = {'searchTerm': 'm4jrimfkrjnfr'}
        response = self.client().post('/questions/search', json=find)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone((data['questions']))
        
    
    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()