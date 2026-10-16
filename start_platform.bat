@echo off
echo ========================================================
echo Lancement de la Plateforme Arbitrage E-Commerce V1
echo ========================================================

docker-compose up -d

echo.
echo Plateforme V1 demarree avec succes !
echo - Dashboard Streamlit V1 : http://localhost:8502
echo - Airflow Webserver V1    : http://localhost:8086
echo - Spark Master UI V1     : http://localhost:8082
echo ========================================================
pause
