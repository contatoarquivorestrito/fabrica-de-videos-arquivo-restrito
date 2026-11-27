# LEIA ANTES DE CONTINUAR
# FABRICA DE VIDEOS — ARQUIVO RESTRITO

Você está continuando um projeto existente de aplicação desktop para Windows chamado **Fábrica de Vídeos — Arquivo Restrito**.

## 1. REPOSITÓRIO OFICIAL

GitHub público:
https://github.com/contatoarquivorestrito/fabrica-de-videos-arquivo-restrito

Branch principal: `main`.

O repositório é público. Qualquer pessoa pode visualizar e baixar os arquivos publicados. Nunca presumir que o GitHub contém a cópia integral do computador do usuário.

A antiga decisão “Sem GitHub” foi REVOGADA. O GitHub é o repositório central do código e da documentação técnica autorizada.

## 2. PRIMEIRO PASSO EM UM NOVO CHAT

Leia, nesta ordem:

1. `README.md`.
2. `CLAUDE.md`.
3. `09_DOCUMENTACAO/LEIA_ANTES_DE_CONTINUAR.md`.
4. `09_DOCUMENTACAO/STATUS_PROJETO.md`.
5. `09_DOCUMENTACAO/CHANGELOG.md`.
6. `09_DOCUMENTACAO/ROADMAP.md`.

O usuário poderá anexar um Documento Mestre/Documento de Continuidade privado. Quando fornecido, leia-o integralmente. Esse documento fica fora do repositório público e não deve ser solicitado para publicação no GitHub.

Examine os arquivos reais antes de afirmar que uma funcionalidade existe ou está concluída.

## 3. ESTADO TÉCNICO CONHECIDO

- Aplicação desktop planejada para Windows.
- Python e PySide6 aparecem no código existente.
- `01_PROGRAMA/app.py` contém `Card`, `RecordingPage`, `PlaceholderPage` e `MainWindow`.
- O código examinado contém cabeçalho com imagem, menu lateral com oito opções, rodapé e uma estrutura visual do Estúdio de Gravação.
- O menu Gravação usa `RecordingPage`; as outras opções examinadas usam `PlaceholderPage`.
- A aplicação seleciona inicialmente a página de Gravação por meio de `self.change_page(2)`.
- `01_PROGRAMA/teste_pyside6.py` contém um teste visual simples de janela.
- Não há comprovação registrada de teste funcional completo.
- Não há comprovação registrada de integração real com câmera, microfone, gravação, teleprompter ou IA.
- FFmpeg, SQLite e Faster-Whisper são tecnologias previstas; não presumir integração concluída.
- O código de `app.py` foi lido corretamente em UTF-8 com `Get-Content -Encoding utf8`.

Use `STATUS_PROJETO.md` e `ROADMAP.md` para o estado mais atualizado. Não transforme estruturas visuais em funcionalidades concluídas.

## 4. ORGANIZAÇÃO E FERRAMENTAS

- Pasta local conhecida: `D:\FABRICA_ARQUIVO_RESTRITO`.
- VS Code: ambiente local de edição e execução.
- Git: controle de versões local.
- GitHub: repositório remoto público.
- ChatGPT: planejamento, análise, revisão, documentação e preparação de código.
- Claude Code: ferramenta auxiliar prevista; o usuário ainda não confirmou assinatura, instalação ou configuração. Não presumir que esteja disponível.

O projeto deve continuar executável localmente no Windows. O GitHub não executa a aplicação desktop.

## 5. FLUXO DE TRABALHO COM GIT

O VS Code e as ferramentas de programação devem trabalhar nos mesmos arquivos locais.

Fluxo recomendado:

1. Editar e salvar os arquivos localmente.
2. Executar a aplicação e testar.
3. Conferir alterações com `git status`.
4. Adicionar somente arquivos revisados e autorizados com `git add`.
5. Conferir a seleção com `git diff --cached --name-only`.
6. Conferir formatação com `git diff --cached --check`.
7. Criar commit com mensagem descritiva.
8. Enviar ao GitHub com `git push`.

Para obter atualizações publicadas remotamente, usar `git pull` após verificar que não há alterações locais conflitantes.

O GitHub não sincroniza automaticamente com a pasta local. Não executar `commit`, `push`, `pull`, rebase ou operações destrutivas sem explicar o efeito e obter autorização do usuário quando a ação não tiver sido previamente autorizada.

## 6. SEGURANÇA — REPOSITÓRIO PÚBLICO

Nunca publicar:

- Senhas, tokens, chaves de API ou credenciais.
- Arquivos `.env` com segredos.
- Certificados ou chaves privadas.
- Documento privado de continuidade GPT.
- Backups ZIP completos.
- Modelos pesados de IA.
- Vídeos, áudios e mídias privadas.
- Arquivos pessoais ou dados sensíveis.

O `.gitignore` ajuda, mas não substitui a revisão manual de cada envio. Conferir `git status` e `git diff --cached --name-only` antes de publicar. Se uma credencial for publicada, tratá-la como exposta e substituí-la/revogá-la; apagar em commit posterior não basta.

Arquivos locais não publicados podem ser anexados pelo usuário diretamente à conversa quando necessários.

## 7. REGRAS DE DESENVOLVIMENTO

1. Trabalhar na pasta local existente, quando houver acesso ao computador do usuário.
2. Não criar outro projeto em outra pasta sem autorização.
3. Não apagar arquivos sem autorização.
4. Não substituir arquivos importantes sem backup.
5. Preservar mockups e referências originais aprovados pelo usuário.
6. Não alterar decisões aprovadas sem autorização.
7. Não instalar ferramentas nem modificar configurações sem autorização.
8. Explicar procedimentos em português brasileiro, de forma simples e uma etapa por vez.
9. Não declarar funcionalidades como prontas sem implementação e testes reais.
10. Distinguir claramente código existente, interface provisória, funcionalidade implementada, testada e aprovada.

## 8. DOCUMENTAÇÃO AO FINAL DE CADA ETAPA

Atualizar, conforme aplicável:

- `STATUS_PROJETO.md`.
- `CHANGELOG.md`.
- `ROADMAP.md`.
- `LEIA_ANTES_DE_CONTINUAR.md`.

Registrar arquivos criados/modificados, decisões, testes e resultados, problemas encontrados e próxima tarefa exata.

Quando o usuário encerrar uma conversa e solicitar, preparar um Documento de Continuidade privado para ser guardado fora do repositório público. Incluir o link do GitHub e instruções para o próximo chat. Não colocar esse documento privado no repositório.

## 9. FORMA DE TRABALHO COM O USUÁRIO

O usuário não é programador. Orientar com comandos completos, explicar onde colar e pedir um resultado por vez. Evitar instruções que dependam de conhecimento técnico não explicado.

Priorizar segurança, preservação do projeto, pequenas etapas verificáveis e aprovação do usuário antes de alterações importantes.
