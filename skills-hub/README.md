# Gabinete de Skills

Acervo pessoal de skills, bots e servidores MCP. Cada peça vira uma ficha com
**o que faz**, **como faz**, **quando usar**, categoria e um **diário de uso**
com nota de 1 a 5 estrelas.

## Descobrir skills e plugins

No topo do Gabinete há uma barra de perguntas: escreva o que quer resolver
("organizar notas fiscais", "automatizar meu Instagram") e o Gabinete procura no
catálogo. Na versão publicada, o Claude traduz a pergunta em termos de busca,
escolhe até 6 itens e diz em uma frase por que cada um serve. Sem o Claude, a
busca por palavras entende termos comuns em português.

Cada resultado traz o comando de instalação com botão de copiar, o link do
GitHub e o botão **Catalogar no acervo**.

### Fontes do catálogo (`fontes.json`)

| Fonte | O que traz | Como instalar |
|---|---|---|
| `vercel-labs/skills` (find-skills) e `vercel-labs/agent-skills` | Skills da Vercel | `npx skills add https://github.com/<repo> --skill <nome>` |
| `anthropics/skills` | Skills oficiais da Anthropic | idem |
| `ComposioHQ/awesome-claude-skills` | Centenas de automações de apps | idem |
| `anthropics/claude-plugins-official` | Marketplace oficial de plugins | `/plugin install <nome>@claude-plugins-official` |

Para incluir outra fonte, acrescente uma linha em `fontes.json`
(`"tipo": "plugins"` quando for um marketplace com `.claude-plugin/marketplace.json`).

### Atualização automática

Uma tarefa agendada roda toda **segunda e quinta às 7h23 (Brasília)**:
executa `scripts/atualizar_catalogo.py`, faz commit do `catalogo.json`
e sincroniza o banco do Gabinete publicado. Skills que entram no catálogo
aparecem no botão "novidades" ao lado da barra de perguntas.

O script também tenta buscar o número de instalações em skills.sh (a mesma
base do `npx skills find`). Se o site não estiver liberado na rede, ele
segue sem esse número.

## Como usar

- **Catalogar**: botão `+ Catalogar skill`. Cole o `SKILL.md` (ou o README do bot)
  e clique em **Ler dados** para puxar nome e descrição do cabeçalho. Na versão
  publicada no claude.ai aparece também **Claude preenche a ficha**, que resume,
  categoriza e sugere tags.
- **Filtrar**: categorias no topo (Segurança, Marketing, Financeiro, Memória,
  Design, Dev, Ideias, Bots & IA, ou qualquer uma nova que você digitar), busca,
  tipo e ordenação (melhor nota, mais usadas, nunca usadas).
- **Registrar uso**: abra a ficha, dê a nota, diga onde usou e o que achou.
- **Backup**: copia todo o acervo em JSON. Cole o resultado em `skills.json`
  para guardar no repositório.

## Rodar localmente

```bash
cd skills-hub && python3 -m http.server 8000
```

Abra http://localhost:8000. Localmente as fichas ficam no navegador
(`localStorage`), começando pelas de `skills.json`.

## Formato de uma ficha

```json
{
  "id": "angulos7", "num": 1, "nome": "angulos7",
  "tipo": "skill | bot | mcp", "categoria": "Marketing",
  "oQueFaz": "...", "comoFaz": "...", "quandoUsar": "...",
  "fonte": "link ou origem", "tags": ["conteúdo"],
  "notas": [{ "id": "x1", "nota": 5, "onde": "Lançamento X", "texto": "...", "data": "2026-11-01" }]
}
```
