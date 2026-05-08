\# Bolão Copa 2026 — Documento Oficial de Escopo e Arquitetura (V1)



\## Objetivo do Projeto



Desenvolver um sistema web responsivo para gerenciamento de um bolão da Copa do Mundo 2026, voltado para uso entre amigos e familiares.



O sistema deverá permitir:

\- cadastro de participantes

\- envio de palpites

\- lançamento de resultados

\- cálculo automático de pontuação

\- ranking em tempo real

\- administração simplificada



A prioridade do projeto é:

\- simplicidade

\- estabilidade

\- facilidade de uso no celular

\- manutenção simples

\- desenvolvimento incremental



\---



\# Escopo Oficial da V1



\## Incluído na V1



\- Sistema web responsivo

\- Login simples

\- Cadastro manual de participantes

\- Cadastro/importação de jogos

\- Palpites por partida

\- Edição de palpites até início do jogo

\- Bloqueio automático

\- Resultados lançados manualmente

\- Pontuação automática

\- Ranking geral

\- Estatísticas individuais

\- Painel administrativo

\- Funcionamento mobile-first



\---



\## Não incluído na V1



\- Aplicativo Android/iOS nativo

\- APIs externas

\- Integração automática de resultados

\- Chat

\- Notificações

\- Múltiplos bolões

\- Grupos privados

\- Gamificação avançada

\- Modo escuro

\- Sistema de recuperação de senha

\- Cadastro público

\- Logs administrativos

\- Cache de ranking

\- JWT

\- Frontend SPA

\- React/Vue



\---



\# Plataforma



\## Tipo

Sistema web responsivo acessado pelo navegador.



\## Estratégia

Mobile-first.



\---



\# Stack Oficial



\## Backend

\- Python

\- Flask

\- Flask-SQLAlchemy

\- Flask-Migrate



\## Frontend

\- Jinja Templates

\- Bootstrap 5

\- Bootstrap Icons



\## Banco de Dados

\- SQLite



\## Sessão

\- Flask Session



\## Configuração

\- python-dotenv



\---



\# Arquitetura Oficial



\## Padrão

App Factory Pattern.



\---



\# Estrutura Oficial do Projeto



```text

bolao\_copa/

├── app/

│   ├── \_\_init\_\_.py

│   ├── extensions.py

│   │

│   ├── models/

│   │   ├── base\_model.py

│   │   ├── participant.py

│   │   ├── tournament.py

│   │   ├── team.py

│   │   ├── match.py

│   │   └── prediction.py

│   │

│   ├── repositories/

│   │

│   ├── services/

│   │

│   ├── routes/

│   │   ├── auth\_routes.py

│   │   ├── home\_routes.py

│   │   ├── prediction\_routes.py

│   │   ├── ranking\_routes.py

│   │   └── admin\_routes.py

│   │

│   ├── templates/

│   │   ├── auth/

│   │   ├── home/

│   │   ├── predictions/

│   │   ├── ranking/

│   │   ├── admin/

│   │   └── shared/

│   │

│   ├── static/

│   │   ├── css/

│   │   ├── js/

│   │   └── img/

│   │

│   └── utils/

│

├── instance/

│   └── bolao.db

│

├── migrations/

│

├── config.py

├── run.py

└── requirements.txt



Usuários

ADMIN



Responsável pela administração do sistema.



Permissões:



cadastrar participantes

editar participantes

ativar/desativar participantes

cadastrar partidas

importar jogos

lançar resultados

editar resultados

USER



Participante comum do bolão.



Permissões:



fazer login

visualizar jogos

enviar palpites

editar palpites até fechamento

visualizar ranking

visualizar estatísticas

Sistema de Login

Modelo

nome de usuário

senha simples

Segurança

senha armazenada apenas como hash

Werkzeug Security

Sessão



Dados mínimos:



session\["participant\_id"]

session\["role"]

Navegação Principal

Menu inferior mobile

🏠 Home

📝 Palpites

🏆 Ranking

👤 Perfil

Estrutura das Telas

Usuário

Login

usuário

senha

botão entrar

Home

posição no ranking

pontuação

próximos jogos

status dos palpites

Palpites

jogos agrupados por data

múltiplos jogos na mesma tela

salvar em lote

Ranking

ranking geral

destaque do usuário logado

Resultados

placares reais

pontos obtidos

Meu Desempenho

pontos totais

placares exatos

vencedores corretos

total de palpites

aproveitamento

Admin

Dashboard

atalhos administrativos

Participantes

listar

ativar/desativar

alterar senha

Partidas

cadastrar

editar

Resultados

lançar resultados

Importação

importar jogos via JSON

Regras Oficiais do Bolão

Palpites

1 palpite por usuário por jogo

edição permitida até início da partida

fechamento automático

palpites ocultos até fechamento

Organização dos Jogos



Exibição por data.



Exemplo:



12/06/2026



Brasil x Japão

França x EUA

Mata-mata



Considerar apenas:



placar dos 90 minutos



Ignorar:



prorrogação

pênaltis

Pontuação Oficial

Situação	Pontos

Placar exato	5

Acertou vencedor/empate	3

Acertou gols de um lado	1

Errou tudo	0

Ranking

Características

ranking geral

atualização automática

cálculo dinâmico

Critérios de Desempate

Mais placares exatos

Mais vencedores corretos

Menos erros

Empate mantido

Banco de Dados

participants

id

name

password\_hash

role

active

created\_at

tournaments

id

name

year

active

created\_at

teams

id

name

group

active

created\_at

matches

id

tournament\_id

phase

team\_home\_id

team\_away\_id

match\_datetime

home\_goals

away\_goals

created\_at

predictions

id

participant\_id

match\_id

home\_goals

away\_goals

points

created\_at

updated\_at

Convenções Oficiais

Nomenclatura Python

snake\_case

Classes

PascalCase

Constantes

UPPER\_CASE

Rotas

inglês

Interface

português

Convenções de Desenvolvimento

Regras obrigatórias

Um passo por vez

Testar antes de avançar

Reescrever arquivos completos

Mobile-first

Sem lógica nas rotas

Simplicidade acima de tudo

Responsabilidades por Camada

routes

recebem requisições

renderizam templates

chamam services

services

regras de negócio

repositories

acesso ao banco

models

entidades SQLAlchemy

Estratégia de Banco

IDs

Integer autoincrement

Exclusão

lógica via active=True/False

Status da partida



NÃO armazenado no banco.



Será derivado automaticamente:



OPEN

CLOSED

FINISHED

Configurações Oficiais

Timezone



America/Sao\_Paulo



Banco SQLite

instance/bolao.db

Variáveis de ambiente



Arquivo .env



Dependências Oficiais

Flask

Flask-SQLAlchemy

Flask-Migrate

python-dotenv

Estratégia Oficial de Desenvolvimento

Ordem de implementação

Fase 1



Estrutura base Flask



Fase 2



Configuração SQLAlchemy + Migrate



Fase 3



Models



Fase 4



Autenticação



Fase 5



Painel Admin



Fase 6



Palpites



Fase 7



Resultados e pontuação



Fase 8



Ranking



Fase 9



Refinamento visual mobile



Diretriz Principal do Projeto



O projeto deve priorizar:



simplicidade

clareza

estabilidade

facilidade de uso

baixo acoplamento

manutenção simples



Evitar complexidade desnecessária é uma regra oficial do projeto.

