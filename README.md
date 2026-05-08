# Bolão Copa 2026

Sistema web para bolão da Copa do Mundo FIFA 2026.

## Funcionalidades

- **Cadastro de participantes**: Cada pessoa cria seu próprio login e senha
- **Login simples**: Autenticação com usuário e senha
- **Cadastro de jogos**: Admin adiciona jogos da Copa
- **Palpites por partida**: Participantes fazem seus palpites
- **Lançamento de resultados**: Admin lança os resultados reais
- **Pontuação automática**: 3 pontos placar exato, 1 ponto vencedor
- **Ranking em tempo real**: Tabela com ranking atualizado
- **Painel administrativo**: Gerenciamento de jogos e resultados

## Como executar localmente

1. Instalar dependências: `pip install -r requirements.txt`
2. Rodar: `python app.py`
3. Acessar: http://127.0.0.1:5000

## Acesso

### Usuário Admin
- **Usuário**: admin
- **Senha**: D/5=b-32/9

### Novos Participantes
Clique em "Faça seu cadastro" na página de login para criar uma conta.

## Pontuação

- **Placar exato**: 3 pontos
- **Apenas vencedor**: 1 ponto
- **Errado**: 0 pontos

## Deploy na Web

### Opção 1: Railway (Recomendado - Fácil e Gratuito)
1. Acesse [railway.app](https://railway.app)
2. Conecte sua conta GitHub
3. Crie um novo projeto e importe este repositório
4. Railway detectará automaticamente o Flask app
5. O banco SQLite será criado automaticamente

### Opção 2: Heroku
1. Instale Heroku CLI
2. Faça login: `heroku login`
3. Crie app: `heroku create nome-do-seu-app`
4. Deploy: `git push heroku main`
5. Abra: `heroku open`

### Opção 3: Vercel (Alternativa Moderna)
1. Acesse [vercel.com](https://vercel.com)
2. Importe o repositório GitHub
3. Configure como Python app
4. Deploy automático

## Tecnologias

- Flask
- SQLAlchemy
- Flask-Login
- Bootstrap
- SQLite
- Gunicorn (para produção)