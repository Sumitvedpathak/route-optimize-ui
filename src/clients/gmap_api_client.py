import os
import httpx
from datetime import datetime, timedelta, timezone

EST = timezone(timedelta(hours=-5))

async def get_route_data(source: str, destination: str, waypoints: list[str] = None):
    url = "https://route-optimize-api-670264226001.us-central1.run.app/optimize-route"
    dt = datetime.now(EST).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")
    print(dt)
    params = {
        "source": source,
        "destination": destination,
        "waypoints": waypoints if waypoints else [],
        "departure_time": dt
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=params)
        return response.json()

if __name__ == "__main__":
    import asyncio
    asyncio.run(get_route_data("34 Finney Terrace, Milton, ON, Canada", 
    "34 Finney Terrace, Milton, ON, Canada", 
    ["6301 Silver Dart Dr, Mississauga, ON L5P 1B2",
        "Toronto Pearson International Airport",
        "55 Mill St, Toronto, ON M5A 3C4",
        "320 Queen St E, Brampton, ON L6V 1C2"]))