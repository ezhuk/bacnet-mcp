import pytest

from bacnet_mcp.settings import Device, Settings
from bacnet_mcp.utils import get_device


def test_get_device():
    settings = Settings()
    with pytest.raises(RuntimeError) as e:
        get_device(settings, "Foo")
    assert "not found" in str(e.value)
    assert get_device(settings, host="10.0.0.1", port=47808) == (
        "10.0.0.1",
        47808,
    )
    settings.devices.append(Device(name="Foo", host="10.10.0.1", port=47808))
    assert get_device(settings, name="Foo") == ("10.10.0.1", 47808)
