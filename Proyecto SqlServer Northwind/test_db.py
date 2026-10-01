from src.database import run_query

try:
    df = run_query("SELECT TOP 5 CustomerID, CompanyName FROM Customers;")
    print("Conexión exitosa a SQL Server (Northwind)!")
    print(df)
except Exception as e:
    print("Error al conectar a la base de datos:")
    print(e)