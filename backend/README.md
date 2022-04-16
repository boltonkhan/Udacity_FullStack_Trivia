# Backend - Trivia API

## Setting up the Backend

### Install Dependencies

1. The solution was written and tested with Python 3.9.7 Anaconda distribution

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:
pip install -r requirements.txt

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py` and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

### Set up the Database

The project uses 2 separated databases: for a production environment and for the tests environment. In both cases, the solution is prepared to work with postgres sql.

**1. Production Environment**

  * **Connection parameters.** 

    Default values: 
    *  *host = `localhost`*,
    * *port = 5432*, 
    * *database name = `trivia_app`*.
     
  	Username and password are not setup. To set it up add environment variables: 
    * `TRIVIA_DB_USERNAME_PROD`
    * `TRIVIA_DB_PASSWORD_PROD`
     
    All of these parameters mentioned before can be changed by setting up enviroment variables. Accordingly: 
    * `TRIVIA_DB_HOST_PROD`, 
    * `TRIVIA_DB_PORT_PROD`, 
    * `TRIVIA_DB_NAME_PROD`

  * Initial setup

    The database itself and the user have to be created at first. Then Flask-Migration can be used to create the schema of the database. The migration script is created and available in a `migration` folder. To see details about Flask-Migrate (https://flask-migrate.readthedocs.io/en/latest/). 
    
    Having the database created, to load sample data, run python script located in a file: *`backend/init_database.py`*

**2. Test enviroment**

* To be able to run tests located in file *`backend/test_flaskr.py`* the test database have to be setup. 
	The database is created before run the tests and is dropped after all tests are finished. Test data are loaded from the files: *`backend/sample_data/categories.csv`* and *`backend/sample_data/questions.csv`*. 
  To make the whole process possible a few adjustements are needed.

  * To create a database you have to setup user with privileges to database creation. The user has to be created in a database and privileges to   create database has to be granted for him. 

  * Test database configuration.

    By default, the master database (to create test database the user has to be connected to existing database, the test database does not exists in the moment) is *`postgres`*. To change it, set up the environment variable **`TRIVIA_MASTER_DATABASE_NAME`**. 
    
    To set up the username and password use enviroment variables:
     * `TRIVIA_DB_USERNAME_TEST`
     * `TRIVIA_DB_PASSWORD_TEST`
     
    The rest of the parameters by default: 
    * database name: `trivia_test`,
    * port: 5432, 
    * host: localhost. 
    
    All can be changed with setting up environment variables:
    * `TRIVIA_DB_NAME_TEST`,
    * `TRIVIA_DB_PORT_TEST`,
    * `TRIVIA_DB_HOST_TEST`.

    To run tests use comment: 
    
    ```
    python backend/test_flaskr.py
    ``` 


### Run the Server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.


## ENDPOINTS DOCUMENTATION

There is a documentation of all API endpoints available in Trivia application.



**`GET '/api/v1.0/categories'`**


- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category.
- Request Arguments: emptyIncluded. If set to True all categories are returned regardless the fact if there are questions in them. If set to False, only categories with questions are included in the response. Default value = True.
- Returns: An object with a single key, `categories`, that contains an object of `id: category_string` key: value pairs.

- Sample requests

	```
	curl 127.0.0.1:5000/api/v1.0/categories
	curl 127.0.0.1:5000/api/v1.0/categories&emptyIncluded=false
	```

- Sample response

	```json
	{
	  "1": "Science",
	  "2": "Art",
	  "3": "Geography",
	  "4": "History",
	  "5": "Entertainment",
	  "6": "Sports"
	}
	```



****`GET '/api/v1.0/questions'`****

- Fetches a dictionary of available categories represent by a dictinary (with any questions only), current category, a collection of questions where each of them is a dictionary and total_questions count.
- The endpoint returns paginated results. Page size is 10.
- Request arguments: page. Page number to take questions from. Default is 1.
- Sample requests:
  
	```
	curl 127.0.0.1:5000/api/v1.0/questions?page=2
	curl 127.0.0.1:5000/api/v1.0/questions
	```

- Sample response:
  
	```json
	{
      "categories": {
          "1": "Science",
          "2": "Art",
          "4": "History",
          "5": "Entertainment"
      },
      "current_category": null,
      "questions": [
          {
            "answer": "One",
            "category": 2,
            "difficulty": 4,
            "id": 14,
            "question": "How many paintings did Van Gogh sell in his lifetime?"
          },
          {
            "answer": "The Liver",
            "category": 1,
            "difficulty": 4,
            "id": 16,
            "question": "What is the heaviest organ in the human body?"
          },
          {
            "answer": "Alexander Fleming",
            "category": 1,
            "difficulty": 3,
            "id": 17,
            "question": "Who discovered penicillin?"
        }
      ],
      "success": true,
      "total_questions": 104
  }
	```



**`GET '/api/v1.0/questions/<int:question_id>'`**

- Fetches a single question specified by the id.
- Request arguments: id of the question. If not exist, 404 is returned.
- Returns an question object represents by a dictionary.
- Sample request:
  
	```
	curl 127.0.0.1:5000/api/v1.0/questions/5
	```

- Sample response:
  
	```json
	{
    "question": {
        "answer": "Edward Scissorhands",
        "category": 5,
        "difficulty": 3,
        "id": 5,
        "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
      },
    "success": true
  }
	```


**`DELETE '/api/v1.0/questions/<int:question_id>'`**

- Delete a question with the provided id. If not exists 404 is returned.
- Request arguments: question_id.
- Return 200 status code if operation was successed.
- Sample request:

	```
	curl -X DELETE http://localhost:5000/api/v1.0/questions/1
	```


**`POST '/api/v1.0/questions'`**

- Create a new question.
- Request arguments (provided as a body): 
  
	```json
  {
	  "question": "some question text",
	  "answer": "answer for the question",
	  "category": 1,
	  "difficulty": 2"
  }
	```

	**Category** and **difficulty** have to be an **integer** type.

  **Category** has to existed is a database. 

  **Difficulty** has to be within a range 1 - 5.
- Return 201 status code if operation was successed. Location header contains the uri to newly created question is set.
  
- Sample request:
  
	```
  curl -X POST -H "Content-Type: application/json" -d '{"question": "text", "answer": "text", "category": 3, "difficulty": 3}' http://localhost:5000/api/v1.0/questions
	```



**`POST '/api/v1.0/questions/searches'`**

- Fetches all questions contain in the question text povided parameter searchTerm.
- Request arguments (as body): searchTerm, string to search for.
- Returns a list of found questions, the found questions count and current category.
- Sample request:
	```
	curl -X POST -H "Content-Type: application/json" -d \
  '{"searchTerm": "title"}' http://localhost:5000/api/v1.0/questions/searches
	```
- Sample response:
	```json
	{
  	"current_category": null,
  	"questions": [
    	{
    	  "answer": "Edward Scissorhands",
    	  "category": 5,
    	  "difficulty": 3,
    	  "id": 5,
    	  "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    	},
    	{
    	  "answer": "Maya Angelou",
    	  "category": 4,
    	  "difficulty": 2,
    	  "id": 20,
    	  "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    	}
     ],
  	"success": true,
  	"total_questions": 9
	}
	```

**`GET '/api/v1.0/categories/<int:category_id>/questions'`**

- Fetches all questions from a provided category.
- Request arguments: category_id, integer, has to exist
- Return: a collection of question objects, the number of questions in the category and a current category.

- Sample request:
  
	```
	curl http://localhost:5000/api/v1.0/categories/2/questions
	```

- Sample response:
  
	```json
	{
     "current_category": {
    	"id": 2,
    	"type": "Art"
  	  },
  	 "questions": [
  	    {
    	  "answer": "Escher",
    	  "category": 2,
    	  "difficulty": 1,
    	  "id": 12,
    	  "question": "Which Dutch graphic artist–initials M C was a creator of optical illusions?"
    	},
    	{
    	  "answer": "Mona Lisa",
    	  "category": 2,
    	  "difficulty": 3,
    	  "id": 13,
    	  "question": "La Giaconda is better known as what?"
    	}
    ],
     "success": true,
     "total_questions": 20
	}
	```

**`POST '/api/v1.0/quizzes'`**

- Fetches random question from a given category (if provided, otherwise returns question selected from all questions). The list of question to draw from is filtered by previous_question parameter. Other words, randomly selected question will not be from the list defined in previous_question parameter.
- Request arguments (as a body): previous_questions (a collection of ids) and category.
- Returns a question as a dictionary.
- Sampele request:

    ```
    curl -X POST -H "Content-Type: application-json" -d '{"previous_questions": [1], "quiz_category": {"type": "Art", "id": "2"}}' http://localhost:5000/api/v1.0/quizzes
    ```
- Sample response: 

  ```json
  {
    "question": {
        "answer": "One",
        "category": 2,
        "difficulty": 4,
        "id": 14,
        "question": "How many paintings did Van Gogh sell in his lifetime?"
    },
    "success": true
  }
  ```