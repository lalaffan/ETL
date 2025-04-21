from pydantic import BaseModel
from fastapi import FastAPI, Query, HTTPException
import psycopg2
from typing import Optional, List, Union
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ElectricPowerOperationResponse(BaseModel):
    generation: Optional[str] = None  
    period: Optional[str] = None
    plantname: Optional[str] = None
    fuel: Optional[str] = None
    state: Optional[str] = None
    primemover: Optional[str] = None

class TotalGenerationResponse(BaseModel):
    total_generation_value: float
    results: List[ElectricPowerOperationResponse]  # Add this to return chart data

app = FastAPI()

dsn= os.getenv("DSN")

def get_db_connection():
    try:
        conn = psycopg2.connect(dsn)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

@app.get("/electric_power_operations", response_model=TotalGenerationResponse)
async def get_electric_power_operations(
    start_period: Optional[str] = Query(None, description="Start period for the operation (year or year-month)"),
    end_period: Optional[str] = Query(None, description="End period for the operation (year or year-month)"),
    plantname: Optional[str] = Query(None, description="Plant name"),
    fuel: Optional[str] = Query(None, description="Fuel type used"),
    state: Optional[str] = Query(None, description="State of operation"),
    primemover: Optional[str] = Query(None, description="Prime mover type")
):

    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = conn.cursor()

        base_query = """
            SELECT period, 
                   SUM(CAST(generation AS NUMERIC)) as total_generation, 
                   plantname, 
                   fuel2002, 
                   state, 
                   primemover
            FROM electric_power_operations_by_energy_source
            WHERE 1=1
        """

        query_params = []

        if start_period:
            base_query += " AND period >= %s"
            query_params.append(start_period)  

        if end_period:
            base_query += " AND period <= %s"
            query_params.append(end_period)  

        if plantname:
            base_query += " AND plantname = %s"
            query_params.append(plantname)
        if fuel:
            base_query += " AND fuel2002 = %s"
            query_params.append(fuel)
        else:
            base_query += "AND fuel2002='ALL'"

        if state:
            base_query += " AND state = %s"
            query_params.append(state)
       
        if primemover:
            base_query += " AND primemover = %s"
            query_params.append(primemover)
        else:
            base_query += " AND primemover = 'ALL'"

        base_query += " GROUP BY period, plantname, fuel2002, state, primemover ORDER BY period"

        logger.debug(f"Executing query: {base_query}")
        logger.debug(f"Query parameters: {query_params}")

        cursor.execute(base_query, query_params)

        rows = cursor.fetchall()

        if not rows:
            logger.warning("No data found matching the provided parameters.")
            return TotalGenerationResponse(total_generation_value=0, results=[])

        detailed_results = []
        total_generation_value = 0

        for row in rows:
            total_generation_value += row[1] 

            detailed_results.append(
                ElectricPowerOperationResponse(
                    generation=str(row[1]),  # Keep as string since it may have decimals
                    period=row[0],
                    plantname=row[2],
                    fuel=row[3],
                    state=row[4] if row[4] is not None else "Unknown",
                    primemover=row[5]
                )
            )

        cursor.close()

        logger.debug(f"Total generation value: {total_generation_value}")

        return TotalGenerationResponse(
            total_generation_value=total_generation_value,
            results=detailed_results 
        )
    except psycopg2.Error as e:
        logger.error(f"Database query error: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")
    finally:
        conn.close()
