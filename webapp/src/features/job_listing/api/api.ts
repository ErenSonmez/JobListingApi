import { client } from "@shared/api/client";
import type { JobListing } from "@features/job_listing/models";
import type { PaginatedResponse } from "@shared/api/common.dto";

export const getListingPage = async (page: number, size: number): Promise<PaginatedResponse<JobListing>> => {
    const { data } = await client.get<PaginatedResponse<JobListing>>("/listing", {
        params: {
            page: page,
            size: size,
        }
    });

    return data;
}