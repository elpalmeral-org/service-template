# service-template

> Plantilla [Cookiecutter](https://cookiecutter.readthedocs.io/) del *golden path* «crear un
> servicio nuevo» del [agentic-platform-lab](https://github.com/elpalmeral-org/agentic-platform-lab)
> (ADR 0035). La usa `crear-servicio.yml` (en `agentic-platform-lab`) para generar un repo nuevo,
> listo para AIDLC y el harness corporativo — y se puede usar igual a mano, en local.

No es un repo que se clona y se edita: es el **molde** del que nace cada servicio nuevo. El
resultado es un esqueleto FastAPI + Angular que arranca, pasa `/healthz`/`/readyz`/`/metrics`, y
no asume ninguna entidad de negocio — la primera *feature* real del servicio nuevo la añade su
propio equipo, por AIDLC.

## Variables

| Variable | De dónde sale | Ejemplo |
|---|---|---|
| `service_name` | la pide el formulario (Port o `cookiecutter` en local) | `Facturas` |
| `service_slug` | `service_name` en minúsculas y con guiones | `facturas` |
| `service_description` | derivada, editable | `Servicio Facturas del agentic-platform-lab` |
| `package_name` | `service_slug` con `_` (identificador Python válido) | `facturas` |
| `env_prefix` | `package_name` en mayúsculas + `_` | `FACTURAS_` |
| `frontend` / `backend` / `runtime` | enumerados; hoy un único valor cada uno | `angular` / `fastapi` / `k3s01` |

## Uso en local

```bash
uvx --from cookiecutter cookiecutter https://github.com/elpalmeral-org/service-template
```

## Por qué los delimitadores de Jinja no son `{{ }}`

Este repo plantilla convive con `${{ github.ref }}` (GitHub Actions), `{{ v }}` (interpolación de
Angular) y `{{"ci-ok"}}` (nodo hexagonal de Mermaid) — los tres usan el mismo delimitador por
defecto de Jinja2. `cookiecutter.json` cambia el delimitador de las variables a `<<= =>>`
(`_jinja2_env_vars`) precisamente para que esos tres sigan intactos y solo se sustituyan las
variables propias de esta plantilla. Cualquier fichero nuevo que se añada aquí debe usar
`<<=cookiecutter.variable=>>`, no `{{ cookiecutter.variable }}`.

## Qué NO se plantilla

Todo lo que gestiona `apm install` (`.claude/`, `.github/instructions/`, `AGENTS.md`…) no vive en
esta plantilla: lo genera `apm` en el propio repo nuevo a partir del harness pineado en `apm.yml`.
Tampoco se plantillan los roles compartidos del harness (`meridian/<rol>` en HarnessRouter) ni el
paquete Rego `data.meridian.pr_gates` — son productos del harness corporativo, no de ningún
servicio en concreto (la «marca» `meridian` es del harness, no de Meridian Orders).
