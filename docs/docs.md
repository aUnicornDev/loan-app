# Loan API Docs

## Auth

The auth directory registers 2 endpoints.Underneath uses a very basic Token Based Authentication

    POST http://127.0.0.1:8000/auth/register/
    POST http://127.0.0.1:8000/auth/token/

**The complete body and expected response can found in the Postman Documentation.**

## Loan
The loan directory registers 7 endpoints.

    POST http://127.0.0.1:8000/loan/
    GET http://127.0.0.1:8000/loan/
    GET http://127.0.0.1:8000/loan/<int:loan_id>/
    POST http://127.0.0.1:8000/loan/<int:loan_id>/prepayment/
    POST http://127.0.0.1:8000/loan/<int:loan_id>/repayment/<<int:payment_id>
    GET http://127.0.0.1:8000/loan/<int:loan_id>/payment/<<int:payment_id>

The *models.py* are the objects that are used in Django ORM.
Loan represent the loan.  

Payments are created at the time of loan creation according to the term and frequency logic.
Repayments are the transaction objects recorded against the payments.

#### A Loan will mostly have multiple payments, and a payment can have multiple repayments.


The *api/serializer.py* takes care of creating the objects and mid-layer validation. 

Field Validation, validations related to status of the payment, the prepayment/repayments logic , all is handled in serializer.
 
From an endpoint perspective, repayment and prepayment are two different entities in this project.

###### A prepayment is made towards the loan, i.e the prepayment amount will balance out payments in the order of their timeline.Closest payments will be cleared out first and so on.

###### A repayment is made towards a payment, i.e. the repayment amount will first try and balance the payment against which it was made and if the amount exceeds the amount t be balanced in the payment, the remaining amount will act like prepayment amount.


The *api/views.py* handles the incoming requests from *api/urls.py*.

### Backend
This is the main Django application containing the settings and test of the application. 

**Models, Serializers and API Endpoints --- all have separate test files covering extensive unit and integration tests**


---



### Project Future Improvements 
* Use "unique_id_generation" logic other than INCREMENT
* Extend User object to create a profile and add fields like 'phone_number'
* Decouple "Status" from Loan into a different workflow object
* Add more status on Workflow object (Rejected, Partially Paid)
* Audit history for loan, payments and workflow 
* Create new LoanApproval Model( like generating a ticket ) to handle Admin Approval without directly affecting the Loan
* Notify users at payment approval through Third party messaging
* Cron job for upcoming payments for users
* Basic filtering through query parameters while listing down loans (based on status, to & from date)



    

