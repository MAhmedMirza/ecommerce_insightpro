import pandas as pd
import pyodbc
import traceback
from datetime import datetime
from celery import current_task
from time import sleep
from app.config import Config
import logging

logger = logging.getLogger(__name__)

VALID_STATUSES = ['In Progress', 'Failed', 'Success']

def get_connection():
    """Get database connection with retry logic"""
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            conn = pyodbc.connect(Config.get_connection_string())
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            return conn
        except pyodbc.Error as e:
            if attempt == max_retries - 1:
                logger.error(f"Database connection failed after {max_retries} attempts")
                raise RuntimeError(f"Database connection failed: {str(e)}") from e
            logger.warning(f"Database connection attempt {attempt + 1} failed, retrying...")
            sleep(retry_delay)

def validate_status(status):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of {VALID_STATUSES}")

def run_etl_for_user(user_id, dataset_id, file_path):
    conn = None
    cursor = None
    start_time = datetime.now()
    etl_id = None
    processed_records = 0

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Insert initial ETL log
        status = 'In Progress'
        validate_status(status)
        cursor.execute("""
            INSERT INTO ETLLogs (DatasetID, UserID, StartTime, Status)
            VALUES (?, ?, ?, ?)
        """, dataset_id, user_id, start_time, status)
        conn.commit()
        cursor.execute("SELECT SCOPE_IDENTITY()")  # Safer than @@IDENTITY
        etl_id = cursor.fetchone()[0]

        # Read CSV
        current_task.update_state(
            state='In Progress',
            meta={'current': 0, 'total': 1, 'status': 'Reading CSV file', 'progress': 0}
        )
        df = pd.read_csv(file_path)

        required_columns = ['order_id', 'order_date', 'customer_id', 'sku', 'qty_ordered', 'price_each', 'city']
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            raise ValueError(f"Missing required columns: {missing}")

        df.rename(columns={
            'order_id': 'OrderID',
            'order_date': 'OrderDate',
            'customer_id': 'CustomerID',
            'sku': 'ProductID',
            'qty_ordered': 'Quantity',
            'price_each': 'Price',
            'city': 'City'
        }, inplace=True)

        df['OrderDate'] = pd.to_datetime(df['OrderDate']).dt.date
        df['TotalAmount'] = df['Quantity'] * df['Price']
        total_records = len(df)

        current_task.update_state(
            state='In Progress',
            meta={'current': 0, 'total': total_records, 'status': f'Processing {total_records} records', 'progress': 0}
        )

        for idx, row in df.iterrows():
            try:
                cust_id = str(row['CustomerID'])
                prod_id = str(row['ProductID'])
                order_date = row['OrderDate']
                order_id = row['OrderID']
                quantity = int(row['Quantity'])
                price = float(row['Price'])
                city = row['City']
                total = float(row['TotalAmount'])

                # Insert into DimCustomers if not exists
                cursor.execute("""
                    IF NOT EXISTS (
                        SELECT 1 FROM DimCustomers WHERE UserID=? AND OriginalCustomerID=?
                    )
                    INSERT INTO DimCustomers (UserID, OriginalCustomerID, City, FirstPurchaseDate, LastPurchaseDate, TotalPurchases, TotalSpent)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, user_id, cust_id, user_id, cust_id, city, order_date, order_date, 1, total)

                cursor.execute("SELECT CustomerKey FROM DimCustomers WHERE UserID=? AND OriginalCustomerID=?", user_id, cust_id)
                customer_key = cursor.fetchone()[0]

                # Insert into DimProducts if not exists
                cursor.execute("""
                    IF NOT EXISTS (
                        SELECT 1 FROM DimProducts WHERE UserID=? AND OriginalProductID=?
                    )
                    INSERT INTO DimProducts (UserID, OriginalProductID, ProductName, Category, Price)
                    VALUES (?, ?, ?, ?, ?)
                """, user_id, prod_id, user_id, prod_id, f'Product {prod_id}', 'General', price)

                cursor.execute("SELECT ProductKey FROM DimProducts WHERE UserID=? AND OriginalProductID=?", user_id, prod_id)
                product_key = cursor.fetchone()[0]

                # Get TimeKey
                cursor.execute("SELECT TimeKey FROM DimTime WHERE FullDate=?", order_date)
                result = cursor.fetchone()
                if not result:
                    continue  # skip if no TimeKey
                time_key = result[0]

                # Insert into FactSales
                cursor.execute("""
                    INSERT INTO FactSales (UserID, TimeKey, CustomerKey, ProductKey, OrderID, Quantity, UnitPrice, TotalAmount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, user_id, time_key, customer_key, product_key, order_id, quantity, price, total)

                processed_records += 1

                # Update progress every 10 records
                if processed_records % 10 == 0 or processed_records == total_records:
                    progress = int((processed_records / total_records) * 100)
                    current_task.update_state(
                        state='In Progress',
                        meta={
                            'current': processed_records,
                            'total': total_records,
                            'status': f'Processed {processed_records} of {total_records}',
                            'progress': progress
                        }
                    )

            except Exception as inner_e:
                logger.error(f"Error processing record {idx}: {inner_e}")
                continue  # Skip problematic rows

        conn.commit()

        # Run RFM analysis
        cursor.execute("EXEC sp_PerformRFMAnalysis @UserID = ?", user_id)
        conn.commit()

        # Update ETL log success
        status = 'Success'
        validate_status(status)
        cursor.execute("UPDATE UploadedDatasets SET Status = 'Success' WHERE DatasetID = ?", dataset_id)
        cursor.execute("UPDATE ETLLogs SET EndTime = ?, Status = ? WHERE ETLID = ?", datetime.now(), status, etl_id)
        conn.commit()

        return {
            'status': 'Success',
            'dataset_id': dataset_id,
            'processed_records': processed_records,
            'message': 'ETL process completed successfully'
        }

    except Exception as e:
        logger.error(f"ETL failed: {str(e)}\n{traceback.format_exc()}")
        return handle_etl_error(conn, cursor, dataset_id, etl_id, str(e.__class__.__name__), str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def handle_etl_error(conn, cursor, dataset_id, etl_id, error_type, error_details):
    """Handle ETL errors and update logs"""
    try:
        if conn and cursor:
            status = 'Failed'
            validate_status(status)
            cursor.execute("UPDATE UploadedDatasets SET Status = 'Failed' WHERE DatasetID = ?", dataset_id)
            cursor.execute("UPDATE ETLLogs SET EndTime = ?, Status = ?, ErrorMessage = ? WHERE ETLID = ?",
                           datetime.now(), status, f"{error_type}: {error_details}", etl_id)
            conn.commit()
    except Exception as db_error:
        logger.error(f"Failed to update error status in DB: {str(db_error)}")

    return {
        'status': 'Failed',
        'error_type': error_type,
        'error_details': error_details,
        'traceback': traceback.format_exc()
    }
