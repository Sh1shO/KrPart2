from sqlalchemy import Column, String, Integer, Date, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

DATABASE_URL = 'postgresql://postgres:1234@localhost:5432/krch2'
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    manager_id = Column(Integer, ForeignKey("employees.id"))
    fk_manager = relationship("Employee", foreign_keys=[manager_id])

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    position = Column(String(100))
    salary = Column(Integer)
    hire_date = Column(Date)
    department_id = Column(Integer, ForeignKey("departments.id"))
    fk_department = relationship("Department", foreign_keys=[department_id])

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)
    budget = Column(Integer)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    description = Column(String(255))
    status = Column(String(20))
    project_id = Column(Integer, ForeignKey("projects.id"))
    assignee_id = Column(Integer, ForeignKey("employees.id"))
    fk_project = relationship("Project")
    fk_assignee = relationship("Employee")

class EmployeeProject(Base):
    __tablename__ = "employee_projects"
    employee_id = Column(Integer, ForeignKey("employees.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    role = Column(String(50))
    fk_employee = relationship("Employee")
    fk_project = relationship("Project")

def get_session():
    return session 