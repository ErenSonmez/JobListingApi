import type { SortField } from "@shared/api/common.types"
import React from "react"

export interface Column<T> {
    header: string,
    getField: (item: T) => React.ReactNode,
    sortKey?: string,
}

export interface TableProps<T>  {
    data: T[],
    columns: Column<T>[],
    getRowKey: (item: T) => React.Key,
}

export interface PaginatedTableProps<T> extends TableProps<T> {
    elementCount: number,
    page: number,
    size: number,
    onPageChange: (page: number) => void,
    pageSizeOptions?: number[],
    onSizeChange: (size: number) => void,
    sortFields?: SortField[],
    onSortChange: (sortFields: SortField[]) => void,
}