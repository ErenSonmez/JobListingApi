export interface PaginatedResponse<T> {
    items: T[],
    page: number,
    size: number,
    element_count: number,
}