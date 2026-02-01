from sqlalchemy import create_engine

def get_engine():
    server = "DESKTOP-28LC7MC\\SQLEXPRESS"
    database = "GestorFinanzas"

    connection_string = (
        f"mssql+pyodbc://@{server}/{database}"
        "?driver=ODBC+Driver+17+for+SQL+Server"
        "&trusted_connection=yes"
    )

    engine = create_engine(connection_string)
    return engine
if __name__ == "__main__":
    engine = get_engine()
    with engine.connect() as conn:
        print("✅ Conexión exitosa a SQL Server")
