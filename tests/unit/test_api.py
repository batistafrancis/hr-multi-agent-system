from unittest.mock import AsyncMock

import pytest

from src.api import main


@pytest.mark.asyncio
async def test_generate_role_returns_final_report(monkeypatch):
    report = "# HR Innovation Report: AI Ethics Manager"
    monkeypatch.setattr(
        main.graph,
        "ainvoke",
        AsyncMock(
            return_value={
                "final_report": report,
                "role_description": "AI Ethics Manager role description",
            }
        ),
    )

    response = await main.generate_role("AI Ethics Manager")

    assert response["report"] == report
