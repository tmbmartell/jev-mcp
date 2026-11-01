# Gabinete de Skills

Acervo pessoal de skills, bots e servidores MCP. Cada peça vira uma ficha com
**o que faz**, **como faz**, **quando usar**, categoria e um **diário de uso**
com nota de 1 a 5 estrelas.

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
