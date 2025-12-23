# query/queries.py

"""
This module stores all SQL queries used for analysis.
Each query is mapped by a number key in the QUERIES dictionary.
"""

QUERIES = {

    2: """
        SELECT
            CASE WHEN pr.Tax_ID IS NULL THEN 'No Penalty' ELSE 'Penalty' END AS PenaltyStatus,
            AVG(apoi.Days_On_Force_At_Incident) AS AvgDaysOnForce
        FROM allegation_period_officer_info apoi
        LEFT JOIN Penalty_Record pr ON pr.Tax_ID = apoi.Tax_ID
        GROUP BY PenaltyStatus;
    """,

    3: """
        SELECT
            coi.Race AS Officer_Race,
            vi.Race AS Victim_Race,
            COUNT(*) AS TotalCases,
            ROUND(
                SUM(CASE WHEN ad.CCRB_Disposition LIKE 'Substantiated%' THEN 1 ELSE 0 END) / COUNT(*) * 100,
                2
            ) AS SubstantiatedRate
        FROM Allegation_Detail ad
        JOIN allegation_period_officer_info apoi ON apoi.Allegation_ID = ad.Allegation_ID
        JOIN current_officer_info coi ON coi.Tax_ID = apoi.Tax_ID
        JOIN Victim_Info vi ON vi.Allegation_ID = ad.Allegation_ID
        GROUP BY Officer_Race, Victim_Race
        ORDER BY SubstantiatedRate DESC;
    """,

    4: """
        WITH complaint_stats AS (
            SELECT
                ad.Complaint_ID,
                COUNT(*) AS allegation_count,
                MAX(CASE WHEN ad.CCRB_Disposition LIKE 'Substantiated%' 
                         THEN 1 ELSE 0 END) AS is_substantiated_complaint
            FROM Allegation_Detail AS ad
            GROUP BY ad.Complaint_ID
        )
        SELECT
            allegation_count,
            COUNT(*) AS num_complaints,
            SUM(is_substantiated_complaint) AS substantiated_complaints,
            AVG(is_substantiated_complaint) AS substantiated_ratio
        FROM complaint_stats
        GROUP BY allegation_count
        ORDER BY allegation_count;
    """,

    5: """
        WITH age_loc AS (
            SELECT
                vi.Age_Range,
                c.Location_Type_Of_Incident AS Location_Type,
                COUNT(*) AS cnt
            FROM Victim_Info vi
            JOIN Allegation_Detail ad ON ad.Allegation_ID = vi.Allegation_ID
            JOIN Complaint c ON c.Complaint_ID = ad.Complaint_ID
            GROUP BY vi.Age_Range, c.Location_Type_Of_Incident
        ),
        ranked AS (
            SELECT
                age_loc.*,
                ROW_NUMBER() OVER(
                    PARTITION BY age_loc.Age_Range
                    ORDER BY age_loc.cnt DESC
                ) AS rn
            FROM age_loc
        )
        SELECT
            Age_Range,
            Location_Type,
            cnt AS Cases
        FROM ranked
        WHERE rn = 1
        ORDER BY Age_Range;
    """,

    6: """
        SELECT
    c.Location_Type_Of_Incident AS Location_Type,
    ROUND(
        SUM(CASE WHEN LOWER(TRIM(ce.BWC_Evidence)) = 'yes' THEN 1 ELSE 0 END) / COUNT(*) * 100,
        2
    ) AS BWC_Rate
FROM Complaint c
LEFT JOIN Complaint_Evidence ce 
    ON ce.Complaint_ID = c.Complaint_ID
GROUP BY Location_Type
ORDER BY BWC_Rate DESC;

    """,

    7: """
        WITH complaint_dates AS (
            SELECT
                c.Complaint_ID,
                STR_TO_DATE(
                    CONCAT(
                        c.Incident_Year, '-',
                        LPAD(c.Incident_Month, 2, '0'), '-',
                        LPAD(c.Incident_Day, 2, '0')
                    ),
                    '%Y-%m-%d'
                ) AS incident_date
            FROM Complaint c
        ),
        closing_dates AS (
            SELECT
                pr.Complaint_ID,
                COALESCE(ya.APU_Closing_Date, na.Non_APU_NYPD_Penalty_Report_Date) AS closing_date
            FROM Penalty_Record pr
            LEFT JOIN yes_APU ya ON ya.Penalty_ID = pr.Penalty_ID
            LEFT JOIN non_APU na ON na.Penalty_ID = pr.Penalty_ID
            WHERE COALESCE(ya.APU_Closing_Date, na.Non_APU_NYPD_Penalty_Report_Date) IS NOT NULL
        )
        SELECT
            ce.BWC_Evidence,
            COUNT(*) AS NumCases,
            AVG(DATEDIFF(cd.closing_date, cdates.incident_date)) AS AvgDaysToClose
        FROM closing_dates cd
        JOIN complaint_dates cdates ON cdates.Complaint_ID = cd.Complaint_ID
        JOIN Complaint_Evidence ce ON ce.Complaint_ID = cd.Complaint_ID
        GROUP BY ce.BWC_Evidence;
    """,

    8: """
        WITH officer_rank AS (
            SELECT
                ocs.Tax_ID,
                ocs.Total_Complaints,
                NTILE(10) OVER (ORDER BY ocs.Total_Complaints DESC) AS decile
            FROM Officer_Complaint_Status ocs
        ),
        top10 AS (
            SELECT Tax_ID FROM officer_rank WHERE decile = 1
        )
        SELECT
            ad.FADO_Type,
            COUNT(*) AS TotalAllegations,
            COUNT(CASE WHEN t.Tax_ID IS NOT NULL THEN 1 END) AS AllegationsByTop10,
            ROUND(
                COUNT(CASE WHEN t.Tax_ID IS NOT NULL THEN 1 END) /
                COUNT(*) * 100, 2
            ) AS PercentByTop10
        FROM Allegation_Detail ad
        JOIN allegation_period_officer_info apoi
            ON apoi.Allegation_ID = ad.Allegation_ID
        LEFT JOIN top10 t
            ON t.Tax_ID = apoi.Tax_ID
        GROUP BY ad.FADO_Type
        ORDER BY PercentByTop10 DESC;
    """,

    9: """
        SELECT
            apoi.At_Command AS Command,
            COUNT(*) AS Allegations,
            ROUND(
                AVG(
                    CASE WHEN LOWER(TRIM(ad.CCRB_Disposition)) LIKE 'Substantiated%' 
                         THEN 1 ELSE 0 END
                ) * 100,
                2
            ) AS SubstantiatedRate
        FROM allegation_period_officer_info apoi
        JOIN Allegation_Detail ad ON ad.Allegation_ID = apoi.Allegation_ID
        GROUP BY apoi.At_Command
        ORDER BY SubstantiatedRate DESC;
    """
}


def borough_query(borough: str) -> str:
    """
    Returns a formatted SQL query that depends on a borough input.
    """
    return f"""
WITH overall_avg AS (
    SELECT AVG(Total_Complaints) AS avg_all
    FROM Officer_Complaint_Status
),
borough_avg AS (
    SELECT AVG(ocs.Total_Complaints) AS avg_borough
    FROM Officer_Complaint_Status ocs
    JOIN current_officer_info coi ON coi.Tax_ID = ocs.Tax_ID
    JOIN Command cmd ON cmd.Command_Code = coi.Current_Command
    JOIN Precinct p ON p.Precinct_ID = cmd.Command_Code
    WHERE p.Borough = '{borough}'
)
SELECT
    '{borough}' AS Borough,
    b.avg_borough AS BoroughAvgComplaints,
    o.avg_all AS OverallAvgComplaints,
    ROUND(b.avg_borough - o.avg_all, 2) AS Difference,
    ROUND(b.avg_borough / o.avg_all * 100, 2) AS PercentOfOverall
FROM borough_avg b
CROSS JOIN overall_avg o;
"""
