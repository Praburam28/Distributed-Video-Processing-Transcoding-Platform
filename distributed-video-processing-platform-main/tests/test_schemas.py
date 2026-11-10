from shared.schemas import ProcessRequest
def test_default_resolutions():
    req=ProcessRequest()
    assert req.resolutions==["360p","720p"]
def test_configurable_resolutions():
    req=ProcessRequest(resolutions=["360p","1080p"])
    assert req.resolutions==["360p","1080p"]
