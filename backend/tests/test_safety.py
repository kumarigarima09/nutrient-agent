from app.services.safety_service import SafetyService


def test_safety_check_normal_query():
    text = "What is a good high-protein breakfast with eggs and oats?"
    result = SafetyService.check_input_safety(text)
    assert result["is_safe_for_automated_planning"] is True
    assert result["requires_medical_referral"] is False


def test_safety_check_eating_disorder_trigger():
    text = "I have been starving myself and taking laxatives to lose weight quickly"
    result = SafetyService.check_input_safety(text)
    assert result["is_safe_for_automated_planning"] is False
    assert result["requires_medical_referral"] is True
    assert "eating_disorder" in result["flagged_categories"]
    assert "HEALTH NOTICE" in result["disclaimer"]


def test_safety_check_chronic_kidney_disease():
    text = "I have chronic kidney disease and high creatinine, plan my diet"
    result = SafetyService.check_input_safety(text)
    assert result["is_safe_for_automated_planning"] is False
    assert result["requires_medical_referral"] is True
    assert "kidney_disease" in result["flagged_categories"]


def test_safety_check_pregnancy():
    text = "I am 4 months pregnant, should I go on a caloric deficit?"
    result = SafetyService.check_input_safety(text)
    assert result["is_safe_for_automated_planning"] is False
    assert "pregnancy_lactation" in result["flagged_categories"]
