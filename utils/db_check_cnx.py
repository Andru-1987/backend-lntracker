from fastapi import Request, HTTPException

async def ensure_db_connection(request: Request):
    if request.app.state.db_status == "connected":
        return

    print(f"Estado DB: {request.app.state.db_status}. Intentando reconexión...")
    try:
        request.app.state.mssql.connect()
        request.app.state.db_status = "connected"
        print("Reconexión exitosa bajo demanda.")
    except Exception as e:
        print(f"Falló la reconexión: {e}")
        return