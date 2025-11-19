import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import StickyTable from "src/components/react-tables/sticky/page";

const BCrumb = [
    {
        to: "/",
        title: "Home",
    },
    {
        title: "Sticky Table",
    },
];
function page() {
    return (
        <>
            <PageContainer title="React Sticky Table" description="this is React Sticky Table page">
                <Breadcrumb title="Sticky Table" items={BCrumb} />
                <StickyTable />
            </PageContainer>
        </>
    );
}

export default page;
