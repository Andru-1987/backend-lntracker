# --------------------------------------------------------------------------
# ETAPA 1: BUILDER (Construcción)
# --------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# 1. Instalar dependencias de sistema necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --------------------------------------------------------------------------
# ETAPA 2: RUNTIME (Producción)
# --------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

WORKDIR /app

# 1. Configurar variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/bin:$PATH"

# 2. Instalar Driver ODBC 18 y sus dependencias de runtime
# IMPORTANTE: Agregamos 'libgssapi-krb5-2' que es vital para msodbcsql18 en imágenes slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    ca-certificates \
    unixodbc \
    libgssapi-krb5-2 \
    # Descargar y registrar la llave de Microsoft
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    # Limpieza: borramos herramientas de build pero DEJAMOS las librerías de runtime
    && apt-get remove -y curl gnupg2 \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Copiar las dependencias de Python desde el Builder
COPY --from=builder /install /usr/local

# 4. Copiar el código de la aplicación
COPY . /app

# 5. Ejecutar
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]