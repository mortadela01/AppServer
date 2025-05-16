Para ejecutar y configurar la aplicación son necesarios los siguientes pasos:

1. Clonar el repositorio
2. Crear la base de datos definida en ./others/SQL/BD.sql
3. Ejecutar en orden:
    3.1. python -m venv ./env
    3.2. ./env/Scripts/activate
    3.3. pip install -r requirements.txt
    3.4. python manage.py makemigrations
    3.5. python manage.py migrate
    3.6. python manage.py createsuperuser (crear con email y contraseña que recuerde)
    3.7. python manage.py runserver
4. Para configurar correctamente oauht, en el navegador se debe:
    4.1. ir a: http://127.0.0.1:8000/admin/
    4.2. ingresar el email y la constraseña ingresados al ejecutar createsuperuser
    4.3. si las credenciales son correctas, verá una interfaz, seleccone "Applications" y añada una aplicación (add aplication)
    4.4. en user ingrese la pk del superusuario creado en 2.6 (si no ha creado nuevos usuario previamente la pk es 1) 
    4.5. en client type seleccionar "Confidential"
    4.6. en authorization grant type seleccionar "Resourc owner password-passed"
    4.7. en name ingresar "Mausoleum API"
    4.8. verificar si está seleccionado "Skip authorization", si no lo está, seleccionelo
    4.9. copiar y guardar en un archivo seguro las claves client secret y client id
    4.10. guardar las configuraciones
5. Revisar las pruebas en ./others/Postman, se deben tener la siguientes consideraciones:
    5.1. en Mausoleum/SeguridadOAUTH/GJToken se debe poner las claves copiadas en 4.9.
    5.2. en Mausoleum/SeguridadOAUTH/GoogleToken se debe poner en el cuerpo un token_id generado con https://developers.google.com/oauthplayground/ (es necesario usar credenciales propia, las claves SOCIAL_AUTH_GOOGLE_OAUTH2_KEY y SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET están en ./mausoleum_server/settings.py) [solo para pruebas]