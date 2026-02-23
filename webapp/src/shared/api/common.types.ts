export type SortDirection = "asc" | "desc"

export interface SortField {
    name: string,
    direction: SortDirection
}