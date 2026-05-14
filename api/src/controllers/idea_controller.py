import csv
import io
import json

from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.lib.db.models.user import User
from src.lib.db.models.idea import Idea
from src.lib.utils.error import ApiError


SCORE_WEIGHTS = {
    "market_size": 0.30,
    "innovation": 0.25,
    "feasibility": 0.25,
    "competition_advantage": 0.20,
}


def _clamp(value: float, low: float = 0.0, high: float = 10.0) -> float:
    return max(low, min(high, value))


def calculate_score(ai_data: dict) -> float:
    """
    Basit ağırlıklı skorlama (0-100).

    Kriterler AI çıktısından heuristik olarak türetilir:
      - market_size:           market_analysis.market_size metninin uzunluğu/varlığı
      - innovation:            value_proposition + strengths sayısı
      - feasibility:           weaknesses ve threats az ise yüksek
      - competition_advantage: opportunities sayısı vs competitors sayısı
    """
    swot = ai_data.get("swot_analysis") or {}
    market = ai_data.get("market_analysis") or {}

    strengths = swot.get("strengths") or []
    weaknesses = swot.get("weaknesses") or []
    opportunities = swot.get("opportunities") or []
    threats = swot.get("threats") or []
    competitors = market.get("competitors") or []
    market_size_text = (market.get("market_size") or "").strip()
    value_prop = (ai_data.get("value_proposition") or "").strip()

    market_size_score = _clamp(
        (5.0 if market_size_text else 0.0) + min(len(market_size_text) / 60.0, 5.0)
    )
    innovation_score = _clamp(
        (3.0 if value_prop else 0.0) + len(strengths) * 1.5
    )
    feasibility_score = _clamp(
        10.0 - (len(weaknesses) * 1.5) - (len(threats) * 1.0)
    )
    competition_score = _clamp(
        5.0 + (len(opportunities) * 1.0) - (len(competitors) * 0.8)
    )

    weighted = (
        market_size_score * SCORE_WEIGHTS["market_size"]
        + innovation_score * SCORE_WEIGHTS["innovation"]
        + feasibility_score * SCORE_WEIGHTS["feasibility"]
        + competition_score * SCORE_WEIGHTS["competition_advantage"]
    )

    return round(weighted * 10.0, 2)


async def list_ideas(current_user: User, db: AsyncSession):
    try:
        if not current_user:
            raise ApiError.unauthorized("User not authenticated.")

        result = await db.execute(
            select(Idea)
            .where(Idea.user_id == current_user.id)
            .order_by(Idea.created_at.desc())
        )
        ideas = result.scalars().all()

        return JSONResponse(status_code=200, content={
            "success": True,
            "data": [
                {
                    "id": idea.id,
                    "title": idea.title,
                    "score": idea.score,
                    "created_at": idea.created_at.isoformat() if idea.created_at else None,
                }
                for idea in ideas
            ],
        })
    except ApiError as error:
        return JSONResponse(
            status_code=error.status_code,
            content={"success": False, "error": error.message},
        )
    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(error) or "Failed to list ideas"},
        )


async def _get_owned_idea(idea_id: int, current_user: User, db: AsyncSession) -> Idea:
    if not current_user:
        raise ApiError.unauthorized("User not authenticated.")

    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalars().first()

    if idea is None:
        raise ApiError.not_found("Idea not found.")
    if idea.user_id != current_user.id:
        raise ApiError.forbidden("You do not have access to this idea.")
    return idea


async def get_idea(idea_id: int, current_user: User, db: AsyncSession):
    try:
        idea = await _get_owned_idea(idea_id, current_user, db)
        return JSONResponse(status_code=200, content={
            "success": True,
            "data": {
                "id": idea.id,
                "user_id": idea.user_id,
                "title": idea.title,
                "executive_summary": idea.executive_summary,
                "problem_statement": idea.problem_statement,
                "target_audience": idea.target_audience,
                "value_proposition": idea.value_proposition,
                "swot_analysis": idea.swot_analysis,
                "market_analysis": idea.market_analysis,
                "business_model": idea.business_model,
                "score": idea.score,
                "created_at": idea.created_at.isoformat() if idea.created_at else None,
                "updated_at": idea.updated_at.isoformat() if idea.updated_at else None,
            },
        })
    except ApiError as error:
        return JSONResponse(
            status_code=error.status_code,
            content={"success": False, "error": error.message},
        )
    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(error) or "Failed to get idea"},
        )


async def delete_idea(idea_id: int, current_user: User, db: AsyncSession):
    try:
        idea = await _get_owned_idea(idea_id, current_user, db)
        await db.delete(idea)
        await db.commit()
        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Idea deleted successfully.",
        })
    except ApiError as error:
        return JSONResponse(
            status_code=error.status_code,
            content={"success": False, "error": error.message},
        )
    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(error) or "Failed to delete idea"},
        )


async def export_csv(idea_id: int, current_user: User, db: AsyncSession):
    try:
        idea = await _get_owned_idea(idea_id, current_user, db)

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Field", "Value"])
        writer.writerow(["ID", idea.id])
        writer.writerow(["Title", idea.title])
        writer.writerow(["Executive Summary", idea.executive_summary or ""])
        writer.writerow(["Problem Statement", idea.problem_statement or ""])
        writer.writerow(["Target Audience", idea.target_audience or ""])
        writer.writerow(["Value Proposition", idea.value_proposition or ""])
        writer.writerow(["Business Model", idea.business_model or ""])
        writer.writerow(["Score", idea.score if idea.score is not None else ""])
        writer.writerow([
            "SWOT Analysis",
            json.dumps(idea.swot_analysis, ensure_ascii=False) if idea.swot_analysis else "",
        ])
        writer.writerow([
            "Market Analysis",
            json.dumps(idea.market_analysis, ensure_ascii=False) if idea.market_analysis else "",
        ])

        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="idea_{idea.id}.csv"'
            },
        )
    except ApiError as error:
        return JSONResponse(
            status_code=error.status_code,
            content={"success": False, "error": error.message},
        )
    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(error) or "Failed to export CSV"},
        )


async def export_pdf(idea_id: int, current_user: User, db: AsyncSession):
    try:
        idea = await _get_owned_idea(idea_id, current_user, db)

        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import cm

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
        )
        styles = getSampleStyleSheet()
        h_style = styles["Heading2"]
        body_style = ParagraphStyle("body", parent=styles["BodyText"], leading=14)

        story = []
        story.append(Paragraph(idea.title or "Idea", styles["Title"]))
        story.append(Spacer(1, 0.4 * cm))
        if idea.score is not None:
            story.append(Paragraph(f"<b>Score:</b> {idea.score} / 100", body_style))
            story.append(Spacer(1, 0.3 * cm))

        sections = [
            ("Executive Summary", idea.executive_summary),
            ("Problem Statement", idea.problem_statement),
            ("Target Audience", idea.target_audience),
            ("Value Proposition", idea.value_proposition),
            ("Business Model", idea.business_model),
        ]
        for title, content in sections:
            if not content:
                continue
            story.append(Paragraph(title, h_style))
            story.append(Paragraph(content.replace("\n", "<br/>"), body_style))
            story.append(Spacer(1, 0.3 * cm))

        if idea.swot_analysis:
            story.append(Paragraph("SWOT Analysis", h_style))
            for key in ("strengths", "weaknesses", "opportunities", "threats"):
                items = idea.swot_analysis.get(key) or []
                if not items:
                    continue
                story.append(Paragraph(f"<b>{key.title()}</b>", body_style))
                for item in items:
                    story.append(Paragraph(f"- {item}", body_style))
                story.append(Spacer(1, 0.2 * cm))

        if idea.market_analysis:
            story.append(Paragraph("Market Analysis", h_style))
            ms = idea.market_analysis.get("market_size")
            tr = idea.market_analysis.get("trends")
            comps = idea.market_analysis.get("competitors") or []
            if ms:
                story.append(Paragraph(f"<b>Market Size:</b> {ms}", body_style))
            if tr:
                story.append(Paragraph(f"<b>Trends:</b> {tr}", body_style))
            if comps:
                story.append(Paragraph("<b>Competitors:</b>", body_style))
                for c in comps:
                    story.append(Paragraph(f"- {c}", body_style))

        doc.build(story)
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="idea_{idea.id}.pdf"'
            },
        )
    except ApiError as error:
        return JSONResponse(
            status_code=error.status_code,
            content={"success": False, "error": error.message},
        )
    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(error) or "Failed to export PDF"},
        )
