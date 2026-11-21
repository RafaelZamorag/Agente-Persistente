"""Modelo baseline explicable para el MVP."""
from app.domain.models import Fixture, Outcome, Prediction


class PredictionEngine:
    """Calcula señales orientativas; no es un modelo validado para apuestas reales."""

    model_version = "baseline-v0.1"

    def predict(self, fixture: Fixture, data_source: str) -> Prediction:
        home_score = self._score(fixture.home.strength, fixture.home.recent_form, 0.08)
        away_score = self._score(fixture.away.strength, fixture.away.recent_form, 0.0)
        draw_score = 0.28 + max(0.0, 0.08 - abs(home_score - away_score) * 0.04)
        total = home_score + draw_score + away_score
        probabilities = {
            Outcome.HOME: home_score / total,
            Outcome.DRAW: draw_score / total,
            Outcome.AWAY: away_score / total,
        }
        implied = {
            Outcome.HOME: 1 / fixture.odds.home,
            Outcome.DRAW: 1 / fixture.odds.draw,
            Outcome.AWAY: 1 / fixture.odds.away,
        }
        edge = {outcome: probabilities[outcome] - implied[outcome] for outcome in Outcome}
        expected_value = {
            Outcome.HOME: probabilities[Outcome.HOME] * fixture.odds.home - 1,
            Outcome.DRAW: probabilities[Outcome.DRAW] * fixture.odds.draw - 1,
            Outcome.AWAY: probabilities[Outcome.AWAY] * fixture.odds.away - 1,
        }
        best = max(expected_value, key=expected_value.get)
        confidence = self._confidence(probabilities, fixture)
        recommendation = (
            f"Señal orientativa: {best.value}"
            if expected_value[best] > 0.03
            else "Sin ventaja clara según el baseline"
        )
        explanation = [
            "La localía aporta un ajuste fijo de 8% al marcador del equipo local.",
            f"La fuerza relativa es {fixture.home.strength - fixture.away.strength:+.1f} puntos.",
            f"La forma reciente favorece a {self._form_leader(fixture)}.",
            "El valor esperado compara el modelo con la cuota, no predice certeza.",
        ]
        return Prediction(
            fixture_id=fixture.id,
            model_version=self.model_version,
            data_source=data_source,
            probabilities=probabilities,
            implied_probabilities=implied,
            edge=edge,
            expected_value=expected_value,
            recommendation=recommendation,
            confidence=confidence,
            explanation=explanation,
            missing_data=[],
        )

    @staticmethod
    def _score(strength: float, form: float, home_advantage: float) -> float:
        return max(0.05, 0.5 + strength / 100 * 0.35 + (form - 0.5) * 0.35 + home_advantage)

    @staticmethod
    def _confidence(probabilities: dict[Outcome, float], fixture: Fixture) -> str:
        gap = max(probabilities.values()) - sorted(probabilities.values())[-2]
        if gap >= 0.18 and abs(fixture.home.strength - fixture.away.strength) >= 8:
            return "media"
        return "baja"

    @staticmethod
    def _form_leader(fixture: Fixture) -> str:
        return (
            fixture.home.name
            if fixture.home.recent_form >= fixture.away.recent_form
            else fixture.away.name
        )
