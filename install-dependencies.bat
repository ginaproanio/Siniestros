@echo off
echo Instalando dependencias del backend...
cd backend
pip install -r ../requirements.txt
cd ..

echo Instalando dependencias del frontend...
cd frontend
npm install
cd ..

echo Todas las dependencias han sido instaladas.
echo Las alertas en VS Code deberían desaparecer ahora.
pause
