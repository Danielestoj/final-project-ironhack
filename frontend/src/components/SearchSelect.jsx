import { useState, useEffect, useRef } from "react";
import client from "../api/client";

export function SearchSelect({ endpoint, selected, onChange, placeholder, labelKey = "nombre", matchKey, metaKeys = [], filterFn }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    if (!query) { setResults([]); return; }
    const timer = setTimeout(async () => {
      try {
        const res = await client.get(endpoint, { params: { q: query } });
        const data = Array.isArray(res.data) ? res.data : [];
        const filtered = filterFn ? data.filter((i) => filterFn(i, query)) : data;
        setResults(filtered.filter((i) => !selected.find((s) => (matchKey ? s[matchKey] : s[labelKey]) === i[labelKey])));
        setOpen(true);
      } catch { setResults([]); }
    }, 300);
    return () => clearTimeout(timer);
  }, [query, endpoint, labelKey, matchKey, selected, filterFn]);

  useEffect(() => {
    const handleClick = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const addItem = (item) => { onChange([...selected, item]); setQuery(""); setOpen(false); };
  const removeItem = (idx) => onChange(selected.filter((_, i) => i !== idx));

  return (
    <div className="search-select" ref={ref}>
      <div className="ss-tags">
        {selected.map((item, i) => (
          <span key={i} className="ss-tag">
            {item[matchKey || labelKey]}
            <button type="button" className="ss-tag-remove" onClick={() => removeItem(i)}>&times;</button>
          </span>
        ))}
        <input value={query} onChange={(e) => setQuery(e.target.value)} onFocus={() => query && setOpen(true)}
          placeholder={selected.length === 0 ? placeholder : ""} className="ss-input" />
      </div>
      {open && results.length > 0 && (
        <div className="ss-dropdown">
          {results.map((item, i) => (
            <div key={i} className="ss-option" onClick={() => addItem(item)}>
              <span className="ss-option-label">{item[labelKey]}</span>
              {metaKeys.length > 0 && (
                <span className="ss-option-meta">{metaKeys.map((k) => item[k]).filter(Boolean).join(" · ")}</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
