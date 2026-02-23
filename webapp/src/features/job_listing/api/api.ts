import { client } from "@shared/api/client";
import type { JobListing } from "@features/job_listing/models";
import type { PaginatedResponse } from "@shared/api/common.dto";
import type { SortField } from "@shared/api/common.types";

export const getListingPage = async (page: number, size: number, sortFields: SortField[] = []): Promise<PaginatedResponse<JobListing>> => {
    const { data } = await client.get<PaginatedResponse<JobListing>>("/listing", {
        params: {
            page: page,
            size: size,
            order_by: sortFields.map((sf) => `${sf.name},${sf.direction}`)
        },
        paramsSerializer: { indexes: null }
    });

    return data;
}