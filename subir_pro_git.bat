@echo off
echo Iniciando o Vulp-Odds para o GitHub...

:: Navega ate a pasta do projeto (ajuste se necessario)
cd /d "C:\proj\apostas\api-oddsapi.io"

:: Pega a data e hora atual para o commit
set dt=%date% %time%

echo Preparando arquivos...
git add .

echo Criando commit com data: %dt%
git commit -m "Update automatico: %dt%"

echo Subindo para o GitHub (Main)...
git push origin main --force

echo.
echo Tudo pronto! Projeto atualizado no GitHub.
echo Finalizado em: %dt%
echo.
pause