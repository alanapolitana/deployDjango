# Usa una imagen base de Python 3.12
FROM python:3.12

# Establece el directorio de trabajo en /planetsuperheroes
WORKDIR /planetsuperheroes

# Copia todos los archivos al contenedor
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto de la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "universidad.wsgi:application", "--bind", "0.0.0.0:8000"]
