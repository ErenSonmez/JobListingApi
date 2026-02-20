import { HomeSection } from "../components/HomeSection";
import { JobListingTable } from "@features/job_listing/components/JobListingTable";

export const HomePage = () => {
  return (
    <div>
      <HomeSection />
      <JobListingTable />
    </div>
  );
};