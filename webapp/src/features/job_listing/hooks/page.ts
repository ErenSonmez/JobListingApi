import { useQuery } from "@tanstack/react-query";
import { getListingPage } from "@features/job_listing/api";

export const useListingPage = (page: number, size: number) => useQuery({
        queryKey: ["listing_page", page, size],
        queryFn: async () => await getListingPage(page, size),
    })
