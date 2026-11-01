#!/usr/bin/env python3
"""Atualiza o catálogo de skills do Gabinete.

Lê os repositórios listados em skills-hub/fontes.json (os mesmos que a skill
find-skills da Vercel indica), extrai nome e descrição de cada SKILL.md e grava:

  skills-hub/catalogo.json        catálogo completo (usado pela versão local)
  skills-hub/catalogo-db/*.json   o mesmo catálogo em partes de até ~150 skills,
                                  no formato dos documentos da coleção `catalogo`
                                  do artifact publicado

Quando skills.sh responde, também anota o número de instalações de cada skill
(a mesma busca que `npx skills find` usa). Se não responder, segue sem isso.

Uso:  python3 skills-hub/scripts/atualizar_catalogo.py [--cache DIR]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HUB = Path(__file__).resolve().parents[1]
CHUNK = 150

# Palavra-chave -> categoria do Gabinete. A primeira categoria com acerto vence.
CATEGORIAS = [
    ("Segurança", r"secur|vulnerab|auth\b|oauth|password|secret|pentest|compliance|gdpr|privacy|1password|okta|audit log"),
    ("Financeiro", r"financ|invoice|account(ing|ant)|stripe|payment|billing|expense|budget|quickbooks|xero|payroll|tax\b|bank|crypto|invest|brex|ramp\b|square\b|paypal|chargebee|freshbooks"),
    ("Marketing", r"marketing|seo\b|\bads?\b|advertis|campaign|newsletter|social media|instagram|tiktok|linkedin|twitter|facebook|youtube|copywrit|content|influenc|mailchimp|hubspot|brevo|klaviyo|activecampaign|lead|growth|sales|crm"),
    ("Memória", r"memory|knowledge|notes?\b|notion|obsidian|recall|journal|second brain|wiki|bookmark|evernote|roam"),
    ("Design", r"design|figma|canvas|\btheme|brand|image|gif|art\b|algorithmic|ui\b|ux\b|font|color|canva|video|photo|visual|slides|pptx|presentation"),
    ("Ideias", r"brainstorm|idea|research|insight|name|strategy|competit|analy[sz]"),
    ("Dev", r"react|next\.?js|code|test|deploy|vercel|github|gitlab|api\b|sdk|mcp|webapp|frontend|backend|database|docker|kubernetes|ci\b|sentry|supabase|postgres|bug|jira|linear"),
    ("Produtividade", r"docx|xlsx|pdf|document|spreadsheet|sheet|calendar|email|gmail|outlook|slack|meeting|todo list|asana|trello|clickup|monday|file|organiz|comms|resume|writing"),
]


def categorizar(nome: str, desc: str) -> str:
    texto = f"{nome} {desc}".lower()
    # Frases-padrão das automações Composio que não dizem nada sobre o assunto
    texto = re.sub(r"via rube mcp( \(composio\))?|always search tools first for current schemas\.?|rube mcp|composio", " ", texto)
    for cat, padrao in CATEGORIAS:
        if re.search(padrao, texto):
            return cat
    return "Automação" if "automation" in texto else "Outra"


# Categoria do marketplace de plugins -> categoria do Gabinete (quando a palavra-chave não decide)
CAT_PLUGIN = {"security": "Segurança", "design": "Design", "development": "Dev", "database": "Dev",
              "monitoring": "Dev", "deployment": "Dev", "testing": "Dev", "migration": "Dev",
              "productivity": "Produtividade", "automation": "Automação", "learning": "Ideias"}


def plugins_do_marketplace(repo: str, raiz: Path, fonte: dict, anterior: dict, hoje: str) -> list[dict]:
    mk = json.loads((raiz / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    nome_mk = mk.get("name", repo.split("/")[-1])
    out = []
    for p in mk.get("plugins", []):
        nome, desc = p.get("name"), re.sub(r"\s+", " ", p.get("description", "")).strip()
        if not nome or not desc:
            continue
        src = p.get("source")
        if isinstance(src, str):
            link = f"https://github.com/{repo}/tree/HEAD/{src.lstrip('./')}"
        elif isinstance(src, dict) and src.get("url"):
            base = src["url"].removesuffix(".git")
            link = f"{base}/tree/{src.get('ref', 'HEAD')}/{src['path']}" if src.get("path") else base
        else:
            link = p.get("homepage") or f"https://github.com/{repo}"
        cat = categorizar(nome, desc)
        if cat in ("Outra", "Automação", "Dev", "Produtividade") and CAT_PLUGIN.get(p.get("category")):
            cat = CAT_PLUGIN[p["category"]] if cat in ("Outra", "Automação") else cat
        sid = re.sub(r"[^a-z0-9_.-]+", "-", f"plugin--{nome_mk}--{nome}".lower()).strip("-")[:190]
        autor = (p.get("author") or {}).get("name", "")
        out.append({
            "id": sid, "tipo": "plugin", "nome": p.get("displayName") or nome,
            "descricao": desc[:700], "fonte": f"{nome_mk}" + (f" · {autor}" if autor else ""),
            "grupo": fonte.get("grupo", repo), "categoria": cat,
            "instalar": f"/plugin install {nome}@{nome_mk}", "link": link,
            "primeiraVez": anterior.get(sid, {}).get("primeiraVez", hoje),
        })
    return out


def frontmatter(md: str) -> dict:
    m = re.match(r"\s*---\s*\n(.*?)\n---", md, re.S)
    if not m:
        return {}
    out, chave = {}, None
    for linha in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_-]+)\s*:\s*(.*)$", linha)
        if kv:
            chave, valor = kv.group(1).lower(), kv.group(2).strip()
            out[chave] = valor
        elif chave and linha.startswith((" ", "\t")):
            out[chave] = (out[chave] + " " + linha.strip()).strip()
    for k, v in out.items():
        v = v.strip()
        if v in (">", "|", ">-", "|-"):
            v = ""
        out[k] = v.strip("\"'").strip()
    return out


def clonar(repo: str, cache: Path) -> Path:
    destino = cache / repo.replace("/", "__")
    url = f"https://github.com/{repo}.git"
    if (destino / ".git").exists():
        subprocess.run(["git", "-C", str(destino), "fetch", "-q", "--depth", "1", "origin"], check=True)
        subprocess.run(["git", "-C", str(destino), "reset", "-q", "--hard", "FETCH_HEAD"], check=True)
    else:
        subprocess.run(["git", "clone", "-q", "--depth", "1", url, str(destino)], check=True)
    return destino


def instalacoes(nomes: list[str]) -> dict[str, int]:
    """Busca install counts no skills.sh. Devolve {} se o site não responder."""
    achados: dict[str, int] = {}
    for i, nome in enumerate(nomes):
        url = "https://skills.sh/api/search?" + urllib.parse.urlencode({"q": nome, "limit": "20"})
        try:
            with urllib.request.urlopen(url, timeout=8) as r:
                dados = json.load(r)
        except Exception:
            if i == 0:
                print("skills.sh não respondeu; seguindo sem número de instalações.", file=sys.stderr)
                return {}
            continue
        for s in dados.get("skills", dados if isinstance(dados, list) else []):
            src, n = s.get("source", ""), s.get("installs") or 0
            if s.get("name") and src:
                achados[f"{src}@{s['name']}".lower()] = int(n)
    return achados


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="/tmp/gabinete-fontes")
    args = ap.parse_args()
    cache = Path(args.cache)
    cache.mkdir(parents=True, exist_ok=True)

    fontes = json.loads((HUB / "fontes.json").read_text(encoding="utf-8"))
    anterior_path = HUB / "catalogo.json"
    anterior = {}
    if anterior_path.exists():
        for s in json.loads(anterior_path.read_text(encoding="utf-8")).get("skills", []):
            anterior[s["id"]] = s
    hoje = dt.date.today().isoformat()

    skills = []
    for fonte in fontes:
        repo = fonte["repo"]
        raiz = clonar(repo, cache)
        if fonte.get("tipo") == "plugins":
            skills.extend(plugins_do_marketplace(repo, raiz, fonte, anterior, hoje))
            continue
        for md in sorted(raiz.rglob("SKILL.md")):
            rel = md.relative_to(raiz)
            if any(p in ("template", "template-skill", "node_modules") or p.startswith(".") for p in rel.parts[:-1]):
                continue
            fm = frontmatter(md.read_text(encoding="utf-8", errors="replace"))
            nome = fm.get("name") or rel.parent.name
            desc = re.sub(r"\s+", " ", fm.get("description", "")).strip()
            if not desc or "placeholder" in desc.lower():
                continue
            sid = re.sub(r"[^a-z0-9_.-]+", "-", f"{repo}--{nome}".lower()).strip("-")[:190]
            velho = anterior.get(sid, {})
            skills.append({
                "id": sid,
                "tipo": "skill",
                "nome": nome,
                "descricao": desc[:700],
                "fonte": repo,
                "grupo": fonte.get("grupo", repo),
                "categoria": categorizar(nome, desc),
                "instalar": f"npx skills add https://github.com/{repo} --skill {nome}",
                "link": f"https://github.com/{repo}/blob/HEAD/{rel.as_posix()}",
                "primeiraVez": velho.get("primeiraVez", hoje),
            })

    # Remove duplicatas: mesmo nome (ignorando _ - e espaços) na mesma fonte
    vistos, unicos = set(), []
    for s in skills:
        chave = (s["fonte"], re.sub(r"[\s_-]+", "-", s["nome"].lower()))
        if s["id"] not in vistos and chave not in vistos:
            vistos.update({s["id"], chave})
            unicos.append(s)
    skills = unicos

    contagem = instalacoes(sorted({s["nome"] for s in skills if s["tipo"] == "skill" and s["grupo"] != "Composio"}))
    for s in skills:
        n = contagem.get(f"{s['fonte']}@{s['nome']}".lower())
        if n:
            s["instalacoes"] = n

    primeira_execucao = not anterior
    novas = [] if primeira_execucao else [s["id"] for s in skills if s["id"] not in anterior]
    info = {
        "atualizadoEm": hoje,
        "total": len(skills),
        "fontes": [f["repo"] for f in fontes],
        "novas": novas,
        "instalacoesDisponiveis": bool(contagem),
    }
    anterior_path.write_text(json.dumps({"info": info, "skills": skills}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    pasta = HUB / "catalogo-db"
    pasta.mkdir(exist_ok=True)
    for f in pasta.glob("*.json"):
        f.unlink()
    (pasta / "info.json").write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
    partes = [skills[i:i + CHUNK] for i in range(0, len(skills), CHUNK)]
    for i, parte in enumerate(partes, 1):
        (pasta / f"parte-{i:02d}.json").write_text(
            json.dumps({"parte": i, "atualizadoEm": hoje, "skills": parte}, ensure_ascii=False), encoding="utf-8")

    print(f"{len(skills)} skills de {len(fontes)} fontes; {len(novas)} novas; {len(partes)} partes em catalogo-db/.")


if __name__ == "__main__":
    main()
