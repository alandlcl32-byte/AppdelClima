WeatherApp - Instrucciones rápidas

1) Reemplaza la API key en main.py: API_KEY = "TU_OPENWEATHERMAP_API_KEY_AQUI"
   Obtén la API key en https://openweathermap.org/

2) Ejecutar en Windows (ejecutar en terminal):
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python main.py

3) Generar APK en Google Colab (usa la celda que te proporciono en el asistente):
   - Monta tu Drive y coloca esta carpeta en MyDrive/WeatherApp
   - Ejecuta buildozer en Colab para compilar el APK

4) Emulador Android (opcional):
   - BlueStacks: instala y arrastra el APK para instalar
   - Android Studio: crea un virtual device e instala el APK con adb install

5) Si tienes dudas, copia el error y pégalo al asistente para que lo revisemos.
