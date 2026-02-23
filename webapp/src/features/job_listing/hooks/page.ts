import { useQuery } from "@tanstack/react-query";
import { getListingPage } from "@features/job_listing/api";
import type { SortField } from "@shared/api/common.types";

export const useListingPage = (page: number, size: number, sortFields: SortField[] = []) => useQuery({
        queryKey: ["listing_page", page, size, sortFields],
        queryFn: async () => await getListingPage(page, size, sortFields),
    })
