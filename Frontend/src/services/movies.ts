import { http } from './http'
import type { Movie, MovieCount, MovieCreate, MovieListQuery, MovieUpdate, OkResponse, PageResult } from './types'

export const moviesApi = {
  list(params: MovieListQuery = {}) {
    return http.get<PageResult<Movie>, PageResult<Movie>>('/v1/movies', { params })
  },
  count() {
    return http.get<MovieCount, MovieCount>('/v1/movies/count')
  },
  get(id: number) {
    return http.get<Movie, Movie>(`/v1/movies/${id}`)
  },
  create(payload: MovieCreate) {
    return http.post<Movie, Movie>('/v1/movies', payload)
  },
  update(id: number, payload: MovieUpdate) {
    return http.patch<Movie, Movie>(`/v1/movies/${id}`, payload)
  },
  togglePin(id: number) {
    return http.post<Movie, Movie>(`/v1/movies/${id}/pin`)
  },
  remove(id: number) {
    return http.delete<OkResponse, OkResponse>(`/v1/movies/${id}`)
  },
}
