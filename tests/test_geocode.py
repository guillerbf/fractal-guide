from fractal_guide.services.geocode import reverse_geocode


def test_reverse_geocode_fallback(monkeypatch):
    class DummyLocation:
        address = None
        raw = {}

    def fake_reverse(_self, *_args, **_kwargs):
        return None

    import fractal_guide.services.geocode as geocode

    monkeypatch.setattr(geocode._geolocator, "reverse", fake_reverse)
    out = reverse_geocode(1.23456, 2.34567)
    assert "1.23456" in out and "2.34567" in out


