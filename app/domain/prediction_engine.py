"""Servicio de dominio para calcular predicciones explicables."""
import math

from app.domain.models import Fixture, Odds, Outcome, Prediction

# Parámetros del baseline. Son explícitos y versionados para poder auditar cambios.
DRAW_BASE = 0.28
DRAW_SKEW = 0.12
DRAW_MIN = 0.16
DRAW_MAX = 0.32
STRENGTH_WEIGHT = 1.15
FORM_WEIGHT = 0.90
HOME_ADVANTAGE = 0.10
SLOPE = 2.00
DIVERGENCE_THRESHOLD = 0.15


def _sigmoid(value: float) -> float:
    return 1 / (1 + math.exp(-value))


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class PredictionEngine:
    """Reglas puras del baseline; no conoce HTTP, persistencia ni proveedores.

    Modelo: el efecto neto entre equipos se transforma en una probabilidad
    condicional sin empate mediante una logística, y la masa de empate depende
    de lo equilibrado que sea el partido. Es una aproximación simple y auditable,
    no un modelo validado para tomar decisiones de apuesta.
    """

    model_version = "baseline-v0.2"

    def predict(self, fixture: Fixture, data_source: str) -> Prediction:
        effect = self._effect(fixture)
        probabilities = self._probabilities(effect)
        implied = self._implied_probabilities(fixture.odds)
        margin = sum(implied.values()) - 1
        edge = {outcome: probabilities[outcome] - implied[outcome] for outcome in Outcome}
        expected_value = {
            outcome: probabilities[outcome] * getattr(fixture.odds, outcome.value) - 1
            for outcome in Outcome
        }
        best = max(expected_value, key=expected_value.get)
        likely = max(probabilities, key=probabilities.get)
        divergence = max(abs(edge[outcome]) for outcome in Outcome)
        warnings: list[str] = []
        if divergence >= DIVERGENCE_THRESHOLD:
            warnings.append(
                f"El modelo diverge {divergence:.1%} del mercado: revisa cuotas o "
                "entrada de datos antes de interpretar la señal."
            )
        confidence = self._confidence(probabilities, fixture, divergence)
        recommendation = (
            f"Mayor probabilidad: {likely.value} ({probabilities[likely]:.1%})"
            + (
                f" · Señal de valor: {best.value} (EV {expected_value[best]:+.1%})"
                if expected_value[best] > 0.02
                else " · Sin señal de valor clara"
            )
        )
        explanation = [
            f"Efecto neto local-visitante: {effect:+.3f} (fuerza, forma y localía).",
            f"Masa de empate asignada: {probabilities[Outcome.DRAW]:.1%}.",
            f"Margen implícito de la casa: {margin:.1%}.",
            "El valor esperado compara el modelo con la cuota; no predice certezas.",
        ]
        return Prediction(
            fixture_id=fixture.id,
            model_version=self.model_version,
            data_source=data_source,
            probabilities=probabilities,
            implied_probabilities=implied,
            fair_odds={outcome: 1 / probabilities[outcome] for outcome in Outcome},
            bookmaker_margin=margin,
            edge=edge,
            expected_value=expected_value,
            recommendation=recommendation,
            confidence=confidence,
            explanation=explanation,
            warnings=warnings,
            missing_data=[],
        )

    @staticmethod
    def _effect(fixture: Fixture) -> float:
        return (
            (fixture.home.strength - fixture.away.strength) / 100 * STRENGTH_WEIGHT
            + (fixture.home.recent_form - fixture.away.recent_form) * FORM_WEIGHT
            + HOME_ADVANTAGE
        )

    @staticmethod
    def _probabilities(effect: float) -> dict[Outcome, float]:
        draw = _clamp(DRAW_BASE - DRAW_SKEW * abs(effect), DRAW_MIN, DRAW_MAX)
        remaining = 1 - draw
        home_share = _sigmoid(effect * SLOPE)
        return {
            Outcome.HOME: remaining * home_share,
            Outcome.DRAW: draw,
            Outcome.AWAY: remaining * (1 - home_share),
        }

    @staticmethod
    def _implied_probabilities(odds: Odds) -> dict[Outcome, float]:
        return {outcome: 1 / getattr(odds, outcome.value) for outcome in Outcome}

    @staticmethod
    def _confidence(
        probabilities: dict[Outcome, float], fixture: Fixture, divergence: float
    ) -> str:
        ordered = sorted(probabilities.values(), reverse=True)
        separation = ordered[0] - ordered[1]
        balanced_gap = abs(fixture.home.strength - fixture.away.strength)
        if divergence >= DIVERGENCE_THRESHOLD:
            return "muy baja"
        if separation >= 0.12 and balanced_gap >= 5:
            return "alta"
        if separation >= 0.06 or balanced_gap >= 4:
            return "media"
        return "baja"
