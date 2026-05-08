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

### 🚀 Railway (Recomendado - Super Fácil)

**Passo 1: Criar conta no GitHub (se não tiver)**
- Acesse [github.com](https://github.com)
- Crie conta gratuita
- Verifique seu email

**Passo 2: Upload do projeto**
- Crie um novo repositório: "bolao-copa-2026"
- No terminal, execute:
```bash
git remote add origin https://github.com/SEU_USERNAME/bolao-copa-2026.git
git branch -M main
git push -u origin main
```

**Passo 3: Deploy no Railway**
- Acesse [railway.app](https://railway.app)
- Faça login com GitHub
- Clique "New Project" → "Deploy from GitHub repo"
- Selecione seu repositório "bolao-copa-2026"
- Railway detectará automaticamente o Flask app
- Deploy leva 2-3 minutos

**Passo 4: Configurar domínio (opcional)**
- No Railway dashboard, vá em "Settings" → "Domains"
- Adicione um domínio personalizado ou use o gratuito fornecido

**✅ Pronto!** Seu bolão estará online 24/7.

### Outras Opções

#### Heroku
1. Instale Heroku CLI
2. `heroku login`
3. `heroku create bolao-copa-2026`
4. `git push heroku main`

#### Vercel
1. Acesse [vercel.com](https://vercel.com)
2. Importe repositório GitHub
3. Configure como Python app

## Tecnologias

- Flask
- SQLAlchemy
- Flask-Login
- Bootstrap
- SQLite
- Gunicorn (para produção)