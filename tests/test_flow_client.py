"""Kiểm thử cấu hình selector và module FlowBrowser."""

import pytest
from playwright_pipeline.flow_client import FlowBrowser, FlowError, load_flow_selectors


def test_load_flow_selectors():
    selectors = load_flow_selectors()
    assert "prompt_box" in selectors
    assert "generate_button" in selectors
    assert "aspect_16_9" in selectors
    assert len(selectors["prompt_box"]) >= 1


def test_flow_error_raised_when_uninitialized():
    fb = FlowBrowser()
    with pytest.raises(FlowError):
        _ = fb.page
