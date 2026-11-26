# Fábrica de Vídeos --- Arquivo Restrito

Aplicação desktop em desenvolvimento para apoiar a criação e a
organização de fluxos de produção audiovisual, com prioridade para
processamento local e ferramentas gratuitas.

**Repositório oficial:**\
https://github.com/contatoarquivorestrito/fabrica-de-videos-arquivo-restrito

**Branch principal:** `main`\
**Estado:** estrutura inicial versionada; desenvolvimento e validação em
andamento.

------------------------------------------------------------------------

## 1. Sobre o projeto

A **Fábrica de Vídeos** é um projeto de aplicação desktop. A proposta é
reunir, em um ambiente local, recursos e etapas de um fluxo de produção
audiovisual.

A interface está sendo desenvolvida com identidade visual *Cinematic*,
tendo um Dashboard como tela inicial planejada.

Este repositório contém somente os arquivos selecionados para
compartilhamento e controle de versão. Ele não representa uma cópia
completa de todas as pastas, ferramentas, modelos, mídias e backups
existentes no computador.

## 2. Tecnologias e arquitetura planejadas

  -----------------------------------------------------------------------
  Área                                Tecnologia ou diretriz
  ----------------------------------- -----------------------------------
  Linguagem                           Python

  Interface desktop                   PySide6

  Processamento audiovisual           FFmpeg

  Banco de dados local                SQLite

  Transcrição                         Faster-Whisper

  Execução                            Prioridade para processamento local

  Interface                           Identidade visual Cinematic;
                                      Dashboard como tela inicial
                                      planejada
  -----------------------------------------------------------------------

**Importante:** esta tabela descreve a arquitetura planejada. A presença
de uma tecnologia no planejamento não significa que sua integração
esteja concluída ou validada.

## 3. Estrutura publicada no GitHub

``` text
FABRICA_ARQUIVO_RESTRITO/
├── 01_PROGRAMA/
│   ├── app.py
│   ├── teste_pyside6.py
│   └── assets/
│       └── header_arquivo_restrito.png
├── 09_DOCUMENTACAO/
│   ├── CHANGELOG.md
│   ├── LEIA_ANTES_DE_CONTINUAR.md
│   ├── ROADMAP.md
│   └── STATUS_PROJETO.md
├── .gitignore
├── CLAUDE.md
└── README.md
```

A estrutura acima representa os arquivos publicados no repositório.
Outras pastas podem existir somente na instalação local.

## 4. Estado atual

A primeira versão do repositório foi publicada na branch `main`, com o
commit inicial:

``` text
2335802 — Initial commit - estrutura base da Fabrica de Videos
```

Arquivos publicados nessa versão:

-   Código inicial em `01_PROGRAMA/app.py`;
-   Arquivo de teste `01_PROGRAMA/teste_pyside6.py`;
-   Imagem do cabeçalho em `01_PROGRAMA/assets/`;
-   Documentação técnica em `09_DOCUMENTACAO/`;
-   Regras de trabalho em `CLAUDE.md`;
-   Regras de exclusão em `.gitignore`.

A existência desses arquivos não comprova que todas as funcionalidades
estejam implementadas. Antes de considerar qualquer recurso concluído, é
necessário executar e testar a aplicação.

Consulte os arquivos `STATUS_PROJETO.md`, `ROADMAP.md` e `CHANGELOG.md`
para acompanhar o estado documentado do desenvolvimento.

## 5. Ambiente local

O projeto está sendo trabalhado no Windows, nesta pasta:

``` text
D:\FABRICA_ARQUIVO_RESTRITO
```

O ambiente virtual Python é mantido localmente e não deve ser enviado ao
GitHub.

Com o repositório já configurado no computador, os comandos básicos para
conferir a versão local são:

``` powershell
git status
git pull origin main
```

Para executar o arquivo principal, a partir da pasta raiz do projeto,
use:

``` powershell
python .\01_PROGRAMA\app.py
```

Esse comando pressupõe que o Python e as dependências necessárias já
estejam instalados no ambiente ativo. A instalação de dependências deve
seguir as instruções técnicas atualizadas do projeto; não presuma que
todas as dependências estejam instaladas.

## 6. Fluxo de trabalho com GitHub

O VS Code e eventuais ferramentas de programação devem trabalhar nos
mesmos arquivos locais. O GitHub funciona como repositório remoto para
histórico de versões e compartilhamento dos arquivos autorizados.

Fluxo recomendado:

1.  Editar os arquivos na pasta local do projeto.

2.  Executar a aplicação e testar as alterações.

3.  Conferir os arquivos modificados:

    ``` powershell
    git status
    ```

4.  Adicionar somente os arquivos autorizados para publicação:

    ``` powershell
    git add caminho\do\arquivo
    ```

5.  Conferir o conteúdo preparado:

    ``` powershell
    git diff --cached --check
    git diff --cached --name-only
    ```

6.  Registrar a alteração:

    ``` powershell
    git commit -m "Descreva a alteração"
    ```

7.  Enviar ao GitHub:

    ``` powershell
    git push
    ```

**O GitHub não sincroniza automaticamente com a pasta local.** As
alterações só chegam ao repositório remoto depois do envio com
`git push`.

## 7. Segurança e arquivos que não devem ser publicados

Este repositório é **público**. Qualquer pessoa pode visualizar e baixar
os arquivos publicados.

Antes de cada envio, confira cuidadosamente o que será incluído. Não
publique:

-   Senhas, tokens, chaves de API ou credenciais;
-   Arquivos `.env` ou configurações com segredos;
-   Certificados, chaves privadas ou arquivos de autenticação;
-   Modelos de IA e arquivos grandes de modelos;
-   Vídeos, áudios, imagens de trabalho e outras mídias privadas;
-   Backups e arquivos compactados de uso interno;
-   Documento privado de continuidade usado para retomar conversas com
    assistentes.

O `.gitignore` ajuda a impedir a inclusão de determinados arquivos, mas
**não substitui a conferência manual antes de cada publicação**. Se um
segredo for publicado por engano, removê-lo em um commit posterior não
elimina necessariamente seu histórico; será necessário tratar a
credencial como exposta e substituí-la/revogá-la.

## 8. Orientações para ChatGPT, Claude e outros colaboradores

Antes de alterar o projeto:

1.  Ler este README.
2.  Ler `CLAUDE.md`.
3.  Consultar `09_DOCUMENTACAO/LEIA_ANTES_DE_CONTINUAR.md`.
4.  Consultar `STATUS_PROJETO.md`, `CHANGELOG.md` e `ROADMAP.md`.
5.  Verificar os arquivos reais antes de concluir que uma função existe
    ou está pronta.

Regras obrigatórias:

-   Trabalhar na pasta raiz local `D:\FABRICA_ARQUIVO_RESTRITO`, quando
    estiver usando o computador do projeto.
-   Não criar uma cópia do projeto em outra pasta sem autorização.
-   Não apagar arquivos nem substituir conteúdo sem autorização.
-   Criar backup antes de alterações importantes.
-   Não instalar ferramentas nem modificar configurações sem
    autorização.
-   Explicar os procedimentos em português brasileiro, de forma simples
    e uma etapa por vez.
-   Não declarar funcionalidades como concluídas sem testes.
-   Ao finalizar uma etapa, atualizar `STATUS_PROJETO.md`,
    `CHANGELOG.md`, `ROADMAP.md` e `LEIA_ANTES_DE_CONTINUAR.md`,
    conforme aplicável.
-   Preparar um arquivo privado de continuidade para o usuário guardar
    fora do repositório, quando solicitado.

### Continuidade entre conversas

Para iniciar um novo chat, o usuário poderá fornecer:

-   O link público deste repositório;
-   O arquivo privado de continuidade mais recente.

O arquivo privado de continuidade não deve ser adicionado ao repositório
público. Se algum arquivo local não publicado for necessário para uma
tarefa, o usuário deverá anexá-lo diretamente à conversa.

------------------------------------------------------------------------

## 9. Princípio de desenvolvimento

Preservar o trabalho existente, avançar em etapas pequenas e
verificáveis e manter o usuário informado antes de mudanças importantes.

**A prioridade é construir uma aplicação funcional, estável e validada
--- não apenas acumular arquivos ou marcar tarefas como concluídas.**
