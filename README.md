# 📂 Contábil Files - Gestão Inteligente de Documentos

![Django](https://img.shields.io/badge/django-%23092e20.svg?style=for-the-badge&logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511fa.svg?style=for-the-badge&logo=bootstrap&logoColor=white)

Uma plataforma moderna de troca de documentos entre escritórios de contabilidade e seus clientes, focada em automação e experiência do usuário (UX).

## ✨ Funcionalidades Principais

- **Dashboard Administrativo:** Visão panorâmica para Administradores Contábeis com relatório de pendências por empresa.
- **Gestão de Tipos de Usuário:** Diferenciação entre Admins, Contadores Operacionais e Clientes.
- **Sistema de Pedidos:** Solicitação formal de documentos com status em tempo real (Pendente/Concluído).
- **Ativação por E-mail:** Fluxo de segurança para novos usuários via token de ativação.
- **Interface Dark Modern:** Design responsivo focado na redução de fadiga visual e profissionalismo.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Django 5.x
- **Banco de Dados:** SQLite (Desenvolvimento) / PostgreSQL (Produção sugerido)
- **Frontend:** HTML5, CSS3 (Custom Dark Theme), Bootstrap 5.3, Bootstrap Icons
- **Autenticação:** Custom User Model com campos de tipo de usuário e empresa.

## 🚀 Como Executar o Projeto



Instale as dependências:
   pip install django
Execute as migrações e o servidor:
   python manage.py migrate
   python manage.py runserver
