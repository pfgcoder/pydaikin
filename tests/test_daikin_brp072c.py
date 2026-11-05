from unittest.mock import MagicMock

import pytest

from pydaikin.daikin_brp072c import DaikinBRP072C


@pytest.mark.parametrize(
    'values, expected',
    [
        ({'hhum': '50'}, 50.0),
        ({'hhum': '25.5'}, 25.5),
        ({'hhum': '-'}, None),
        ({'hhum': '--'}, None),
        ({}, None),
        ({'hhum': None}, None),
        ({'hhum': 'invalid'}, None),
    ],
)
def test_humidity(values, expected):
    """Test the humidity property for DaikinBRP072C."""
    mock_session = MagicMock()
    device = DaikinBRP072C('127.0.0.1', session=mock_session, key='dummy_key')
    device.values.update(values)
    assert device.humidity == expected


@pytest.mark.parametrize(
    'values, expected',
    [
        ({'hhum': '50'}, True),
        ({'hhum': '25.5'}, True),
        ({'hhum': '-'}, False),
        ({'hhum': '--'}, False),
        ({}, False),
        ({'hhum': None}, False),
        ({'hhum': 'invalid'}, False),
    ],
)
def test_support_humidity(values, expected):
    """Test the support_humidity property for DaikinBRP072C."""
    mock_session = MagicMock()
    device = DaikinBRP072C('127.0.0.1', session=mock_session, key='dummy_key')
    device.values.update(values)
    assert device.support_humidity is expected


def test_init_cipher_sslerror(monkeypatch):
    """Test __init__ when set_ciphers raises ssl.SSLError."""
    import ssl

    mock_session = MagicMock()

    def raise_sslerror(self, ciphers):
        raise ssl.SSLError('cipher not supported')

    monkeypatch.setattr(ssl.SSLContext, 'set_ciphers', raise_sslerror)
    device = DaikinBRP072C('127.0.0.1', session=mock_session, key='dummy_key')
    assert device._key == 'dummy_key'


def test_uuid_is_random_when_not_given():
    """Without a uuid, each device object registers its own random one."""
    first = DaikinBRP072C('192.168.1.100', session=MagicMock(), key='key')
    second = DaikinBRP072C('192.168.1.100', session=MagicMock(), key='key')

    assert first.headers["X-Daikin-uuid"] != second.headers["X-Daikin-uuid"]
    assert len(first.headers["X-Daikin-uuid"]) == 32


def test_given_uuid_is_used():
    """A given uuid is sent without its dashes."""
    device = DaikinBRP072C(
        '192.168.1.100',
        session=MagicMock(),
        key='key',
        uuid='12345678-1234-5678-1234-567812345678',
    )

    assert device.headers["X-Daikin-uuid"] == "12345678123456781234567812345678"
