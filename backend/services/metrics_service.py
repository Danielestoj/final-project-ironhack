import json
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter, defaultdict

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
METRICS_FILE = DATA_DIR / "metrics_save.json"


class MetricsService:
    def __init__(self):
        self.spell_views = Counter()
        self.chat_queries = []
        self.searches = []
        self.dice_rolls = []
        self.game_activity = defaultdict(lambda: {"spell_views": 0, "chat_queries": 0, "searches": 0})

    def track_spell_view(self, nombre: str, game_slug: str = "dnd"):
        self.spell_views[nombre] += 1
        self.game_activity[game_slug]["spell_views"] += 1

    def track_chat_query(self, texto: str, game_slug: str = "dnd"):
        self.chat_queries.append({
            "texto": texto[:200],
            "juego": game_slug,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.game_activity[game_slug]["chat_queries"] += 1

    def track_search(self, q: str = "", nivel: str = "", escuela: str = "", game_slug: str = "dnd"):
        self.searches.append({
            "q": q, "nivel": nivel, "escuela": escuela,
            "juego": game_slug,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.game_activity[game_slug]["searches"] += 1

    def track_dice_roll(self, formula: str, resultados: list, total: int, usuario: str = ""):
        self.dice_rolls.append({
            "formula": formula,
            "resultados": resultados,
            "total": total,
            "usuario": usuario,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        if len(self.dice_rolls) > 100:
            self.dice_rolls = self.dice_rolls[-100:]

    def get_recent_dice_rolls(self, n: int = 10):
        return self.dice_rolls[-n:][::-1]

    def get_dashboard(self) -> dict:
        top_spells = self.spell_views.most_common(20)
        recent_chat = self.chat_queries[-50:][::-1]
        recent_searches = self.searches[-30:][::-1]

        search_q_counter = Counter()
        for s in self.searches:
            if s["q"]:
                search_q_counter[s["q"]] += 1

        return {
            "top_spells": [{"nombre": n, "visitas": c} for n, c in top_spells],
            "total_chat_queries": len(self.chat_queries),
            "total_searches": len(self.searches),
            "total_dice_rolls": len(self.dice_rolls),
            "recent_chat": recent_chat,
            "recent_searches": recent_searches,
            "recent_dice_rolls": self.get_recent_dice_rolls(10),
            "top_search_terms": [{"termino": t, "count": c} for t, c in search_q_counter.most_common(10)],
            "game_activity": dict(self.game_activity),
        }

    def save_to_disk(self) -> dict:
        data = {
            "spell_views": dict(self.spell_views),
            "chat_queries": self.chat_queries,
            "searches": self.searches,
            "dice_rolls": self.dice_rolls,
            "game_activity": dict(self.game_activity),
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        DATA_DIR.mkdir(exist_ok=True)
        METRICS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"ok": True, "path": str(METRICS_FILE), "entries": len(self.chat_queries) + len(self.searches)}


metrics_service = MetricsService()
