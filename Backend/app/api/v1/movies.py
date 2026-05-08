"""电影接口：list/get/create/update/delete/togglePin/count。"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import current_user, require_permissions
from app.exceptions import NotFound
from app.models import AuditAction, Movie, User
from app.permissions import Perm
from app.schemas import MovieCount, MovieCreate, MovieOut, MovieUpdate, OkResponse
from app.schemas.common import Page
from app.services import audit
from app.utils.debug_ndjson import debug_log
from app.utils.pagination import PageParams, build_page_meta, page_params

router = APIRouter(prefix="/movies", tags=["movies"])


def _serialize_list(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return []


def _to_out(movie: Movie) -> MovieOut:
    return MovieOut(
        id=movie.id,
        title=movie.title,
        original_title=movie.original_title,
        director=movie.director,
        cast=_serialize_list(movie.cast),
        genres=_serialize_list(movie.genres),
        year=movie.year,
        duration_minutes=movie.duration_minutes,
        rating=movie.rating,
        synopsis=movie.synopsis or "",
        cover_url=movie.cover_url,
        video_url=movie.video_url,
        stills=_serialize_list(movie.stills),
        tags=_serialize_list(movie.tags),
        pinned=bool(movie.pinned),
        owner_id=movie.owner_id,
        created_at=movie.created_at,
        updated_at=movie.updated_at,
    )


async def _reload(session: AsyncSession, movie_id: int) -> Movie:
    stmt = select(Movie).where(Movie.id == movie_id)
    return (await session.execute(stmt)).scalar_one()


@router.get("", response_model=Page[MovieOut], dependencies=[Depends(require_permissions(Perm.MOVIE_READ))])
async def list_movies(
    keyword: str | None = Query(None, max_length=200),
    genre: str | None = Query(None, max_length=80),
    year: int | None = Query(None),
    pinned: bool | None = Query(None),
    pp: PageParams = Depends(page_params),
    session: AsyncSession = Depends(get_session),
) -> Page[MovieOut]:
    stmt = select(Movie)
    count_stmt = select(func.count()).select_from(Movie)

    if keyword:
        like = f"%{keyword}%"
        cond = or_(
            Movie.title.ilike(like),
            Movie.original_title.ilike(like),
            Movie.director.ilike(like),
            Movie.synopsis.ilike(like),
            cast(Movie.tags, String).ilike(like),
            cast(Movie.cast, String).ilike(like),
            cast(Movie.genres, String).ilike(like),
        )
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    if genre:
        genre_like = f"%{genre}%"
        stmt = stmt.where(cast(Movie.genres, String).ilike(genre_like))
        count_stmt = count_stmt.where(cast(Movie.genres, String).ilike(genre_like))
    if year is not None:
        stmt = stmt.where(Movie.year == year)
        count_stmt = count_stmt.where(Movie.year == year)
    if pinned is not None:
        stmt = stmt.where(Movie.pinned.is_(pinned))
        count_stmt = count_stmt.where(Movie.pinned.is_(pinned))

    stmt = stmt.order_by(Movie.pinned.desc(), Movie.updated_at.desc(), Movie.id.desc())
    stmt = stmt.offset(pp.offset).limit(pp.page_size)

    # region agent log
    debug_log(
        run_id="pre-fix",
        hypothesis_id="H4",
        location="app/api/v1/movies.py:list_movies",
        message="list_movies query params and selected columns",
        data={
            "page": pp.page,
            "page_size": pp.page_size,
            "keyword": keyword,
            "genre": genre,
            "year": year,
            "pinned": pinned,
            "selected_columns": [str(c.key) for c in Movie.__table__.columns],
        },
    )
    # endregion
    try:
        rows = (await session.execute(stmt)).scalars().all()
    except Exception as exc:
        # region agent log
        debug_log(
            run_id="pre-fix",
            hypothesis_id="H5",
            location="app/api/v1/movies.py:list_movies",
            message="list_movies failed before count query",
            data={"error_type": exc.__class__.__name__, "error": str(exc)},
        )
        # endregion
        raise
    total = (await session.execute(count_stmt)).scalar_one()

    return Page[MovieOut](items=[_to_out(row) for row in rows], meta=build_page_meta(pp, total))


@router.get("/count", response_model=MovieCount, dependencies=[Depends(require_permissions(Perm.MOVIE_READ))])
async def count_movies(session: AsyncSession = Depends(get_session)) -> MovieCount:
    total = (await session.execute(select(func.count()).select_from(Movie))).scalar_one()
    return MovieCount(total=int(total))


@router.get("/{movie_id}", response_model=MovieOut, dependencies=[Depends(require_permissions(Perm.MOVIE_READ))])
async def get_movie(movie_id: int, session: AsyncSession = Depends(get_session)) -> MovieOut:
    movie = await session.get(Movie, movie_id)
    if not movie:
        raise NotFound("电影不存在")
    return _to_out(movie)


@router.post("", response_model=MovieOut, dependencies=[Depends(require_permissions(Perm.MOVIE_WRITE))])
async def create_movie(
    request: Request,
    body: MovieCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> MovieOut:
    movie = Movie(
        title=body.title.strip(),
        original_title=body.original_title or None,
        director=body.director or None,
        cast=list(body.cast or []),
        genres=list(body.genres or []),
        year=body.year,
        duration_minutes=body.duration_minutes,
        rating=body.rating or None,
        synopsis=body.synopsis or "",
        cover_url=body.cover_url or None,
        video_url=body.video_url or None,
        stills=list(body.stills or []),
        tags=list(body.tags or []),
        pinned=bool(body.pinned),
        owner_id=user.id,
    )
    session.add(movie)
    await session.flush()
    await audit.record(
        session,
        actor=user,
        action=AuditAction.create,
        target_type="movie",
        target_id=movie.id,
        summary=f"新建电影 {movie.title}",
        request=request,
    )
    movie = await _reload(session, movie.id)
    return _to_out(movie)


@router.patch("/{movie_id}", response_model=MovieOut, dependencies=[Depends(require_permissions(Perm.MOVIE_WRITE))])
async def update_movie(
    movie_id: int,
    request: Request,
    body: MovieUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> MovieOut:
    movie = await session.get(Movie, movie_id)
    if not movie:
        raise NotFound("电影不存在")

    payload = body.model_dump(exclude_unset=True)
    if "title" in payload and payload["title"] is not None:
        movie.title = payload["title"].strip()
    if "original_title" in payload:
        movie.original_title = payload["original_title"] or None
    if "director" in payload:
        movie.director = payload["director"] or None
    if "cast" in payload and payload["cast"] is not None:
        movie.cast = list(payload["cast"])
    if "genres" in payload and payload["genres"] is not None:
        movie.genres = list(payload["genres"])
    if "year" in payload:
        movie.year = payload["year"]
    if "duration_minutes" in payload:
        movie.duration_minutes = payload["duration_minutes"]
    if "rating" in payload:
        movie.rating = payload["rating"] or None
    if "synopsis" in payload and payload["synopsis"] is not None:
        movie.synopsis = payload["synopsis"]
    if "cover_url" in payload:
        movie.cover_url = payload["cover_url"] or None
    if "video_url" in payload:
        movie.video_url = payload["video_url"] or None
    if "stills" in payload and payload["stills"] is not None:
        movie.stills = list(payload["stills"])
    if "tags" in payload and payload["tags"] is not None:
        movie.tags = list(payload["tags"])
    if "pinned" in payload and payload["pinned"] is not None:
        movie.pinned = bool(payload["pinned"])

    await session.flush()
    await audit.record(
        session,
        actor=user,
        action=AuditAction.update,
        target_type="movie",
        target_id=movie.id,
        summary=f"更新电影 {movie.title}",
        request=request,
    )
    movie = await _reload(session, movie.id)
    return _to_out(movie)


@router.post("/{movie_id}/pin", response_model=MovieOut, dependencies=[Depends(require_permissions(Perm.MOVIE_WRITE))])
async def toggle_pin(
    movie_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> MovieOut:
    movie = await session.get(Movie, movie_id)
    if not movie:
        raise NotFound("电影不存在")
    movie.pinned = not bool(movie.pinned)
    await session.flush()
    await audit.record(
        session,
        actor=user,
        action=AuditAction.update,
        target_type="movie",
        target_id=movie.id,
        summary=("置顶" if movie.pinned else "取消置顶") + f" 电影 {movie.title}",
        request=request,
    )
    movie = await _reload(session, movie.id)
    return _to_out(movie)


@router.delete("/{movie_id}", response_model=OkResponse, dependencies=[Depends(require_permissions(Perm.MOVIE_DELETE))])
async def delete_movie(
    movie_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> OkResponse:
    movie = await session.get(Movie, movie_id)
    if not movie:
        raise NotFound("电影不存在")
    title = movie.title
    await session.delete(movie)
    await audit.record(
        session,
        actor=user,
        action=AuditAction.delete,
        target_type="movie",
        target_id=movie_id,
        summary=f"删除电影 {title}",
        request=request,
    )
    return OkResponse(message="deleted")
