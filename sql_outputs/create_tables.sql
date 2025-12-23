-- Active: 1749715778350@@127.0.0.1@3306@ccrb_db
SET FOREIGN_KEY_CHECKS = 0;


-- DROP ALL TABLES (in FK-safe order)
DROP TABLE IF EXISTS allegation_period_officer_info;
DROP TABLE IF EXISTS non_APU;
DROP TABLE IF EXISTS yes_APU;
DROP TABLE IF EXISTS Penalty_Record;
DROP TABLE IF EXISTS Officer_Complaint_Status;
DROP TABLE IF EXISTS current_officer_info;
DROP TABLE IF EXISTS rank_system;
DROP TABLE IF EXISTS Command;
DROP TABLE IF EXISTS Victim_Info;
DROP TABLE IF EXISTS Allegation_Detail;
DROP TABLE IF EXISTS Complaint_Evidence;
DROP TABLE IF EXISTS Complaint;
DROP TABLE IF EXISTS Precinct;



-- 1. Precinct
CREATE TABLE Precinct (
    Precinct_ID INT PRIMARY KEY,
    Borough VARCHAR(20)
);

-- 2. Complaint
CREATE TABLE Complaint (
    Complaint_ID INT PRIMARY KEY,
    Precinct_ID INT,
    Incident_Year INT,
    Incident_Month INT,
    Incident_Day INT,
    Incident_Hour TIME,
    CCRB_Complaint_Disposition VARCHAR(50),
    Reason_For_Police_Contact VARCHAR(100),
    Location_Type_Of_Incident VARCHAR(100),
    FOREIGN KEY (Precinct_ID) REFERENCES Precinct(Precinct_ID)
);

-- 3. Complaint_Evidence
CREATE TABLE Complaint_Evidence (
    Complaint_ID INT PRIMARY KEY,
    BWC_Evidence VARCHAR(50),
    Video_Evidence VARCHAR(50),
    FOREIGN KEY (Complaint_ID) REFERENCES Complaint(Complaint_ID)
);

-- 4. Allegation_Detail
CREATE TABLE Allegation_Detail (
    Allegation_ID INT AUTO_INCREMENT PRIMARY KEY,
    Complaint_ID INT NOT NULL,
    FADO_Type VARCHAR(50),
    Allegation VARCHAR(200),
    Investigator_Disposition_Rec VARCHAR(100),
    NYPD_Disposition VARCHAR(100),
    CCRB_Disposition VARCHAR(100),
    FOREIGN KEY (Complaint_ID) REFERENCES Complaint(Complaint_ID)
);

-- 5. Victim_Info
CREATE TABLE Victim_Info (
    Victim_ID INT AUTO_INCREMENT PRIMARY KEY,
    Allegation_ID INT NOT NULL,
    Age_Range VARCHAR(50),
    Gender VARCHAR(30),
    Race VARCHAR(255),
    FOREIGN KEY (Allegation_ID) REFERENCES Allegation_Detail(Allegation_ID)
);

-- 6. Command
CREATE TABLE Command (
    Command_Code VARCHAR(50) PRIMARY KEY,
    Command_Name VARCHAR(100)
);

-- 7. rank_system
CREATE TABLE rank_system (
    Abbreviation VARCHAR(20) PRIMARY KEY,
    Rank_Name VARCHAR(100)
);

-- 8. current_officer_info
CREATE TABLE current_officer_info (
    Tax_ID INT PRIMARY KEY,
    Current_Command VARCHAR(50),
    Active_Last_Status VARCHAR(50),
    Last_Active_Date DATE,
    First_Name VARCHAR(50),
    Last_Name VARCHAR(50),
    Gender VARCHAR(30),
    Race VARCHAR(50),
    Abbreviation VARCHAR(20),
    Shield_Num INT,
    FOREIGN KEY (Current_Command) REFERENCES Command(Command_Code),
    FOREIGN KEY (Abbreviation) REFERENCES rank_system(Abbreviation)
);

-- 9. Officer_Complaint_Status
CREATE TABLE Officer_Complaint_Status (
    Tax_ID INT PRIMARY KEY,
    Total_Complaints INT,
    Total_Substantiated INT,
    FOREIGN KEY (Tax_ID) REFERENCES current_officer_info(Tax_ID)
);

-- 10. Penalty_Record
CREATE TABLE Penalty_Record (
    Penalty_ID INT AUTO_INCREMENT PRIMARY KEY,
    Complaint_ID INT NOT NULL,
    Tax_ID INT NOT NULL,
    CCRB_Substantiated_Officer_Disposition VARCHAR(100),
    is_APU TINYINT(1),
    NYPD_Officer_Penalty VARCHAR(100),
    FOREIGN KEY (Complaint_ID) REFERENCES Complaint(Complaint_ID),
    FOREIGN KEY (Tax_ID) REFERENCES current_officer_info(Tax_ID)
);

-- 11. yes_APU
CREATE TABLE yes_APU (
    Penalty_ID INT PRIMARY KEY,
    APU_CCRB_Trial_Recommended_Penalty VARCHAR(100),
    APU_Trial_Commissioner_Recommended_Penalty VARCHAR(100),
    APU_Plea_Agreed_Penalty VARCHAR(100),
    APU_Case_Status VARCHAR(100),
    APU_Closing_Date DATE,
    FOREIGN KEY (Penalty_ID) REFERENCES Penalty_Record(Penalty_ID)
);

-- 12. non_APU
CREATE TABLE non_APU (
    Penalty_ID INT PRIMARY KEY,
    Non_APU_NYPD_Penalty_Report_Date DATE,
    FOREIGN KEY (Penalty_ID) REFERENCES Penalty_Record(Penalty_ID)
);

-- 13. allegation_period_officer_info
CREATE TABLE allegation_period_officer_info (
    Allegation_ID INT NOT NULL,
    Tax_ID INT NOT NULL,
    Complaint_Officer_Number INT,
    Abbrevation VARCHAR(50),
    At_Command VARCHAR(20),
    Days_On_Force_At_Incident INT,
    PRIMARY KEY (Allegation_ID, Tax_ID),
    FOREIGN KEY (Allegation_ID) REFERENCES Allegation_Detail(Allegation_ID),
    FOREIGN KEY (Tax_ID) REFERENCES current_officer_info(Tax_ID),
    FOREIGN KEY (At_Command) REFERENCES Command(Command_Code)
);

SET FOREIGN_KEY_CHECKS = 1;
