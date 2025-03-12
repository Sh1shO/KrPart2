create table employees (
    id serial primary key,
    first_name varchar(50),
    last_name varchar(50),
    position varchar(100),
    salary int,
    hire_date date,
    department_id int
);

create table departments (
    id serial primary key,
    name varchar(100),
    manager_id int references employees(id)
);

create table projects (
    id serial primary key,
    name varchar(100),
    start_date date,
    end_date date,
    budget int
);

create table tasks (
    id serial primary key,
    name varchar(100),
    description text,
    status varchar(20) check (status in ('в процессе', 'завершена', 'отменена')),
    project_id integer references projects(id),
    assignee_id integer references employees(id)
);

create table employee_projects (
    employee_id int references employees(id),
    project_id int references projects(id),
    role varchar(50),
    primary key (employee_id, project_id)
); 
