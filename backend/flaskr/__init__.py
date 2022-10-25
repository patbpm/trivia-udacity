import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from unicodedata import category
from cmath import exp
from http.cookies import BaseCookie
from json import dumps

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginateQuestion(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    paginatedQuestions= questions[start:end]

    return paginatedQuestions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,PATCH,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories',methods=['GET'])
    def getCategories():
        categories=Category.query.order_by(Category.id).all()
        categoriesDict={}
        for category in categories:
                categoriesDict[category.id] = category.type
        
        return jsonify({
            'success': True,
            'categories':categoriesDict
            
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions',methods=['GET'])
    def getQuestions():

        selection=Question.query.order_by(Question.id).all()
        paginatedQuestions =paginateQuestion(request,selection)

        if len(paginatedQuestions)==0:
            abort(404)

        categories=Category.query.order_by(Category.id).all()
        categoriesDict={}
        for category in categories:
            categoriesDict[category.id] = category.type

        return jsonify({
            'success': True,
            'questions':paginatedQuestions,
            'totalQuestions':len(Question.query.all()),
            'categories':categoriesDict
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>',methods=['DELETE'])
    def deleteQuestion(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(422)
        else:
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            currentQuestions = paginateQuestion(request, selection)

            return jsonify({
                "success": True,
                'deleted': question_id,
                'current_questions': currentQuestions
            })


    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions',methods=['POST'])
    def addQuestions():
        try:
            body=request.get_json()
            newQuestion=body.get('question',None)
            newAnswer=body.get('answer',None)
            newCategory=body.get('category',None)
            newDifficulty=body.get('difficulty',None)
            question=Question(question=newQuestion,answer=newAnswer,category=newCategory,difficulty=newDifficulty)
            question.insert()
        except:
            abort(422)

        return jsonify({
            'success':True
        })
    
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questionsSearch',methods=['POST'])
    def search():
        body=request.get_json()
        search=body.get('searchTerm',None)
        selection=Question.query.filter(Question.question.ilike("%{}%".format(search))).all()
        if selection:
            questions=paginateQuestion(request, selection)
            return jsonify({
                'questions':questions,
                'total_questions':len(selection)
            })
        else:
            abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions',methods=['GET'])
    def retrieveQuestionsByCategory(category_id):
        category=Category.query.filter(Category.id==category_id).one_or_none()
        if category:
            selection=Question.query.filter_by(category=str(category_id)).all()
            questions=paginateQuestion(request,selection)
            return jsonify({
                'questions':questions,
                'CurrentCategory':category.type
            })
        else:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes',methods=['POST'])
    def playQuizze():
        #get the previous question and its category
        body=request.get_json()
        previousQuestions=body.get('previous_questions')
        quizCategory=body.get('quiz_category')


        #get randomly the next question to show 
        try:
            if quizCategory['id']==0:
                questions=Question.query.all()
            else:
                questions=Question.query.filter_by(category=quizCategory['id']).all()
                Index=random.randint(0,len(questions)-1)
                nextQuestion=questions[Index]
                while nextQuestion.id not in previousQuestions:
                    nextQuestion=questions[Index]

                    return jsonify({
                        'success':True,
                        'question':nextQuestion.format()
                    })
        
        except:
            abort(404)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def notNound(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "Unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "Bad request"}), 400

    return app
