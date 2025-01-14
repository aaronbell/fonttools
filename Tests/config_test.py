from fontTools.misc.configTools import AbstractConfig, Options
import pytest
from fontTools.config import (
    Config,
    ConfigUnknownOptionError,
    ConfigValueParsingError,
    ConfigValueValidationError,
)
from fontTools.ttLib import TTFont


def test_can_register_option():
    MY_OPTION = Config.register_option(
        name="tests:MY_OPTION",
        help="Test option, value should be True or False, default = True",
        default=True,
        parse=lambda v: v in ("True", "true", 1, True),
        validate=lambda v: v == True or v == False,
    )

    assert (
        MY_OPTION.help == "Test option, value should be True or False, default = True"
    )
    assert MY_OPTION.default == True
    assert MY_OPTION.parse("true") == True
    assert MY_OPTION.validate("hello") == False

    ttFont = TTFont(cfg={"tests:MY_OPTION": True})
    assert True == ttFont.cfg.get("tests:MY_OPTION")


COMPRESSION_LEVEL = "fontTools.otlLib.optimize.gpos:COMPRESSION_LEVEL"


def test_ttfont_has_config():
    ttFont = TTFont(cfg={COMPRESSION_LEVEL: 8})
    assert 8 == ttFont.cfg.get(COMPRESSION_LEVEL)


def test_ttfont_can_take_superset_of_fonttools_config():
    # Create MyConfig with all options from fontTools.config plus some
    my_options = Options()
    for name, option in Config.options.items():
        my_options.register_option(name, option)

    my_options.register("custom:my_option", "help", "default", str, any)

    class MyConfig(AbstractConfig):
        options = my_options

    ttFont = TTFont(cfg=MyConfig({"custom:my_option": "my_value"}))
    assert 0 == ttFont.cfg.get(COMPRESSION_LEVEL)
    assert "my_value" == ttFont.cfg.get("custom:my_option")


def test_no_config_returns_default_values():
    ttFont = TTFont()
    assert 0 == ttFont.cfg.get(COMPRESSION_LEVEL)
    assert 3 == ttFont.cfg.get(COMPRESSION_LEVEL, 3)


def test_can_set_config():
    ttFont = TTFont()
    ttFont.cfg.set(COMPRESSION_LEVEL, 5)
    assert 5 == ttFont.cfg.get(COMPRESSION_LEVEL)
    ttFont.cfg.set(COMPRESSION_LEVEL, 6)
    assert 6 == ttFont.cfg.get(COMPRESSION_LEVEL)


def test_different_ttfonts_have_different_configs():
    cfg = Config({COMPRESSION_LEVEL: 5})
    ttFont1 = TTFont(cfg=cfg)
    ttFont2 = TTFont(cfg=cfg)
    ttFont2.cfg.set(COMPRESSION_LEVEL, 6)
    assert 5 == ttFont1.cfg.get(COMPRESSION_LEVEL)
    assert 6 == ttFont2.cfg.get(COMPRESSION_LEVEL)


def test_cannot_set_inexistent_key():
    with pytest.raises(ConfigUnknownOptionError):
        TTFont(cfg={"notALib.notAModule.inexistent": 4})


def test_value_not_parsed_by_default():
    # Note: value given as a string
    with pytest.raises(ConfigValueValidationError):
        TTFont(cfg={COMPRESSION_LEVEL: "8"})


def test_value_gets_parsed_if_asked():
    # Note: value given as a string
    ttFont = TTFont(cfg=Config({COMPRESSION_LEVEL: "8"}, parse_values=True))
    assert 8 == ttFont.cfg.get(COMPRESSION_LEVEL)


def test_value_parsing_can_error():
    with pytest.raises(ConfigValueParsingError):
        TTFont(
            cfg=Config(
                {COMPRESSION_LEVEL: "not an int"},
                parse_values=True,
            )
        )


def test_value_gets_validated():
    # Note: 12 is not a valid value for GPOS compression level (must be in 0-9)
    with pytest.raises(ConfigValueValidationError):
        TTFont(cfg={COMPRESSION_LEVEL: 12})


def test_implements_mutable_mapping():
    cfg = Config()
    cfg[COMPRESSION_LEVEL] = 2
    assert 2 == cfg[COMPRESSION_LEVEL]
    assert [COMPRESSION_LEVEL] == list(iter(cfg))
    assert 1 == len(cfg)
    del cfg[COMPRESSION_LEVEL]
    assert 0 == cfg[COMPRESSION_LEVEL]
    assert [] == list(iter(cfg))
    assert 0 == len(cfg)
