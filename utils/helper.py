async def fetch(session, url):
    async with session.get(url) as response:
        assert response.status == 200
        return await response.text()