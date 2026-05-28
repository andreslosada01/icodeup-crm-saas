from __future__ import annotations

import csv
import io
import re
import unicodedata
from datetime import datetime, timedelta

from app.models import Customer, ManagementActivity, PaymentPromise


def risk_from_dpd(dpd: int, balance: int) -> str:
    if dpd >= 60 or balance >= 20_000_000:
        return "Alto"
    if dpd >= 15 or balance >= 5_000_000:
        return "Medio"
    return "Bajo"


def priority_score(dpd: int, balance: int, risk: str, status_value: str) -> int:
    risk_score = {"Alto": 30, "Medio": 18, "Bajo": 8}.get(risk, 12)
    status_score = {"Promesa": 12, "Sin contacto": 10, "Escalado": 14, "Disputa": 12}.get(status_value, 5)
    return min(100, risk_score + min(35, round(dpd / 3)) + min(25, round(balance / 2_000_000)) + status_score)


def next_action_for(status_value: str, risk: str) -> str:
    if status_value == "Promesa":
        return "Confirmar cumplimiento de promesa"
    if status_value == "Escalado":
        return "Seguimiento lider y ruta especializada"
    if status_value == "Disputa":
        return "Solicitar soporte documental y congelar automatizaciones"
    if risk == "Alto":
        return "Contacto prioritario y alternativa de normalizacion"
    return "Programar nueva gestion"


def normalize_header(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", normalized.lower()).strip("_")


def pick(record: dict[str, str], keys: list[str]) -> str:
    for key in keys:
        value = record.get(normalize_header(key))
        if value:
            return value.strip()
    return ""


def parse_money(value: str) -> int:
    cleaned = re.sub(r"[^\d.-]", "", value or "")
    try:
        return max(0, round(float(cleaned)))
    except ValueError:
        return 0


def parse_csv_records(csv_text: str) -> list[dict[str, str]]:
    first_line = csv_text.splitlines()[0] if csv_text.splitlines() else ""
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
    reader = csv.reader(io.StringIO(csv_text), delimiter=delimiter)
    rows = [row for row in reader if any(cell.strip() for cell in row)]
    if len(rows) < 2:
        return []
    headers = [normalize_header(header) for header in rows[0]]
    return [dict(zip(headers, row, strict=False)) for row in rows[1:]]


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, value))


def semaphore_status(score: int) -> str:
    if score >= 75:
        return "green"
    if score >= 45:
        return "yellow"
    return "red"


def recovery_probability(customer: Customer, activities: list[ManagementActivity], promises: list[PaymentPromise]) -> float:
    score = 28.0
    score += {"Bajo": 20, "Medio": 10, "Alto": -8}.get(customer.risk, 0)
    score += {"Alta": 16, "Media": 7, "Baja": -8}.get(customer.contactability, 0)
    score += {"Promesa": 22, "Contactado": 14, "Pago parcial": 18, "Sin contacto": -12, "Escalado": -6, "Disputa": -14}.get(customer.status, 0)
    score -= min(28, customer.dpd * 0.22)
    score += min(14, len(activities) * 3)
    if any(item.status == "Vigente" for item in promises):
        score += 12
    if customer.phone:
        score += 4
    if customer.email:
        score += 3
    return clamp(score, 3, 92) / 100


def activity_is_stale(customer: Customer, now: datetime) -> bool:
    if customer.last_contact_at is None:
        return True
    return customer.last_contact_at < now - timedelta(days=7)


def aging_bucket_label(dpd: int) -> str:
    if dpd <= 15:
        return "0-15"
    if dpd <= 30:
        return "16-30"
    if dpd <= 60:
        return "31-60"
    if dpd <= 90:
        return "61-90"
    return "90+"
