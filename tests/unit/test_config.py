from repochronicle.config import Settings


def test_settings_validate_limits() -> None:
    settings = Settings(_env_file=None, max_context_chars=12000, embedding_dimensions=384)
    assert settings.max_context_chars == 12000
    assert settings.embedding_dimensions == 384
