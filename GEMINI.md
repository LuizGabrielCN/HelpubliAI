# Plano de Ação: Análise e Melhorias do Frontend (Atualizado)

## 1. Resumo do Estado Atual

A análise inicial apontava uma estrutura híbrida com páginas estáticas e uma aplicação React. No entanto, o projeto evoluiu e a estrutura foi unificada com sucesso na aplicação React. As páginas estáticas legadas (`login.html`, `admin-dashboard.html`, etc.) já foram removidas, e a base de código está centralizada em `frontend/react-app/`.

As ferramentas de qualidade de código e documentação de componentes, como Prettier e Storybook, já estão configuradas e em uso.

## 2. Itens Concluídos (Fases 1 e 2)

As fases iniciais do plano de ação foram concluídas com sucesso, seja por já terem sido implementadas anteriormente ou pelas ações recentes.

- **✅ Unificação do Frontend:** O projeto não é mais híbrido. Toda a interface está consolidada na aplicação React.
- **✅ Remoção de Código Legado:** Os arquivos estáticos (`.html`, `js/`, `css/`) foram removidos, simplificando a estrutura do projeto.
- **✅ Qualidade de Código:** O Prettier foi integrado ao ESLint, garantindo um padrão de formatação consistente.
- **✅ Migração de Funcionalidades:** As páginas de autenticação e o dashboard de administração já são componentes React (`LoginPage.js`, `AdminDashboardPage.js`).
- **✅ Documentação no Storybook:** Todos os componentes reutilizáveis na pasta `src/components` possuem "stories" correspondentes.
- **✅ Testes de Acessibilidade:** O addon de acessibilidade (`@storybook/addon-a11y`) está instalado e configurado no Storybook.

## 3. Pendências e Próximos Passos (Fase 3)

Com a fundação do projeto sólida, o foco agora é na otimização e refinamento.

### a. Auditoria de Vulnerabilidades (Pendente)
- **Status:** A execução de `npm audit` revelou 9 vulnerabilidades que exigem uma atualização forçada (`npm audit fix --force`).
- **Ação Necessária:** Requer decisão do usuário, pois a atualização forçada pode introduzir "breaking changes".

### b. Otimização e Refinamento (Próximos Passos)

1.  **Auditoria de Performance com Lighthouse:**
    - **Objetivo:** Analisar a aplicação em execução para identificar gargalos de performance, acessibilidade, SEO e PWA (Progressive Web App).
    - **Pré-requisito:** A aplicação precisa estar em execução.

2.  **Aumento da Cobertura de Testes:**
    - **Objetivo:** Analisar a cobertura de testes unitários e de integração (`*.test.js`) e expandi-la para hooks, serviços e componentes críticos, garantindo a estabilidade da aplicação.

3.  **Otimizações Sugeridas pelo Lighthouse:**
    - **Objetivo:** Implementar as melhorias recomendadas pela auditoria, como "lazy loading" de rotas/componentes com `React.lazy()` para otimizar o tempo de carregamento inicial.