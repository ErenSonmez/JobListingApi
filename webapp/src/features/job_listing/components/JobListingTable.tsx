import { useListingPage } from "../hooks/page";

export const JobListingTable = () => {
  const { data, isLoading } = useListingPage(1, 10);

  if(isLoading) {
    return (
      <section>
        <p>Loading...</p>
      </section>
    )
  }
  else if(data) {
    return (
      <section>
        <h1>Job listing page 1 - 10</h1>
        <p>{data.items[0].title}</p>
      </section>
    );
  }
  else {
    return (
      <section>
        <p>Could not fetch data</p>
      </section>
    )
  }
};