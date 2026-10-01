from src.database import run_query

try:
    df = run_query("""
        SELECT EMPLOYEE_ID, FIRST_NAME, LAST_NAME, SALARY, DEPARTMENT_ID
        FROM EMPLOYEES
        FETCH FIRST 5 ROWS ONLY"""
        )
    print("Conexión exitosa a Oracle (HR schema)!")
    print(df)
except Exception as e:
    print("Error al conectar a la base de datos:")
    print(e)