import {useEffect, useRef, useState} from 'react';
import {WorkPackagePage} from './WorkPackagePage';
import './supply-chain.css';

type Obj = Record<string, any>;

export function SupplyChainWorkspace({data, scenario, busy, onSave, run}: {
  data: Obj; scenario: Obj; busy: boolean; onSave: (v: Obj) => void; run: () => void;
}) {
  const [reference, setReference] = useState<Obj | null>(null);
  const [error, setError] = useState('');
  const [loaded, setLoaded] = useState(false);
  const frame = useRef<HTMLIFrameElement>(null);
  const evidence = useRef<HTMLDetailsElement>(null);
  useEffect(() => {
    const controller = new AbortController();
    fetch('/api/references/lattice-supply', {signal: controller.signal})
      .then(async r => {if (!r.ok) throw Error('The imported supply-chain snapshot could not be loaded.'); return r.json();})
      .then(setReference).catch(e => {if (e.name !== 'AbortError') setError(e.message);});
    return () => controller.abort();
  }, []);
  const meta = reference?.metadata;
  return <div className="supply-workspace">
    <section className="supply-context" aria-label="Supply-chain scope">
      <div><h2>Lattice supply-chain explorer</h2>
        <p>Procurement workspace · revision {scenario.revision} · {scenario.inputs.capacity_mw.toLocaleString()} MW</p>
      </div>
      <div className="button-row">
        <button className="secondary" onClick={() => {if (evidence.current) {evidence.current.open = true; evidence.current.scrollIntoView({behavior: 'smooth', block: 'start'});}}}>Procurement evidence ↓</button>
        <button className="secondary" onClick={() => frame.current?.requestFullscreen().catch(() => setError('Full screen is unavailable in this browser. Use the explorer below.'))}>Expand explorer</button>
        <button className="primary" disabled={busy} onClick={run}>Refresh C54 record</button>
      </div>
    </section>
    <div className="supply-snapshot"><span className="supply-dot"/>
      <p>{reference ? <><b>UK directory snapshot · {meta.snapshot_date}</b> · {reference.counts.suppliers} supplier profiles · {reference.counts.components} components · {reference.counts.links} capability links.</> : 'Loading imported directory metadata…'}<br/>
        The directory is contextual across layouts. It is not a supplier shortlist for this farm. Exposure scores describe the attached evidence; lead times, quotations and available capacity need vendor records.</p>
    </div>
    {error && <p className="error" role="alert">{error}</p>}
    <section className="supply-explorer" aria-label="Interactive Lattice supply-chain explorer">
      {!loaded && <p className="supply-loading" role="status">Loading the seven supply-chain views…</p>}
      <iframe ref={frame} key={scenario.id} title="C54 Lattice supply-chain explorer" src={import.meta.env.BASE_URL+'assets/lattice/index.html'}
        sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox" allowFullScreen
        referrerPolicy="no-referrer" onLoad={() => setLoaded(true)}/>
    </section>
    <details className="supply-source">
      <summary>Source, model and geographic coverage</summary>
      <div><p>Adapted from <b>Lattice · Offshore Wind</b>, by Koorosh Aslansefat. The original page and its embedded directory data are preserved with checksums. Supplier capability claims have not been independently reverified.</p>
        <p>The model combines supply depth (35%), cluster concentration (20%), size fragility (15%), overseas headquarters (15%) and evidence weakness (15%). Explicit, declared and inferred links have weights 1, 0.9 and 0.6. Scores are indices, not delay probabilities. An absent link can reflect missing directory evidence.</p>
        <p>Town points are geocoded reference locations; regional cluster shapes and country anchors are illustrative. Firm counts do not measure vessels, manufacturing throughput, berths or available capacity. “Ask the graph” runs deterministic local queries.</p>
        {reference?.data_notes?.map((note: string) => <p key={note}>{note}</p>)}
        {meta && <><p className="micro">Original SHA-256: <code>{meta.original_sha256}</code><br/>Data SHA-256: <code>{meta.data_sha256}</code></p>
          <div className="button-row"><a className="secondary small" href="/api/references/lattice-supply/original" download>Original reference</a>
          <a className="secondary small" href="/api/references/lattice-supply/data.json" download>Directory data JSON</a>
          <a className="secondary small" href={`/api/scenarios/${scenario.id}/export.json`} download>Revision JSON</a></div></>}
      </div>
    </details>
    <details ref={evidence} className="supply-evidence" id="procurement-evidence">
      <summary>Procurement evidence & lead-time review <span>Revision {scenario.revision} · {data.work_package?.draft.evidence.filter((r: Obj) => r.status === 'reviewed').length || 0} reviewed inputs</span></summary>
      {data.work_package ? <WorkPackagePage key={scenario.id + data.work_package.method + (data.work_package.supply_reference?.metadata.data_sha256 || '')} data={data} scenario={scenario} cid="C54" busy={busy} onSave={onSave}/>
        : <div><p>Refresh the C54 record to open this revision’s procurement evidence register.</p><button className="primary" disabled={busy} onClick={run}>Open procurement register</button></div>}
    </details>
  </div>;
}
