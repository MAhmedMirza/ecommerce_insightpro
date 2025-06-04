import pyodbc
from ..models import db
from app import current_app

def perform_rfm_analysis(user_id):
    """Perform RFM analysis for a specific user"""
    conn = pyodbc.connect(current_app.config['SQLALCHEMY_DATABASE_URI'].replace('mssql+pyodbc:///?odbc_connect=', ''))
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            -- Calculate RFM metrics
            WITH rfm_raw AS (
                SELECT 
                    c.CustomerKey,
                    c.OriginalCustomerID,
                    DATEDIFF(day, MAX(t.FullDate), GETDATE()) AS recency,
                    COUNT(DISTINCT s.OrderID) AS frequency,
                    SUM(s.TotalAmount) AS monetary
                FROM FactSales s
                JOIN DimCustomers c ON s.CustomerKey = c.CustomerKey
                JOIN DimTime t ON s.TimeKey = t.TimeKey
                WHERE s.UserID = ?
                GROUP BY c.CustomerKey, c.OriginalCustomerID
            ),
            rfm_scores AS (
                SELECT
                    CustomerKey,
                    OriginalCustomerID,
                    recency,
                    frequency,
                    monetary,
                    NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
                    NTILE(5) OVER (ORDER BY frequency) AS f_score,
                    NTILE(5) OVER (ORDER BY monetary) AS m_score
                FROM rfm_raw
            )
            
            -- Update customer records with RFM scores
            UPDATE c
            SET 
                c.RecencyScore = r.r_score,
                c.FrequencyScore = r.f_score,
                c.MonetaryScore = r.m_score,
                c.RFMScore = CAST(r.r_score AS VARCHAR) + CAST(r.f_score AS VARCHAR) + CAST(r.m_score AS VARCHAR),
                c.LastRFMUpdate = GETDATE()
            FROM DimCustomers c
            JOIN rfm_scores r ON c.CustomerKey = r.CustomerKey
            WHERE c.UserID = ?
        """, user_id, user_id)
        
        conn.commit()
    finally:
        cursor.close()
        conn.close()