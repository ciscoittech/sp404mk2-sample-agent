import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ReactDenseTable from 'src/components/react-tables/dense/page';


const BCrumb = [
  {
    to: "/",
    title: "Home",
  },
  {
    title: "Dense Table ",
  },
];
function page() {
  return (
    <>
      <PageContainer title="React Dense Table" description="this is React Dense Table page">

        <Breadcrumb title="Dense Table " items={BCrumb} />
        <div>
          <ReactDenseTable />
        </div>
      </PageContainer>
    </>
  );
}

export default page;
