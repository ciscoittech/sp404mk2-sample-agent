import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import EmptyTable from "src/components/react-tables/empty/page";


const BCrumb = [
    {
        to: "/",
        title: "Home",
    },
    {
        title: "Empty Table",
    },
];
function page() {
    return (
        <>
            <PageContainer title="React Empty Table" description="this is React Empty Table page">
                <Breadcrumb title="Empty Table " items={BCrumb} />
                <EmptyTable />
            </PageContainer>
        </>
    );
}

export default page;
