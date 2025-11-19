import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ExpandingTable from "src/components/react-tables/expanding/page";

const BCrumb = [
    {
        to: "/",
        title: "Home",
    },
    {
        title: "Expanding Table",
    },
];
function page() {
    return (
        <>
            <PageContainer title="React Expanding Table" description="this is React  Expanding Table page">
                <Breadcrumb title="Expanding Table " items={BCrumb} />
                <ExpandingTable />
            </PageContainer>
        </>
    );
}

export default page;
