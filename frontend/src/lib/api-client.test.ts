import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { API } from '../test/handlers'
import { ApiError, buildUrl, errorMessage, request } from './api-client'

describe('buildUrl', () => {
  it('prefixes the API and skips empty values', () => {
    const url = buildUrl('/tasks', { page: 2, tag: '', priority: undefined, pinned: false })
    expect(url).toBe(`${API}/tasks?page=2&pinned=false`)
  })

  it('repeats array values', () => {
    expect(buildUrl('/tasks', { status: ['todo', 'in_progress'] })).toBe(
      `${API}/tasks?status=todo&status=in_progress`,
    )
  })
})

describe('request', () => {
  it('returns parsed JSON', async () => {
    server.use(http.get(`${API}/tags`, () => HttpResponse.json([{ id: 1, name: 'work' }])))
    await expect(request('/tags')).resolves.toEqual([{ id: 1, name: 'work' }])
  })

  it('sends JSON bodies with the right headers', async () => {
    let received: { body: unknown; contentType: string | null } | undefined
    server.use(
      http.post(`${API}/tasks`, async ({ request: req }) => {
        received = { body: await req.json(), contentType: req.headers.get('content-type') }
        return HttpResponse.json({ id: 1 }, { status: 201 })
      }),
    )
    await request('/tasks', { method: 'POST', body: { title: 'x' } })
    expect(received).toEqual({ body: { title: 'x' }, contentType: 'application/json' })
  })

  it('returns undefined for 204 responses', async () => {
    server.use(http.delete(`${API}/tasks/1`, () => new HttpResponse(null, { status: 204 })))
    await expect(request('/tasks/1', { method: 'DELETE' })).resolves.toBeUndefined()
  })

  it('throws ApiError with the backend error shape', async () => {
    server.use(
      http.post(`${API}/tasks`, () =>
        HttpResponse.json(
          {
            error: {
              code: 'validation_error',
              message: 'title: String should have at least 1 character',
              details: [{ field: 'title', message: 'String should have at least 1 character' }],
            },
          },
          { status: 422 },
        ),
      ),
    )
    const error = await request('/tasks', { method: 'POST', body: {} }).catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({
      status: 422,
      code: 'validation_error',
      message: 'title: String should have at least 1 character',
    })
    expect((error as ApiError).details?.[0]?.field).toBe('title')
  })

  it('handles error responses without a JSON body', async () => {
    server.use(http.get(`${API}/tasks`, () => new HttpResponse('Bad gateway', { status: 502 })))
    await expect(request('/tasks')).rejects.toMatchObject({ status: 502, code: 'http_error' })
  })

  it('turns network failures into a friendly ApiError', async () => {
    server.use(http.get(`${API}/tasks`, () => HttpResponse.error()))
    await expect(request('/tasks')).rejects.toMatchObject({ status: 0, code: 'network_error' })
  })
})

describe('errorMessage', () => {
  it('reads messages from any error', () => {
    expect(errorMessage(new ApiError(404, 'not_found', 'Task 1 not found'))).toBe(
      'Task 1 not found',
    )
    expect(errorMessage(new Error('boom'))).toBe('boom')
    expect(errorMessage('weird')).toBe('Something went wrong')
  })
})
