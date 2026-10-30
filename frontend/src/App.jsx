import { useEffect, useState } from 'react'

const LABELS = { ok: 'Conectado', unavailable: 'Indisponível', degraded: 'Degradado' }

function Status({ name, value }) {
  return (
    <li className="status">
      <span className={`dot ${value === 'ok' ? 'ok' : 'down'}`} />
      <span>{name}</span>
      <strong>{LABELS[value] ?? value}</strong>
    </li>
  )
}

export default function App() {
  const [health, setHealth] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/health')
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setHealth)
      .catch((e) => setError(e.message))
  }, [])

  return (
    <main>
      <h1>Peso do Cavalo</h1>
      <p className="sub">Protótipo em desenvolvimento · Sprint 1</p>

      <section>
        <h2>Estado do sistema</h2>
        {error && <p className="error">Não consegui falar com a API ({error}). Ela está rodando?</p>}
        {!health && !error && <p>Consultando a API…</p>}
        {health && (
          <ul>
            <Status name="API" value={health.status} />
            <Status name="Banco de dados" value={health.database} />
            <Status name="Armazenamento de fotos" value={health.storage} />
          </ul>
        )}
      </section>
    </main>
  )
}
