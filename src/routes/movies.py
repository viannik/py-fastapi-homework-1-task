from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, MovieModel
from schemas.movies import MovieListResponseSchema, MovieDetailResponseSchema
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate


router = APIRouter()

@router.get("/movies/", response_model=MovieListResponseSchema)
async def read_movies(
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=10, ge=1, le=20, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    page_data = await paginate(
        db,
        select(MovieModel),
        params=Params(page=page, size=per_page),
    )

    if page_data.total == 0:
        raise HTTPException(status_code=404, detail="No movies found.")

    total_pages = page_data.pages

    if page > total_pages:
        raise HTTPException(status_code=404, detail="No movies found.")

    movies = page_data.items

    base_path = "/api/v1/theater/movies/"
    prev_page = None if page <= 1 else f"{base_path}?page={page - 1}&per_page={per_page}"
    next_page = None if page >= total_pages else f"{base_path}?page={page + 1}&per_page={per_page}"

    return {
        "movies": movies,
        "prev_page": prev_page,
        "next_page": next_page,
        "total_pages": total_pages,
        "total_items": page_data.total,
    }


@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
async def read_movie_by_id(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
):
    movie = await db.get(MovieModel, movie_id)

    if movie is None:
        raise HTTPException(status_code=404, detail="Movie with the given ID was not found.")

    return movie
