from http.client import HTTPException

import httpx

from db import models
from temperature import schemas
from temperature.repositories.temperature_repository import TemperatureRepository


class TemperatureService:
    def __init__(self, temperature_repository: TemperatureRepository) -> None:
        self.temperature_repository = temperature_repository

    async def get_temperature_list(self) -> list[models.Temperature]:
        return await self.temperature_repository.get_temperatures_list()

    async def get_temperature(self, temperature_id: int) -> models.Temperature:
        temperature = await self.temperature_repository.get_temperature_by_id(
            temperature_id
        )
        if not temperature:
            raise HTTPException(status_code=404, detail="Temperature not found")
        return temperature

    async def create_temperature(
        self,
        temperature: schemas.TemperatureCreate
    ) -> models.Temperature:
        return await self.temperature_repository.create_temperature(
            temperature
        )

    async def fetch_city_temperature(
        self,
        city: models.City,
        client: httpx.AsyncClient
    ) -> models.Temperature | None:
        city = await self.temperature_repository.fetch_city_temperature(
            city,
            client
        )
        if not city:
            return
        return city

    async def update_cities_temperatures(
        self
    ) -> None:
        await self.temperature_repository.fetch_temperatures_for_all_cities()
