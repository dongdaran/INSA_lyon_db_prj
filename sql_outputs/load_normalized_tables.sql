-- Active: 1749715778350@@127.0.0.1@3306@ccrb_db
-- Active: 1749715778350@@127.0.0.1@3306@blog
SET FOREIGN_KEY_CHECKS = 0;

-- ========================================================
-- 1. Precinct (from staging_complaints)
-- ========================================================
INSERT IGNORE INTO Precinct (Precinct_ID, Borough)
SELECT DISTINCT
    CAST(Precinct_Of_Incident_Occurrence AS UNSIGNED),
    Borough_Of_Incident_Occurrence
FROM staging_complaints;


-- ========================================================
-- 2. Complaint
--   Incident_Date를 Year/Month/Day로 분해해서 저장
-- ========================================================
UPDATE staging_complaints
SET Precinct_Of_Incident_Occurrence =
    TRIM(BOTH '|' FROM REPLACE(Precinct_Of_Incident_Occurrence, 'Precinct ', ''))
WHERE Precinct_Of_Incident_Occurrence LIKE 'Precinct %';


INSERT INTO Complaint (
    Complaint_ID,
    Precinct_ID,
    Incident_Year,
    Incident_Month,
    Incident_Day,
    CCRB_Complaint_Disposition,
    Reason_For_Police_Contact,
    Location_Type_Of_Incident
)
SELECT
    -- Complaint_ID
    CAST(NULLIF(Complaint_ID, '') AS UNSIGNED) AS Complaint_ID,
    -- Precinct_ID
    CAST(NULLIF(Precinct_Of_Incident_Occurrence, '') AS UNSIGNED) AS Precinct_ID,
    -- Incident_Year: YYYY-xx-xx → 앞 4자리
    CASE 
        WHEN Incident_Date IS NULL OR Incident_Date = ''
            THEN NULL
        ELSE CAST(SUBSTRING_INDEX(Incident_Date, '-', 1) AS UNSIGNED)
    END AS Incident_Year,
    -- Incident_Month: YYYY-MM-xx → 가운데 MM, 잘못된 값/결번이면 NULL
    CASE 
        WHEN Incident_Date IS NULL
             OR Incident_Date = ''
             OR SUBSTRING_INDEX(SUBSTRING_INDEX(Incident_Date, '-', 2), '-', -1) IN ('', '__')
            THEN NULL
        ELSE CAST(
            SUBSTRING_INDEX(
                SUBSTRING_INDEX(Incident_Date, '-', 2),
                '-',
                -1
            ) AS UNSIGNED
        )
    END AS Incident_Month,
    -- Incident_Day: YYYY-xx-DD → 마지막 DD, 잘못된 값/결번이면 NULL
    CASE 
        WHEN Incident_Date IS NULL
             OR Incident_Date = ''
             OR SUBSTRING_INDEX(Incident_Date, '-', -1) IN ('', '__')
            THEN NULL
        ELSE CAST(
            SUBSTRING_INDEX(Incident_Date, '-', -1) AS UNSIGNED
        )
    END AS Incident_Day,
    -- 나머지 문자열 컬럼들
    CCRB_Complaint_Disposition,
    Reason_for_Police_Contact,
    Location_Type_Of_Incident
FROM staging_complaints;





-- ========================================================
-- 3. Complaint_Evidence
-- ========================================================
INSERT INTO Complaint_Evidence (
    Complaint_ID,
    BWC_Evidence,
    Video_Evidence
)
SELECT
    CAST(NULLIF(Complaint_ID, '') AS UNSIGNED) AS Complaint_ID,
    (BWC_Evidence = 'Yes'),
    (Video_Evidence = 'Yes')
FROM staging_complaints;


-- ========================================================
-- 4. Allegation_Detail
-- ========================================================
INSERT INTO Allegation_Detail (
    Complaint_ID,
    FADO_Type,
    Allegation,
    Investigator_Disposition_Rec,
    NYPD_Disposition,
    CCRB_Disposition
)
SELECT
    CAST(NULLIF(Complaint_ID, '') AS UNSIGNED) AS Complaint_ID,
    FADO_Type,
    Allegation,
    CCRB_Investigations_Division_Recommendation,
    NYPD_Allegation_Disposition,
    CCRB_Allegation_Disposition
FROM staging_allegations;


-- ========================================================
-- 5. Victim_Info
-- ========================================================
INSERT INTO Victim_Info (
    Allegation_ID,
    Age_Range,
    Gender,
    Race
)
SELECT
    ad.Allegation_ID,                                        -- 🔥 AUTO_INCREMENT PK 가져오기
    sa.Victim_Alleged_Victim_Age_Range_At_Incident,
    sa.Victim_Alleged_Victim_Gender,
    sa.Victim_Alleged_Victim_Race_Ethnicity
FROM staging_allegations sa
JOIN Allegation_Detail ad
    ON ad.Complaint_ID = CAST(NULLIF(sa.Complaint_ID,'') AS UNSIGNED)



-- ========================================================
-- 6. Command
-- ========================================================
INSERT IGNORE INTO Command (Command_Code, Command_Name)
SELECT DISTINCT
    Command_Code,
    Command_Name
FROM staging_commands
WHERE Command_Code IS NOT NULL;


-- ========================================================
-- 7. rank_system
-- ========================================================
INSERT IGNORE INTO rank_system (Abbreviation, Rank_Name)
SELECT DISTINCT
    Abbreviation, 
    Rank_Name
FROM staging_ranksystem
WHERE Abbreviation IS NOT NULL;


-- ========================================================
-- 8. current_officer_info
-- ========================================================
INSERT INTO current_officer_info (
    Tax_ID,
    Current_Command,
    Active_Last_Status,
    Last_Active_Date,
    First_Name,
    Last_Name,
    Gender,
    Race,
    Abbreviation,
    Shield_Num
)
SELECT DISTINCT
    CAST(soi.Tax_ID AS UNSIGNED),
    cmd.Command_Code,
    soi.Active_Per_Last_Reported_Status,
    STR_TO_DATE(soi.Last_Reported_Active_Date, '%m/%d/%Y %r'),
    soi.Officer_First_Name,
    soi.Officer_Last_Name,
    soi.Officer_Gender,
    soi.Officer_Race,
    -- 🔥 rank_system에 있으면 사용 / 없으면 NULL
    rs.Abbreviation,
    CAST(NULLIF(soi.Shield_No, '') AS UNSIGNED) AS Shield_No
FROM staging_officers soi
LEFT JOIN Command cmd
  ON TRIM(soi.Current_Command)
     COLLATE utf8mb4_unicode_ci
   = TRIM(cmd.Command_Code)
     COLLATE utf8mb4_unicode_ci

LEFT JOIN rank_system rs
  ON TRIM(soi.Current_Rank_Abbreviation)
     COLLATE utf8mb4_unicode_ci
   = TRIM(rs.Abbreviation)
     COLLATE utf8mb4_unicode_ci




-- ========================================================
-- 9. Officer_Complaint_Status
-- ========================================================
INSERT INTO Officer_Complaint_Status (
    Tax_ID,
    Total_Complaints,
    Total_Substantiated
)
SELECT
    CAST(Tax_ID AS UNSIGNED),
    CAST(Total_Complaints AS UNSIGNED),
    CAST(Total_Substantiated_Complaints AS UNSIGNED)
FROM staging_officers
WHERE Total_Complaints IS NOT NULL
ON DUPLICATE KEY UPDATE
    Total_Complaints = VALUES(Total_Complaints),
    Total_Substantiated = VALUES(Total_Substantiated);



-- ========================================================
-- 10. Penalty_Record (Main record)
-- ========================================================
INSERT INTO Penalty_Record (
    Complaint_ID,
    Tax_ID,
    CCRB_Substantiated_Officer_Disposition,
    is_APU,
    NYPD_Officer_Penalty
)
SELECT
    CAST(Complaint_ID AS UNSIGNED),
    CAST(Tax_ID AS UNSIGNED),
    CCRB_Substantiated_Officer_Disposition,
    (Officer_is_APU = 'Yes'),
    NYPD_Officer_Penalty
FROM staging_penalties;


-- ========================================================
-- 11. yes_APU (Subtype)
-- ========================================================
INSERT INTO yes_APU (
    Penalty_ID,
    APU_CCRB_Trial_Recommended_Penalty,
    APU_Trial_Commissioner_Recommended_Penalty,
    APU_Plea_Agreed_Penalty,
    APU_Case_Status,
    APU_Closing_Date
)
SELECT
    pr.Penalty_ID,
    sp.APU_CCRB_Trial_Recommended_Penalty,
    sp.APU_Trial_Commissioner_Recommended_Penalty,
    sp.APU_Plea_Agreed_Penalty,
    sp.APU_Case_Status,
    CASE
        WHEN sp.APU_Closing_Date IS NULL OR sp.APU_Closing_Date = ''
        THEN NULL
        ELSE STR_TO_DATE(sp.APU_Closing_Date, '%m/%d/%Y')
    END AS APU_Closing_Date
FROM staging_penalties sp
JOIN Penalty_Record pr
  ON pr.Complaint_ID = CAST(NULLIF(sp.Complaint_ID,'') AS UNSIGNED)
 AND pr.Tax_ID = CAST(NULLIF(sp.Tax_ID,'') AS UNSIGNED)
 AND pr.CCRB_Substantiated_Officer_Disposition
     COLLATE utf8mb4_0900_ai_ci
   = sp.CCRB_Substantiated_Officer_Disposition
     COLLATE utf8mb4_0900_ai_ci
WHERE sp.Officer_is_APU
      COLLATE utf8mb4_0900_ai_ci = 'Yes';




-- ========================================================
-- 12. non_APU (Subtype)
-- ========================================================
INSERT INTO non_APU (
    Penalty_ID,
    Non_APU_NYPD_Penalty_Report_Date
)
SELECT
    pr.Penalty_ID,
    CASE
        WHEN sp.Non_APU_NYPD_Penalty_Report_Date IS NULL
             OR sp.Non_APU_NYPD_Penalty_Report_Date = ''
        THEN NULL
        ELSE STR_TO_DATE(sp.Non_APU_NYPD_Penalty_Report_Date, '%m/%d/%Y')
    END AS Non_APU_NYPD_Penalty_Report_Date
FROM staging_penalties sp
JOIN Penalty_Record pr
  ON pr.Complaint_ID = CAST(NULLIF(sp.Complaint_ID,'') AS UNSIGNED)
 AND pr.Tax_ID = CAST(NULLIF(sp.Tax_ID,'') AS UNSIGNED)
 AND pr.CCRB_Substantiated_Officer_Disposition
     COLLATE utf8mb4_0900_ai_ci
   = sp.CCRB_Substantiated_Officer_Disposition
     COLLATE utf8mb4_0900_ai_ci
WHERE sp.Officer_is_APU
      COLLATE utf8mb4_0900_ai_ci <> 'Yes';




-- ========================================================
-- 13. allegation_period_officer_info
-- ========================================================

ALTER TABLE allegation_period_officer_info
MODIFY At_Command VARCHAR(50);

INSERT INTO allegation_period_officer_info (
    Allegation_ID,
    Tax_ID,
    Complaint_Officer_Number,
    Abbrevation,
    At_Command,
    Days_On_Force_At_Incident
)
SELECT DISTINCT
    ad.Allegation_ID,
    coi.Tax_ID,
    CAST(NULLIF(sp.Complaint_Officer_Number, '') AS UNSIGNED),
    sp.Officer_Rank_Abbreviation_At_Incident,
    cmd.Command_Code,
    CASE 
        WHEN CAST(NULLIF(sp.Officer_Days_On_Force_At_Incident,'') AS SIGNED)
             BETWEEN -200000 AND 200000
        THEN ABS(CAST(NULLIF(sp.Officer_Days_On_Force_At_Incident,'') AS SIGNED))
        ELSE NULL
    END AS Days_On_Force_At_Incident
FROM staging_allegations sp
JOIN Allegation_Detail ad
  ON ad.Complaint_ID = CAST(NULLIF(sp.Complaint_ID, '') AS UNSIGNED)
JOIN current_officer_info coi
  ON coi.Tax_ID = CAST(NULLIF(sp.Tax_ID, '') AS UNSIGNED)
LEFT JOIN Command cmd
  ON TRIM(sp.Officer_Command_At_Incident)
     COLLATE utf8mb4_0900_ai_ci
   = TRIM(cmd.Command_Code)
     COLLATE utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;

