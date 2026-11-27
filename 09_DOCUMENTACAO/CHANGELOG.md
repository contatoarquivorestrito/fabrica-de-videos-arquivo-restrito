# CHANGELOG — FABRICA DE VIDEOS

Este arquivo registra alterações efetivamente realizadas ou decisões formalmente atualizadas. Não registrar tarefas apenas planejadas como concluídas.

## 26/11/2026 — GitHub e organização do projeto

- Repositório público criado e configurado como remoto `origin`.
- Branch principal local padronizada como `main`.
- Primeiro commit local criado: `2335802` — `Initial commit - estrutura base da Fabrica de Videos`.
- Primeiro envio para o GitHub concluído.
- `README.md` criado, adicionado à raiz do projeto e enviado ao GitHub.
- Última conferência relatada: `git status` indicou `main` sincronizada com `origin/main` e árvore de trabalho limpa.
- Definido o GitHub como repositório central de código e documentação técnica autorizada.
- Revogada a decisão antiga de não utilizar GitHub.
- Documento privado de continuidade GPT mantido fora do repositório público.
- Definido que somente arquivos selecionados e revisados serão publicados.

## 26/11/2026 — Auditoria do código existente

- Examinado o conteúdo de `01_PROGRAMA/app.py`.
- Identificadas as classes `Card`, `RecordingPage`, `PlaceholderPage` e `MainWindow`.
- Identificados cabeçalho com imagem, menu lateral com oito opções, área central de páginas e rodapé.
- Confirmado que o menu Gravação utiliza uma estrutura visual própria.
- Confirmado que as outras opções do menu utilizam páginas provisórias (`PlaceholderPage`) no código examinado.
- Identificada a seleção inicial da página Gravação (`self.change_page(2)`).
- Examinado `01_PROGRAMA/teste_pyside6.py`, que contém um teste visual simples de abertura de janela.
- Leitura de `app.py` com `Get-Content -Encoding utf8` exibiu corretamente os caracteres acentuados.
- Não foi registrado teste funcional completo nem integração real de câmera, microfone, gravação ou IA.

## 25/11/2026 — Registros históricos da preparação

- Definida a pasta principal local: `D:\FABRICA_ARQUIVO_RESTRITO`.
- Definidos o nome do projeto, a identidade visual Cinematic e o Dashboard como tela inicial desejada.
- Definida a arquitetura de referência: Python + PySide6, FFmpeg, SQLite e Faster-Whisper.
- Preparada a estrutura inicial de documentação.
- Decisões históricas desta data devem ser interpretadas à luz das atualizações posteriores. Em particular, a decisão antiga de não utilizar GitHub foi revogada em 26/11/2026.

## DECISÕES VISUAIS E DE PRESERVAÇÃO

- Home/Dashboard é a tela inicial desejada.
- Identidade visual: Cinematic.
- Preservar mockups e referências originais fornecidos pelo usuário.
- Não substituir referências aprovadas por interfaces genéricas sem autorização.
- Não declarar uma tela ou funcionalidade como pronta sem implementação e validação.

## PRÓXIMAS ALTERAÇÕES

Registrar novas alterações com data, arquivos envolvidos, descrição e resultado dos testes.
Não registrar tarefas apenas planejadas como concluídas.
