# Euro Scouts Directory — app (Next.js + shadcn/ui)

Front-end do diretório: Next.js 15 (static export) + Tailwind + shadcn/ui.
3 visões — **Cards**, **Lista** e **Tabela** (com ordenação) — busca e filtros por
liga/clube, layout claro.

## Rodar local

```bash
cd web
npm install      # (rode você — não instalo pacotes automaticamente)
npm run dev      # http://localhost:3000
```

## Build estático

```bash
npm run build    # gera web/out/  (output: 'export')
```

## Dados

`public/data.json` é gerado pelo pipeline (`python 3_build_site.py` na raiz copia
`data/scouts.json` pra cá). Não editar à mão.

## Deploy

Netlify builda automático via `netlify.toml` na raiz do repo
(base `web`, `npm install && npm run build`, publish `out`).
