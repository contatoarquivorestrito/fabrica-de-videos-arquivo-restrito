# ROADMAP — FABRICA DE VIDEOS

Este roadmap distingue preparação, código existente, implementação funcional e validação. Marcar uma tarefa como concluída somente quando houver evidência suficiente.

## FASE 0 — REPOSITÓRIO E DOCUMENTAÇÃO

- [x] Inicializar Git na pasta local.
- [x] Configurar o repositório remoto do GitHub.
- [x] Padronizar a branch principal como `main`.
- [x] Criar o primeiro commit.
- [x] Publicar a estrutura inicial no GitHub público.
- [x] Criar e publicar o `README.md`.
- [x] Definir o documento privado de continuidade fora do repositório público.
- [ ] Publicar a documentação técnica corrigida desta atualização.
- [ ] Conferir periodicamente se o repositório contém somente arquivos autorizados.

## FASE 1 — AMBIENTE E VALIDAÇÃO INICIAL

- [ ] Verificar versão do Windows e características do hardware.
- [ ] Confirmar versão do Python e ambiente virtual utilizado.
- [ ] Confirmar versão e funcionamento do PySide6.
- [ ] Executar `01_PROGRAMA/teste_pyside6.py` e registrar o resultado.
- [ ] Executar `01_PROGRAMA/app.py` e registrar o resultado.
- [ ] Verificar carregamento da imagem do cabeçalho.
- [ ] Verificar navegação entre as oito opções do menu.
- [ ] Confirmar FFmpeg e sua versão, quando instalado.
- [ ] Verificar disponibilidade de SQLite no ambiente Python.
- [ ] Confirmar situação do Faster-Whisper e seus requisitos.
- [ ] Verificar GPU, drivers e espaço em disco, se ainda necessário.

## FASE 2 — INTERFACE CINEMATIC

Código visual inicial já identificado em `app.py`:
- [x] Estrutura de janela principal (`MainWindow`) presente no código.
- [x] Cabeçalho com carregamento de imagem presente no código.
- [x] Menu lateral com oito opções presente no código.
- [x] Estrutura visual inicial do Estúdio de Gravação presente no código.
- [ ] Validar visualmente a interface em execução.
- [ ] Implementar Dashboard Cinematic como tela inicial.
- [ ] Definir e aprovar navegação e estados visuais.
- [ ] Implementar Biblioteca de Histórias.
- [ ] Implementar Novo Projeto e Meus Projetos.
- [ ] Implementar Relatos em Sequência.
- [ ] Finalizar Criar Episódio conforme referências aprovadas.
- [ ] Implementar Configurações.
- [ ] Implementar telas de Edição Automática, Cortes e Microdocumentários.

As opções que atualmente usam `PlaceholderPage` não devem ser consideradas telas funcionais.

## FASE 3 — ESTÚDIO DE GRAVAÇÃO

- [ ] Integrar câmera e pré-visualização real.
- [ ] Integrar microfone e seleção de dispositivo.
- [ ] Implementar medidor de áudio real.
- [ ] Implementar gravação, pausa e encerramento.
- [ ] Implementar organização de etapas e relatos.
- [ ] Implementar teleprompter.
- [ ] Implementar leitura assistida.
- [ ] Testar salvamento e recuperação das gravações.

## FASE 4 — INTELIGÊNCIA DE NARRAÇÃO

- [ ] Integrar transcrição.
- [ ] Acompanhar palavras durante a leitura.
- [ ] Detectar erros e releituras.
- [ ] Selecionar melhores tentativas.
- [ ] Implementar harmonização, quando especificada.
- [ ] Implementar tratamento de voz.
- [ ] Classificar pausas.
- [ ] Validar resultados com gravações reais.

## FASE 5 — PRODUÇÃO AUDIOVISUAL

- [ ] Definir modelos de produção.
- [ ] Implementar montagem automática.
- [ ] Implementar editor manual.
- [ ] Integrar processamento audiovisual com FFmpeg.
- [ ] Implementar renderização.
- [ ] Implementar exportação.
- [ ] Testar formatos e qualidade dos arquivos gerados.

## FASE 6 — CONTEÚDO VERTICAL

- [ ] Implementar fluxo para Reels.
- [ ] Implementar fluxo para Shorts.
- [ ] Implementar cortes automáticos.
- [ ] Criar e validar templates verticais.

## FASE 7 — FINALIZAÇÃO E DISTRIBUIÇÃO

- [ ] Executar testes completos.
- [ ] Corrigir erros identificados.
- [ ] Testar backup e recuperação local.
- [ ] Preparar instalador Windows.
- [ ] Validar instalação em ambiente limpo.
- [ ] Documentar procedimento de atualização.

## REGRA DE ATUALIZAÇÃO

Todos os itens futuros permanecem pendentes até implementação e validação. A existência de elementos visuais, botões ou rótulos não comprova que uma funcionalidade esteja operacional.
