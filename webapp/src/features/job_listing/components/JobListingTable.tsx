import { useState } from "react";
import { useListingPage } from "../hooks/page";
import { PaginatedTable } from "@shared/components/table";
import type { SortField } from "@shared/api/common.types";
import type { JobListing } from "../models";

export const JobListingTable = () => {
  const [ page, setPage ] = useState(1);
  const [ size, setSize ] = useState(10);
  const [sortFields, setSortFields] = useState<SortField[]>([]);

  const { data, isLoading } = useListingPage(page, size, sortFields);


  if(isLoading) {
    return (
      <section>
        <p>Loading...</p>
      </section>
    )
  }
  else if(!data) {
    return (
      <section>
        <p>Could not fetch data</p>
      </section>
    )
  }
  else {
    return (
      <section>
        <h1>Job listing page {page} - {size}</h1>
        <PaginatedTable<JobListing>
        data={data.items}
        columns={[
          { header: "ID", getField: (item) => item._id, sortKey: "id" },
          { header: "Title", getField: (item) => item.title, sortKey: "title" },
        ]}
        getRowKey={(item) => item._id}

        elementCount={data.element_count}
        page={page}
        onPageChange={setPage}
        size={size}
        onSizeChange={setSize}
        sortFields={sortFields}
        onSortChange={setSortFields}
      />
      </section>
    );
  }
};