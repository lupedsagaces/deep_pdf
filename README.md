# Deep PDF

Este é um aplicativo para localizar conteúdo em PDF. Obs: Para que encontre o termo buscado, é necessário garantir que o PDF não seja lido como uma imagem. O robô consegue localizar apenas textos dentro do PDF. 

Tem duas funcionalidades principais:

## *Busca de Texto em PDFs*

1. Selecionar Diretório: O usuário pode selecionar um diretório contendo arquivos PDF.
2. Inserir Texto de Busca: O usuário insere o texto que deseja buscar nos PDFs.
3. Iniciar Busca: Ao clicar no botão "Buscar", o script procura o texto inserido em todos os PDFs do diretório e subdiretórios.
4. Resultados: Os PDFs que contêm o texto buscado são listados na interface, com links clicáveis para abrir a localização do arquivo.
5. Barra de Progresso: Uma barra de progresso indica o andamento da busca.
6. Contagem de Resultados: Exibe a quantidade de arquivos encontrados que contêm o texto buscado.
7. Salvar Resultados: O programa seleciona o diretório destino que o usuário escolhe para copiar os PDFs encontrados.

## *Conversão de PDFs para Pesquisáveis (OCR):*

1. Selecionar Arquivos: O usuário pode selecionar múltiplos arquivos PDF não pesquisáveis.
2. Selecionar Diretório de Saída: O usuário seleciona um diretório onde os PDFs convertidos serão salvos.
3. Conversão OCR: O script converte os PDFs não pesquisáveis para PDFs pesquisáveis usando OCR.
    Observação **IMPORTANTE**!:
    
    Para garantir que o OCR traduza o conteúdo escaneado de PDF para texto pesquisável da melhor forma possível, deve-se observar:
    * Resolução: Assegure-se de que as imagens têm alta resolução. Aumentar a resolução pode melhorar a precisão do OCR. Idealmente, use uma resolução de pelo menos 300 DPI.
    * Contraste: Garanta um bom contraste entre o texto e o fundo. Textos escuros em fundos claros são ideais.
    * Ruído: Minimize o ruído nas imagens. Imagens claras e sem manchas ou artefatos são mais fáceis para o OCR processar corretamente.

4. Barra de Progresso: Indica o andamento da conversão OCR.
5. Notificação de Conclusão: Exibe uma mensagem ao finalizar a conversão.

## Criando um ambiente de desenvolvimento para rodar o arquivo python desse projeto

1. tkinter: Normalmente vem pré-instalado com o Python em muitas distribuições, especialmente no Windows. Caso contrário, pode ser necessário instalar a partir do gerenciador de pacotes do sistema operacional.
2. tkhtmlview: Biblioteca para exibir HTML em Tkinter.
3. Pillow: Biblioteca para manipulação de imagens.
4. PyMuPDF: Interface Python para o MuPDF.
5. pytesseract: Necessário instalar o tesseract para windows disponível no seguinte link: https://github.com/UB-Mannheim/tesseract/wiki
Para linux:

```bash
pip install tkhtmlview Pillow PyMuPDF pytesseract PyPDF2
sudo apt update
sudo apt install tesseract-ocr
 ```
6. PyPDF2: Biblioteca para manipulação de PDFs.



## Comando usado para compilar no windows:
```bash
pyinstaller --windowed --onefile --icon=ico.ico deepPDF.py
```

## Comando usado para compilar no linux:

```bash
#linux
pip install pyinstaller
pyinstaller deepPDF.py --windowed --onefile
```
Compilado e testado no linux mint virginia 21.3 x86_64 . Compilado no linux mint

Compilado e testado no Windows x64. Compilado no Windows 11

