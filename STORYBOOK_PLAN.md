# Plano de Ação: Integração do Projeto com Storybook

## 1. Objetivo

O objetivo deste plano é integrar o Storybook ao projeto HelpubliAI para criar um guia de estilos vivo e uma biblioteca de componentes documentada. Isso irá acelerar o desenvolvimento, melhorar a consistência da UI, facilitar testes visuais e simplificar a manutenção dos componentes a longo prazo.

---

## Fase 1: Configuração e Primeiras Histórias

Nesta fase, vamos garantir que o Storybook esteja corretamente configurado para o nosso ambiente e criar nossa primeira história como prova de conceito.

### 1.1. Integrar o Tema do Material-UI (Passo Crítico)

- **Problema:** Por padrão, o Storybook não conhece o tema (cores, fontes) que criamos no arquivo `src/theme.js`. Os componentes serão renderizados com a aparência padrão do MUI, não a nossa.
- **Ação:** Precisamos "decorar" todas as histórias com o nosso `ThemeProvider`. Para isso, modifique o arquivo `.storybook/preview.js`.

  ```javascript
  // .storybook/preview.js
  import { ThemeProvider } from '@mui/material/styles';
  import CssBaseline from '@mui/material/CssBaseline';
  import theme from '../src/theme'; // Importe nosso tema

  export const decorators = [
    (Story) => (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Story />
      </ThemeProvider>
    ),
  ];
  ```

### 1.2. Criar uma História para um Componente Atômico

- **Objetivo:** Validar a configuração do tema e entender o fluxo básico de criação de histórias.
- **Ação:** Crie um novo arquivo `src/stories/Button.stories.js` para documentar o componente `Button` do MUI, que é a base de muitas interações no nosso app.

  ```javascript
  // src/stories/Button.stories.js
  import React from 'react';
  import { Button } from '@mui/material';

  export default {
    title: 'Design System/Button',
    component: Button,
  };

  export const Contained = () => <Button variant="contained">Contained Button</Button>;
  export const Outlined = () => <Button variant="outlined">Outlined Button</Button>;
  export const Disabled = () => <Button disabled>Disabled Button</Button>;
  export const ColorSecondary = () => <Button variant="contained" color="secondary">Secondary Color</Button>;
  ```

### 1.3. Iniciar o Storybook

- **Ação:** Rode o comando `npm run storybook` no terminal (na pasta `frontend/react-app`).
- **Resultado Esperado:** O navegador deve abrir uma nova aba com a interface do Storybook. Na barra lateral, você verá "Design System/Button" com as variações que criamos. Os botões devem estar com as cores e estilos do nosso tema.

---

## Fase 2: Histórias para Componentes do Projeto

Agora que a base está pronta, vamos documentar os componentes específicos que criamos para o HelpubliAI.

### 2.1. História para `UsersTable`

- **Objetivo:** Documentar a tabela de usuários, permitindo visualizá-la com diferentes conjuntos de dados.
- **Ação:** Crie o arquivo `src/stories/UsersTable.stories.js`.
  - Crie um array de dados `mockUsers` para simular os usuários.
  - Crie histórias para os diferentes estados da tabela:
    - `Default`: Passando a lista de `mockUsers`.
    - `Empty`: Passando um array vazio `[]`.
    - `Loading`: Passando `null` para a prop `users`.
  - Use o "actions addon" do Storybook para registrar cliques no botão de `onToggleAdmin`.

### 2.2. História para `RichTextEditor`

- **Objetivo:** Documentar e testar o editor de texto em isolamento.
- **Ação:** Crie o arquivo `src/stories/RichTextEditor.stories.js`.
  - Crie histórias para os diferentes estados do editor:
    - `Default`: Com um conteúdo HTML inicial.
    - `Empty`: Com o conteúdo sendo uma string vazia.
  - Conecte a prop `onContentChange` ao "actions addon" para ver o HTML sendo atualizado em tempo real no painel do Storybook.

---

## Fase 3: (Avançado) Histórias para Páginas e Layouts

Documentar páginas inteiras é útil para ver o layout geral e como os componentes interagem.

### 3.1. História para `MainLayout`

- **Problema:** O `MainLayout` e outros componentes usam `NavLink` e `useNavigate` do `react-router-dom`, que quebrarão no Storybook, pois ele não provê um contexto de roteamento.
- **Solução:** Precisamos decorar a história com um `MemoryRouter`.
- **Ação:** Crie `src/stories/MainLayout.stories.js` e envolva o componente em um `MemoryRouter` para simular o roteamento.

### 3.2. História para `LoginPage`

- **Objetivo:** Visualizar e refinar a página de login sem precisar deslogar da aplicação principal.
- **Ação:** Crie `src/stories/LoginPage.stories.js`. Assim como o `MainLayout`, ela precisará ser decorada com o `MemoryRouter`.

---

## Próximos Passos Imediatos

1.  **Modificar `.storybook/preview.js`** para adicionar o `ThemeProvider`, conforme descrito na Fase 1.
2.  **Criar `src/stories/Button.stories.js`** como sua primeira história.
3.  **Executar `npm run storybook`** e verificar se tudo funciona como esperado.
