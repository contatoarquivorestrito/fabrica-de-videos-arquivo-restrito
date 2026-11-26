
# CLAUDE.md
# FABRICA DE VIDEOS — ARQUIVO RESTRITO

## 1. REGRA PRINCIPAL

Trabalhar exclusivamente na pasta raiz local do projeto.

O VS Code e o Claude Code devem trabalhar nos mesmos
arquivos locais.

O GitHub e o repositorio central para armazenar codigo,
documentacao tecnica autorizada e historico de versoes.

O projeto deve continuar funcionando localmente no Windows.

Nao criar outro projeto em outra pasta.
Nao apagar arquivos sem autorizacao.

## 2. DOCUMENTACAO OBRIGATORIA

Antes de trabalhar, consultar:

- 09_DOCUMENTACAO\STATUS_PROJETO.md
- 09_DOCUMENTACAO\CHANGELOG.md
- 09_DOCUMENTACAO\ROADMAP.md
- 09_DOCUMENTACAO\LEIA_ANTES_DE_CONTINUAR.md

O Documento Mestre e de Continuidade GPT fica fora
do repositorio, em pasta separada no computador.

Quando o usuario fornecer esse documento, ler integralmente
antes de continuar o desenvolvimento.

## 3. GITHUB E CONTROLE DE VERSAO

O repositorio GitHub e publico.

Publicar somente arquivos revisados e autorizados.

Antes de enviar alteracoes:
- Conferir os arquivos modificados.
- Verificar se nao existem credenciais.
- Verificar se nao existem arquivos pesados.
- Conferir o git status.

Nunca enviar:
- Senhas e tokens.
- Chaves de API.
- Arquivos .env com credenciais.
- Ambientes virtuais.
- Modelos pesados de IA.
- Videos, audios e midias privadas.
- Backups ZIP.
- Projetos pessoais e exportacoes.

Nunca executar commit ou push sem autorizacao
do usuario.

Nunca executar force push.

O GitHub nao sincroniza automaticamente.
As alteracoes locais precisam ser revisadas e enviadas.

## 4. PRESERVACAO

- Nunca apagar arquivos sem autorizacao.
- Nunca substituir arquivos sem backup.
- Preservar mockups e referencias originais.
- Preservar decisoes aprovadas pelo usuario.
- Nao declarar funcionalidades como prontas sem testes.
- Trabalhar de maneira nao destrutiva.

## 5. DESENVOLVIMENTO

Arquitetura de referencia:

- Python: logica da aplicacao.
- PySide6: interface desktop.
- FFmpeg: processamento audiovisual.
- SQLite: armazenamento local.
- Faster-Whisper: transcricao.

Identidade visual: Cinematic.

Tela inicial: Dashboard.

Priorizar processamento local e ferramentas gratuitas.

Nao presumir que ferramentas ou funcionalidades estao
instaladas ou implementadas sem verificacao.

## 6. DOCUMENTACAO E HISTORICO

Ao final de cada etapa aprovada, atualizar:

- STATUS_PROJETO.md
- CHANGELOG.md
- ROADMAP.md
- LEIA_ANTES_DE_CONTINUAR.md

Registrar:
- Arquivos criados e modificados.
- Funcionalidades implementadas.
- Testes realizados e resultados.
- Problemas encontrados.
- Pendencias.
- Proxima tarefa.

Manter o historico tecnico atualizado.

## 7. BACKUPS

Antes de alteracoes importantes:

- Criar copia de seguranca.
- Guardar em 08_BACKUPS.
- Nunca apagar backups anteriores sem autorizacao.

Backups permanecem locais e nao devem ser publicados
no GitHub.

Nao gerar ZIP de toda a pasta como procedimento obrigatorio
de continuidade entre chats.

## 8. COMPORTAMENTO

O usuario nao e programador.

Explicar cada procedimento em portugues brasileiro,
com instrucoes simples e uma etapa por vez.

Nao instalar ferramentas, modificar configuracoes
ou executar operacoes destrutivas sem autorizacao.

Sempre explicar o que sera alterado antes de executar
uma tarefa importante.

## 9. ESTADO ATUAL DO PROJETO

- Estrutura local do projeto existente.
- Git inicializado.
- Repositorio remoto configurado.
- Primeiro envio ao GitHub ainda pendente.
- app.py existente.
- teste_pyside6.py existente.
- Recursos visuais em 01_PROGRAMA\assets.
- Documentacao tecnica em 09_DOCUMENTACAO.
- Ambiente virtual Python mantido localmente.
- Documento de continuidade GPT mantido fora do repositorio.

A existencia dos arquivos nao significa que todas
as funcionalidades estejam implementadas.

Verificar e testar antes de declarar qualquer recurso
como concluido.
