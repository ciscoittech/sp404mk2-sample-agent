import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import SortingTable from "src/components/react-tables/sorting/page";



const BCrumb = [
  {
    to: "/",
    title: "Home",
  },
  {
    title: "Sorting Table",
  },
];
function page() {
  return (
    <>
      <PageContainer title="React Sorting Table" description="this is React Sorting Table page">
        <Breadcrumb title="Sorting Table" items={BCrumb} />
        <SortingTable />
      </PageContainer>
    </>
  );
}

export default page;
