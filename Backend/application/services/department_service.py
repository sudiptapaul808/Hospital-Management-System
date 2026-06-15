from application.models import SpecializationDept, Doctor 
from sqlalchemy.orm import joinedload

def get_departments_paginated(page, per_page):
    
    departments_query = SpecializationDept.query.order_by(SpecializationDept.id).paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        "departments": [
            {
                "id": d.id,
                "department_name": d.department_name,
                "description": d.description
            } for d in departments_query.items
        ],
        "pagination": {
            "page": departments_query.page,
            "per_page": departments_query.per_page,
            "total": departments_query.total
        }
    }
    
def get_all_departments():
    all_department_names_query = SpecializationDept.query.all()
    
    return {
        "departments": [
            {
                "id": d.id,
                "department_name": d.department_name   
            } for d in all_department_names_query
        ]
    }
    
def doctors_belonging_from_the_department(department_id):
    # department = SpecializationDept.query.get_or_404(department_id)
    
    department = (
        SpecializationDept.query
        .options(
            joinedload(SpecializationDept.doctors) #For joinedload we have to import the models
                .joinedload(Doctor.user) #we don't import User cause we don't do joinedload(User.something)
        ).filter_by(id=department_id).first_or_404()
    )
    
    return [  #since this is a helper, we won't wrap it inside a "data:"
        {
            "id": d.id,
            "name": d.user.username
        } for d in department.doctors
    ]
    