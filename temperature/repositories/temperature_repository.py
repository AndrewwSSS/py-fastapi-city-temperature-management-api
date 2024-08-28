from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from datetime import datetime

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from city.repositories.city_repository import CityRepository
from db import models
from dependencies import get_session
from settings import settings
from temperature import schemas as temperature_schemas
from city import schemas as city_schemas

from city.services.city_service import CityService


class TemperatureRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_temperatures_list(
        self,
        city_id: int = None
    ) -> list[models.Temperature]:
        query = select(models.Temperature)
        if city_id:
            query = query.where(models.Temperature.city_id == city_id)

        temperature_list = await self.session.execute(query)
        return [temperature[0] for temperature in temperature_list.fetchall()]

    async def get_temperature_by_id(self, temperature_id: int):
        query = select(models.Temperature).where(models.Temperature.id == temperature_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_temperature(
        self,
        temperature: temperature_schemas.TemperatureCreate,
        session: AsyncSession = None
    ) -> models.Temperature:
        if session is None:
            session = self.session
        temperature_db = models.Temperature(
            city_id=temperature.city_id,
            temperature=temperature.temperature,
            date_time=temperature.date_time,
        )
        session.add(temperature_db)
        await session.commit()
        await session.refresh(temperature_db)
        return temperature_db

    async def fetch_city_temperature(
        self,
        city: models.City,
        client: httpx.AsyncClient
    ) -> models.Temperature | None:
        response = await client.get(
            settings.WEATHER_API_URL,
            params={"key": settings.API_KEY, "q": city.name},
        )
        json_response = response.json()
        if not json_response.get("current", False):
            # todo create some logs
            return
        temperature_schema = models.Temperature(
            temperature=json_response["current"]["temp_c"],
            city_id=city.id,
            date_time=datetime.now(),
        )
        return temperature_schema

    async def fetch_temperatures_for_all_cities(
        self
    ) -> None:
        city_repository = CityRepository(self.session)
        cities = await city_repository.get_cities_list()
        client = httpx.AsyncClient()
        results = await asyncio.gather(
            *[
                self.fetch_city_temperature(city, client)
                for city in cities
            ]
        )
        self.session.add_all(result for result in results if results)
        await self.session.commit()
        await client.aclose()

