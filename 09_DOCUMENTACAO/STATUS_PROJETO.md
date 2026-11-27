# FABRICA DE VIDEOS — ARQUIVO RESTRITO
# STATUS OFICIAL DO PROJETO

Atualizado em: 26/11/2026

## 1. ESTADO ATUAL

Fase: fundação técnica, documentação e estrutura inicial da interface.

- Aplicação desktop para Windows.
- Nome: Fábrica de Vídeos — Arquivo Restrito.
- Pasta principal local: `D:\FABRICA_ARQUIVO_RESTRITO`.
- Linguagem utilizada no código existente: Python.
- Interface utilizada no código existente: PySide6.
- Identidade visual definida: Cinematic.
- Tela inicial planejada: Dashboard.
- Repositório oficial: GitHub público.
- Branch principal: `main`.
- Repositório: https://github.com/contatoarquivorestrito/fabrica-de-videos-arquivo-restrito
- VS Code é utilizado para editar e executar os arquivos locais.
- O ambiente virtual Python permanece no computador e não é publicado.
- Claude Code está previsto como ferramenta auxiliar, mas ainda não foi confirmado como instalado ou configurado.

O GitHub contém somente os arquivos selecionados para publicação. Ele não é uma cópia integral das pastas, ferramentas, modelos, mídias e backups locais.

## 2. ESTADO DO CONTROLE DE VERSÃO

- Git inicializado localmente.
- Repositório remoto `origin` configurado.
- Branch local principal: `main`.
- Primeiro commit criado: `2335802` — `Initial commit - estrutura base da Fabrica de Videos`.
- Primeiro envio ao GitHub realizado com sucesso.
- `README.md` adicionado e enviado posteriormente.
- Última conferência relatada: `git status` indicou branch `main` atualizada com `origin/main` e árvore de trabalho limpa.
- Repositório público: qualquer pessoa pode visualizar e baixar os arquivos publicados.

Arquivos rastreados na última conferência:

- `.gitignore`
- `01_PROGRAMA/app.py`
- `01_PROGRAMA/assets/header_arquivo_restrito.png`
- `01_PROGRAMA/teste_pyside6.py`
- `09_DOCUMENTACAO/CHANGELOG.md`
- `09_DOCUMENTACAO/LEIA_ANTES_DE_CONTINUAR.md`
- `09_DOCUMENTACAO/ROADMAP.md`
- `09_DOCUMENTACAO/STATUS_PROJETO.md`
- `CLAUDE.md`
- `README.md`

A lista deve ser conferida com `git ls-files` se houver dúvida sobre o estado atual.

## 3. CÓDIGO EXISTENTE E AUDITADO

### 3.1 Arquivo principal

Arquivo: `01_PROGRAMA/app.py`

O código examinado contém:

- Classe `Card` para organizar cartões da interface.
- Classe `RecordingPage` com estrutura visual do Estúdio de Gravação.
- Classe `PlaceholderPage` para páginas ainda sem implementação específica.
- Classe `MainWindow` para a janela principal.
- Cabeçalho que carrega `01_PROGRAMA/assets/header_arquivo_restrito.png`.
- Menu lateral com oito opções.
- Área central baseada em `QStackedWidget`.
- Rodapé de status.
- Folha de estilos com identidade visual escura e detalhes em vermelho.

### 3.2 Menu identificado no código

1. Home.
2. Biblioteca de Histórias.
3. Gravação.
4. Edição Automática.
5. Cortes (Reels/Shorts).
6. Microdocumentários.
7. Projetos.
8. Configurações.

No código examinado, somente a opção Gravação cria uma `RecordingPage`. As demais opções criam `PlaceholderPage`, ou seja, páginas provisórias.

O código chama `self.change_page(2)` ao iniciar a janela. Portanto, a tela selecionada inicialmente é Gravação, não Home/Dashboard. Isso deverá ser ajustado quando o Dashboard for implementado e aprovado.

### 3.3 Estúdio de Gravação

O código contém elementos visuais para:

- Pré-visualização de câmera com mensagem de espera.
- Indicador visual de áudio.
- Área de histórias da sessão.
- Botões de etapas: Início, Relato 1, Relato 2, Adicionar Relato e Final.
- Área de leitura assistida.
- Área de monitoramento da narração por IA.
- Botões Iniciar Gravação, Pausar e Encerrar Sessão.

Esses elementos comprovam a existência de uma estrutura visual no código, mas não comprovam integração funcional com câmera, microfone, gravação, teleprompter ou inteligência artificial. As ações dos botões e as integrações reais ainda precisam ser implementadas e testadas.

### 3.4 Arquivo de teste

Arquivo: `01_PROGRAMA/teste_pyside6.py`

O arquivo contém um teste visual simples que cria uma janela PySide6 com título e textos. Não é uma suíte automatizada abrangente e não valida as funcionalidades da aplicação principal.

## 4. TESTES E VALIDAÇÕES

- O conteúdo de `app.py` foi consultado usando leitura UTF-8.
- A leitura com `Get-Content -Encoding utf8` exibiu corretamente caracteres acentuados. A exibição incorreta anterior ocorreu na leitura padrão do PowerShell; não há evidência suficiente para afirmar que o arquivo precise de conversão.
- Não há, neste registro, comprovação de teste funcional completo da aplicação.
- Não há comprovação de integração real com câmera, microfone, FFmpeg, SQLite ou Faster-Whisper.
- Não declarar funcionalidades como concluídas sem executar e registrar testes reais.

## 5. DECISÕES APROVADAS E ATUAIS

- Aplicação desktop para Windows.
- Nome: Fábrica de Vídeos — Arquivo Restrito.
- Identidade visual: Cinematic.
- Dashboard como tela inicial desejada.
- Python + PySide6 como base da aplicação.
- Processamento local como prioridade.
- FFmpeg previsto para processamento audiovisual.
- SQLite previsto para armazenamento local.
- Faster-Whisper previsto para transcrição.
- GitHub público como repositório central do código e documentação técnica autorizada.
- VS Code como ambiente local de edição e execução.
- ChatGPT para planejamento, análise, revisão e preparação de código.
- Claude Code como ferramenta auxiliar futura, quando instalado/configurado e quando seu uso for conveniente.
- Backups completos, modelos de IA, mídias, arquivos privados e ambiente virtual permanecem locais.
- Documento Mestre/Documento de Continuidade GPT fica fora do repositório público e é fornecido pelo usuário ao iniciar uma nova conversa, quando necessário.

A antiga decisão “Sem GitHub” está REVOGADA e não deve ser seguida.

## 6. ORGANIZAÇÃO DOS ARQUIVOS

### Publicados no GitHub
Somente arquivos selecionados, revisados e autorizados, como código-fonte, documentação técnica e recursos leves necessários à aplicação.

### Mantidos localmente
- Ambiente virtual `.venv`.
- Ferramentas e instalações locais.
- Modelos de inteligência artificial.
- Vídeos, áudios e mídias de produção.
- Projetos, exportações e arquivos temporários.
- Backups ZIP.
- Documento privado de continuidade GPT.
- Credenciais, tokens, senhas e arquivos `.env`.

O `.gitignore` contém regras para excluir ambientes virtuais, segredos, modelos pesados, arquivos compactados e pastas locais específicas. Mesmo com essas regras, revisar sempre `git status` e `git diff --cached --name-only` antes de publicar.

## 7. PRÓXIMAS ETAPAS PRIORITÁRIAS

1. Atualizar e publicar esta documentação corrigida.
2. Executar `app.py` no ambiente local e registrar o resultado.
3. Executar `teste_pyside6.py` e registrar o resultado.
4. Verificar visualmente o cabeçalho, menu, navegação e Estúdio de Gravação.
5. Confirmar dependências instaladas e versões do Python/PySide6.
6. Verificar ambiente Windows, hardware, GPU, drivers e espaço em disco, se ainda necessário.
7. Definir e implementar o Dashboard Cinematic, respeitando as referências visuais aprovadas.
8. Desenvolver os módulos gradualmente, com aprovação do usuário e testes por etapa.

## 8. REGRA DE CONFIABILIDADE

Distinguir sempre:
- Planejado.
- Código existente.
- Interface visual provisória.
- Implementado.
- Testado.
- Aprovado pelo usuário.

Não transformar uma tarefa planejada em funcionalidade concluída apenas porque existe um botão, rótulo ou tela provisória.
