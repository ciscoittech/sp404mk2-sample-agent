import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import FilteringTable from "src/components/react-tables/filter/page";

const BCrumb = [
  {
    to: "/",
    title: "Home",
  },
  {
    title: "Filter Table",
  },
];
function page() {
  return (
    <>
      <PageContainer title="React Filter Table" description="this is React  Filter Table page">
        <Breadcrumb title="Filter Table " items={BCrumb} />
        <FilteringTable />
      </PageContainer>
    </>
  );
}

export default page;
