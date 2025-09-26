# Plano de Ação: Análise e Melhorias do Frontend

## 1. Resumo da Análise

A estrutura atual do frontend é híbrida, contendo:
1.  **Páginas estáticas:** Um conjunto de arquivos `html`, `css` e `js` na pasta `frontend/` que parecem lidar com funcionalidades-chave como login, registro e o dashboard de admin.
2.  **Aplicação React:** Uma aplicação moderna (`frontend/react-app/`) criada com `create-react-app`, utilizando Material-UI (MUI), Tiptap (editor de texto), Storybook e React Router.

Essa estrutura dupla pode gerar inconsistências de UI/UX, dificultar a manutenção e duplicar esforços. O plano de ação visa unificar a experiência do usuário e a base de código dentro da aplicação React.

## 2. Pontos de Melhoria Identificados

### a. Base de Código e Dependências (React App)
- **Dependências:** O `package.json` mostra uma base sólida, mas uma auditoria (`npm audit`) é recomendada para identificar vulnerabilidades. As dependências do Storybook estão na seção `devDependencies`, o que é uma boa prática.
- **Qualidade de Código:** O projeto já possui uma configuração do ESLint. A adição do **Prettier** para formatação automática de código é recomendada para manter um estilo consistente em toda a equipe.
- **Estrutura de Pastas:** A estrutura (`components`, `pages`, `hooks`, `services`) é lógica e escalável.

### b. Componentização e UI/UX
- **Storybook:** O uso do Storybook é um excelente começo. No entanto, poucos componentes (`Button`, `Header`, `Page`, etc.) e páginas (`LoginPage`) estão documentados. Expandir o Storybook para cobrir todos os componentes da UI (especialmente os do MUI) e estados de página é crucial.
- **Consistência de UI:** A biblioteca MUI (`@mui/material`) e um arquivo de tema (`src/theme.js`) foram configurados, o que é ótimo para a consistência visual. O desafio é garantir que as páginas estáticas (se mantidas) sigam o mesmo design system.
- **Migração:** As páginas estáticas (`admin-dashboard.html`, `login.html`, `register.html`) devem ser migradas para se tornarem páginas dentro da aplicação React, aproveitando o React Router, os componentes reutilizáveis e o design system do MUI.

### c. Performance e Acessibilidade
- **Performance:** A aplicação React já faz "code splitting" (divisão de código), o que é bom para o tempo de carregamento inicial. Recomenda-se uma análise com o **Lighthouse** (ferramenta do Chrome DevTools) para identificar gargalos de performance, SEO e PWA (Progressive Web App).
- **Acessibilidade (a11y):** É fundamental garantir que a aplicação seja acessível a todos. Recomenda-se usar o addon `@storybook/addon-a11y` para verificar a acessibilidade dos componentes diretamente no Storybook.

## 3. Plano de Ação Sugerido

### Fase 1: Fundação e Unificação (Curto Prazo)

1.  **Decisão Estratégica:** Oficializar a migração de todas as funcionalidades das páginas estáticas para a aplicação React. As páginas antigas devem ser arquivadas ou removidas após a migração.
2.  **Setup de Qualidade de Código:**
    - Executar `npm audit --fix` para corrigir vulnerabilidades conhecidas.
    - Instalar e configurar o **Prettier** com o ESLint para padronizar a formatação do código.
3.  **Migração da Autenticação:**
    - Criar as páginas de Login (`LoginPage.js`) e Registro (`RegisterPage.js`) que já existem no React para substituir `login.html` and `register.html`.
    - Garantir que o `auth.js` e a lógica de API (`api.js`) sejam totalmente integrados aos serviços React (`src/services/api.js`).

### Fase 2: Expansão e Consolidação (Médio Prazo)

1.  **Migração do Dashboard:** Migrar o `admin-dashboard.html` para uma nova página na aplicação React (`AdminDashboardPage.js`), utilizando os componentes do MUI, como o `UsersTable.js` que já existe.
2.  **Cobertura do Storybook:** Documentar todos os componentes de UI reutilizáveis e as principais páginas no Storybook. Para cada componente, criar "stories" para seus diferentes estados (ex: botão desabilitado, formulário com erro, etc.).
3.  **Testes de Acessibilidade:** Configurar o addon de acessibilidade no Storybook e corrigir os problemas reportados.

### Fase 3: Otimização e Refinamento (Longo Prazo)

1.  **Auditoria de Performance:** Realizar uma auditoria completa com o Lighthouse na aplicação unificada. Implementar otimizações sugeridas, como "lazy loading" de rotas/componentes com `React.lazy()`.
2.  **Testes Unitários e de Integração:** Aumentar a cobertura de testes (`*.test.js`) para os hooks, serviços e componentes críticos, garantindo a estabilidade da aplicação à medida que ela cresce.
3.  **Remoção de Código Legado:** Após a migração completa e verificação, remover definitivamente os arquivos estáticos (`.html`, `js/`, `css/`) da pasta `frontend/` para simplificar o projeto.
