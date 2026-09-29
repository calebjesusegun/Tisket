import { http, HttpResponse } from 'msw'
import { page } from './factories'

export const API = 'http://localhost:8000/api/v1'

/** Default handlers: an empty workspace. Tests override with server.use(...). */
export const handlers = [
  http.get(`${API}/tasks`, () => HttpResponse.json(page([]))),
  http.get(`${API}/notes`, () => HttpResponse.json(page([]))),
  http.get(`${API}/tags`, () => HttpResponse.json([])),
  http.get(`${API}/search`, () => HttpResponse.json(page([]))),
  http.get(`${API}/reminders/due-soon`, () => HttpResponse.json(page([]))),
  http.get(`${API}/reminders/overdue`, () => HttpResponse.json(page([]))),
  http.get(`${API}/reminders/notifications`, () => HttpResponse.json(page([]))),
]
