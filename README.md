# Loan App
API For a Loan App

## Intro
 The project uses Python , and is build upon Django with the Django Rest Framework.

 For the database, it uses a local sqllite instance.

## Features
* Register, Login (TokenAuthentication)
* Create Loan For A User with multiple payments 
* List Loans
* Approve Loan through Admin
* Add a Repayment on payment
* Add a Prepayment on the loan 


## Installation

Clone the repository

    git clone https://github.com/aUnicornDev/loan-app.git

Change directory the loan-app folder

    cd loan-app
    
Create and activate the virtual environment

    python -m venv venv

    venv\Scripts\activate

Install the requirements 

    pip install -r requirements.txt

Migrate Changes

    cd backend

    python manage.py migrate

Create User and Superuser (Optional) -- created to be in sync with Postman API endpoints 
    
    python manage.py populate_db

Start the local development server
    
    python manage.py runserver
    
    
You can now access the server at http://localhost:8000 (*It is adviced to used the postman collection after importing it.*)


To run tests (Unit and Integration)

    python manage.py test

## Docs

A very basic doc around the functionality and files is given in the doc/doc.md file.

## Postman 

Postman export can be found in the docs folder.

After starting the server, you can **View Documentation, Run Collection**  on the Loan API Copy collection. 
 



