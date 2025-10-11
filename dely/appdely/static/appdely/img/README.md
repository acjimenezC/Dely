Instrucciones para añadir el QR de canje

1) Guarda tu imagen QR como `qr_redeem.png` en esta carpeta.

Ruta destino dentro del repositorio:

  dely/appdely/static/appdely/img/qr_redeem.png

2) Comandos (bash) desde la raíz del proyecto:

  mkdir -p dely/appdely/static/appdely/img
  cp /ruta/local/qr_redeem.png dely/appdely/static/appdely/img/qr_redeem.png

3) En Windows PowerShell:

  New-Item -ItemType Directory -Force -Path .\dely\appdely\static\appdely\img
  Copy-Item C:\ruta\local\qr_redeem.png .\dely\appdely\static\appdely\img\qr_redeem.png

4) Si quieres que lo haga yo, pega aquí la cadena base64 del PNG y lo crearé por ti.

5) Después de copiar, en desarrollo Django la plantilla `redeem_success.html` mostrará el QR en la ruta estática.
