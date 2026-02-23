import type { Column, PaginatedTableProps } from "./types"

export function PaginatedTable<T>({
  data,
  columns,
  getRowKey,

  elementCount,
  page,
  size,
  onPageChange,
  pageSizeOptions = [10, 25, 50, 100],
  onSizeChange,
  sortFields = [],
  onSortChange,
}: PaginatedTableProps<T>) {
  const pageCount = Math.ceil(elementCount / size);

  const handleSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newSize = Number(e.target.value);
    onSizeChange(newSize)
    onPageChange(1) // size değişince ilk sayfaya dön
  };

  const handleSort = (column: Column<T>) => {
    if (!column.sortKey) return

    const existing = sortFields.find((sf) => sf.name === column.sortKey)

    let newSorts = [...sortFields]

    if (!existing) {
      newSorts.push({ name: column.sortKey, direction: "asc" })
    }
    else if (existing.direction === "asc") {
      newSorts = newSorts.map((s) =>
        s.name === column.sortKey
          ? { ...s, direction: "desc" }
          : s
      )
    }
    else {
      newSorts = newSorts.filter((s) => s.name !== column.sortKey)
    }

    onSortChange(newSorts)
    onPageChange(1)
  }

  const getSortIndicator = (fieldName?: string) => {
    const index = sortFields.findIndex((sf) => sf.name === fieldName)
    if (index === -1) return null

    const direction = sortFields[index].direction
    return ` ${direction === "asc" ? "🔼" : "🔽"}(${index + 1})`
  }

  return (
    <div>
      <div style={{ marginBottom: 12 }}>
        <label>
          Page Size:{" "}
          <select value={size} onChange={handleSizeChange}>
            {pageSizeOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
      </div>
      <table>
        <thead>
          <tr>
            {columns.map((col, index) => (
              <th
                key={index}
                onClick={() => handleSort(col)}
                style={{ cursor: col.sortKey ? "pointer" : "default" }}>
                  {col.header}
                  {col.sortKey && getSortIndicator(col.sortKey)}
                </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {data.map((row) => (
            <tr key={getRowKey(row)}>
              {columns.map((col, colIndex) => (
                <td key={colIndex}>{col.getField(row)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: 16 }}>
        <button disabled={page === 1} onClick={() => onPageChange(page - 1)}>
          Previous
        </button>

        <span style={{ margin: "0 8px" }}>
          Page {page} / {pageCount}
        </span>

        <button disabled={page >= pageCount} onClick={() => onPageChange(page + 1)}>
          Next
        </button>
      </div>
    </div>
  )
}