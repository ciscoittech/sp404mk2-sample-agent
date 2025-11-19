import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ReactColumnVisibilityTable from 'src/components/react-tables/column-visiblity/page'


const BCrumb = [
    {
        to: "/",
        title: "Home",
    },
    {
        title: "column visibility Table ",
    },
];
function page() {
    return (
        <>
            <PageContainer title="React column visibility Table" description="this is React column visibility Table page">
                <Breadcrumb title="React column visibility Table" items={BCrumb} />
                <div>
                    <ReactColumnVisibilityTable />
                </div>
            </PageContainer>
        </>
    );
}

export default page;
