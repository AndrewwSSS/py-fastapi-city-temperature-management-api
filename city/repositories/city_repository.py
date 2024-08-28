from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from city import schemas
from db import models


class CityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_cities_list(self):
        query = select(models.City)
        cities_list = await self.session.execute(query)
        return [city[0] for city in cities_list.fetchall()]

    async def get_city_by_id(self, city_id: int):
        query = select(models.City).where(models.City.id == city_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_city_by_id(
        self,
        city_id: int,
        city: schemas.CityUpdate,
    ) -> models.City | None:
        db_city = await self.get_city_by_id(city_id)
        if not db_city:
            return None
        db_city.name = city.name
        db_city.additional_info = city.additional_info
        await self.session.commit()
        await self.session.refresh(db_city)
        return db_city

    async def create_city(self, city: schemas.CityCreate):
        db_city = models.City(
            name=city.name,
            additional_info=city.additional_info
        )
        self.session.add(db_city)
        await self.session.commit()
        await self.session.refresh(db_city)
        return db_city

    async def delete_city_by_id(self, city_id: int) -> bool:
        db_city = await self.get_city_by_id(city_id)
        if not db_city:
            return False
        await self.session.delete(db_city)
        await self.session.commit()
        return True
