# Usa una imagen base de Python 3.12
FROM python:3.12

# Establece el directorio de trabajo en /planetsuperheroes
WORKDIR /planetsuperheroes

# Copia el archivo .env al contenedor
COPY .env /planetsuperheroes/.env

# Copia todos los archivos al contenedor
COPY . .

# Crea el directorio de logs
RUN mkdir -p /planetsuperheroes/logs

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Ejecuta las migraciones automáticamente
RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations
RUN python manage.py migrate

# Expone el puerto de la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación con Gunicorn y especificar el archivo de log de errores
CMD ["gunicorn", "universidad.wsgi:application", "--bind", "0.0.0.0:8000", "--error-logfile", "/planetsuperheroes/logs/django_error.log"]
