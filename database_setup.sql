-- ####################################################################
-- ## STEP 1: CREATE THE DATABASE                                    ##
-- ## Run this command first, then connect to the 'agentsuite' DB.   ##
-- ####################################################################

CREATE DATABASE agentsuite;

-- ####################################################################
-- ## IMPORTANT: Now, connect to the 'agentsuite' database before    ##
-- ## running the rest of this script. In psql, use: \c agentsuite   ##
-- ####################################################################


-- ####################################################################
-- ## STEP 2: CREATE THE SYSTEM SCHEMA AND ITS TABLES                ##
-- ####################################################################

CREATE SCHEMA system;

-- Create the users table for login details
CREATE TABLE system.users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create the agents table to store details of all agents
CREATE TABLE system.agents (
    agent_id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    schema_name VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Populate the agents table
INSERT INTO system.agents (agent_name, description, schema_name) VALUES
('Job Placement RAG', 'A conversational agent to assist with student job placements in the healthcare field.', 'jobplacement_RAG'),
('AI-Powered Instructor Assistant', 'Analyzes student feedback from files to provide summaries, sentiment, and actionable suggestions.', 'instructor_assistant');


-- ####################################################################
-- ## STEP 3: CREATE THE JOB PLACEMENT SCHEMA AND TABLES             ##
-- ####################################################################

CREATE SCHEMA jobplacement_RAG;

-- Create table for healthcare training programs
CREATE TABLE jobplacement_RAG.training_programs (
    program_id SERIAL PRIMARY KEY,
    program_name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

-- Create table for healthcare employers
CREATE TABLE jobplacement_RAG.employers (
    employer_id SERIAL PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100),
    website VARCHAR(255),
    contact_email VARCHAR(100)
);

-- Create table for students, linked to a training program
CREATE TABLE jobplacement_RAG.students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    major VARCHAR(100),
    graduation_year INT,
    resume_url TEXT,
    program_id INT,
    CONSTRAINT fk_program
        FOREIGN KEY(program_id)
        REFERENCES jobplacement_RAG.training_programs(program_id)
);

-- Create table for job listings from employers
CREATE TABLE jobplacement_RAG.job_listings (
    job_id SERIAL PRIMARY KEY,
    employer_id INT NOT NULL,
    job_title VARCHAR(150) NOT NULL,
    job_description TEXT,
    min_salary NUMERIC(10, 2),
    max_salary NUMERIC(10, 2),
    location VARCHAR(100),
    posted_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (employer_id) REFERENCES jobplacement_RAG.employers(employer_id)
);

-- Create table to track job placements of students
CREATE TABLE jobplacement_RAG.placements (
    placement_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    job_id INT NOT NULL,
    placement_date DATE NOT NULL,
    offered_salary NUMERIC(10, 2),
    FOREIGN KEY (student_id) REFERENCES jobplacement_RAG.students(student_id),
    FOREIGN KEY (job_id) REFERENCES jobplacement_RAG.job_listings(job_id)
);


-- ####################################################################
-- ## STEP 4: POPULATE THE JOB PLACEMENT TABLES WITH HEALTHCARE DATA ##
-- ####################################################################

-- Insert healthcare employers
INSERT INTO jobplacement_RAG.employers (company_name, industry, website, contact_email) VALUES
('Thong Trams Medical Clinic', 'Healthcare', 'http://example.com/thongtrams', 'hr@thongtrams.example.com'),
('Rolling Hills Clinic', 'Healthcare', 'http://example.com/rollinghills', 'careers@rollinghills.example.com'),
('Ampla Health', 'Healthcare', 'http://example.com/amplahealth', 'jobs@amplahealth.example.com'),
('Northern Valley Indian Health', 'Healthcare', 'http://example.com/nvih', 'recruitment@nvih.example.com'),
('Peach Tree Health', 'Healthcare', 'http://example.com/peachtree', 'hr@peachtree.example.com');

-- Insert healthcare training programs
INSERT INTO jobplacement_RAG.training_programs (program_name, description) VALUES
('Phlebotomy Technician Program', 'Trains students to draw blood for tests, transfusions, donations, or research.'),
('Medical Assistant Program', 'Prepares students for administrative and clinical duties in a healthcare setting.'),
('Pharmacy Technician Program', 'Trains students to assist pharmacists in dispensing prescription medication.'),
('Patient Care Technician Program', 'Focuses on direct patient care skills such as bathing, feeding, and monitoring vital signs.'),
('Emergency Medical Technician Program', 'Prepares students to provide out-of-hospital emergency medical care.'),
('Online Medical Billing & Coding Specialist Program', 'Trains students in the critical process of medical coding and billing for insurance reimbursement.'),
('Online EKG Technician Program', 'Focuses on performing electrocardiograms (EKGs) to monitor and record heart activity.');

-- Insert mock students enrolled in these programs
INSERT INTO jobplacement_RAG.students (first_name, last_name, email, major, graduation_year, program_id) VALUES
('Maria', 'Garcia', 'maria.g@university.edu', 'Healthcare Studies', 2025, 1),
('David', 'Chen', 'david.c@university.edu', 'Pre-Med', 2024, 2),
('Laura', 'Wilson', 'laura.w@university.edu', 'Health Administration', 2025, 6),
('James', 'Miller', 'james.m@university.edu', 'Nursing', 2024, 4),
('Sophia', 'Lee', 'sophia.l@university.edu', 'Biology', 2025, 1);

-- Insert healthcare job listings with salaries in standard US dollar numeric format
INSERT INTO jobplacement_RAG.job_listings (employer_id, job_title, job_description, min_salary, max_salary, location) VALUES
(1, 'Certified Phlebotomy Technician', 'Seeking a skilled Phlebotomy Technician to perform blood draws and prepare specimens for medical testing.', 40000.00, 52000.00, 'Chico, CA'),
(2, 'Medical Assistant (MA)', 'Full-time Medical Assistant needed for a busy family practice. Responsibilities include patient intake, vital signs, and assisting with minor procedures.', 45000.00, 58000.00, 'Redding, CA'),
(3, 'Pharmacy Technician', 'Ampla Health is looking for a certified pharmacy technician to manage prescriptions and assist our pharmacists.', 48000.00, 62000.00, 'Yuba City, CA'),
(5, 'Patient Care Technician (PCT)', 'Peach Tree Health requires a compassionate PCT for our inpatient care unit. Must have relevant certification.', 42000.00, 55000.00, 'Sacramento, CA'),
(4, 'Medical Billing and Coding Specialist', 'Remote work opportunity for an experienced medical coder to join our administrative team.', 55000.00, 70000.00, 'Remote');

-- Insert expanded placement data
INSERT INTO jobplacement_RAG.placements (student_id, job_id, placement_date, offered_salary) VALUES
(1, 1, '2025-06-15', 51500.00), -- Maria Garcia (Phlebotomy student) gets the Phlebotomy Technician job.
(2, 2, '2024-08-01', 56000.00), -- David Chen (Medical Assistant student) gets the Medical Assistant job.
(3, 5, '2025-07-20', 68000.00), -- Laura Wilson (Billing & Coding student) gets the remote Billing and Coding Specialist job.
(4, 4, '2024-09-01', 54500.00); -- James Miller (Patient Care student) gets the Patient Care Technician job.